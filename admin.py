# admin.py
import os
from datetime import datetime, timedelta
from sqlalchemy import func
from flask_admin import Admin, AdminIndexView, expose 
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditorField
from flask_admin.form.upload import ImageUploadField
from flask_admin.menu import MenuLink
from wtforms.validators import ValidationError
from flask import flash, redirect, url_for, request, render_template
from flask_login import current_user, logout_user 
from slugify import slugify
from wtforms.fields import DateField

from flask_admin.actions import action
from slugify import slugify

from extensions import db
from models import (
    HeaderCategory, CircularCategory, Banner,
    Product, ProductSection, TextSection,
    Variation, Category,
    FooterLink,
    Product, Promotion,
    Order, SiteStat
)

# --- Configuração do Caminho de Upload ---
basedir = os.path.abspath(os.path.dirname(__file__))
upload_path = os.path.join(basedir, 'static', 'uploads')


# --- Views de Admin Personalizadas ---

class SecureModelView(ModelView):
    
    def is_accessible(self):
        # Retorna True se o usuário estiver logado
        return current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))

class SecureAdminIndexView(AdminIndexView):
    """
    Protege a página inicial do painel admin e exibe o dashboard com filtros.
    """
    
    def __init__(self, template=None, url=None, **kwargs):
        super(SecureAdminIndexView, self).__init__(
            template=template or 'admin/index.html', # Nosso template de dashboard
            url=url or '/admin',
            **kwargs
        )

    def is_accessible(self):
        return current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))

    @expose('/')
    def index(self, **kwargs):
        """
        Carrega a página de dashboard com os dados para os gráficos,
        processando os filtros de data.
        """
        
        # --- 1. ESTA É A CORREÇÃO CRÍTICA ---
        # Carrega os args padrão do admin (incluindo 'admin_base_template')
        template_args = self._template_args.copy()
        
        # --- 2. PROCESSAR FILTROS DE DATA ---
        try:
            start_date_str = request.args.get('start_date')
            end_date_str = request.args.get('end_date')

            if not end_date_str:
                end_date = datetime.now()
                end_date_str = end_date.strftime('%Y-%m-%d')
            else:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)

            if not start_date_str:
                start_date = end_date - timedelta(days=30)
                start_date_str = start_date.strftime('%Y-%m-%d')
            else:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

            recent_pending_orders = Order.query.filter_by(status='Pendente')\
                                                .order_by(Order.created_at.desc())\
                                                .limit(10).all()
        
        except ValueError:
            flash('Formato de data inválido. Usando o padrão (últimos 30 dias).', 'warning')
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            end_date_str = end_date.strftime('%Y-%m-%d')
            start_date_str = start_date.strftime('%Y-%m-%d')

        
        # --- 3. QUERIES (DENTRO DE UM 'TRY' CORRIGIDO) ---
        try:
            # Cria uma consulta base de pedidos dentro do período
            base_query_pedidos = Order.query.filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
            
            total_leads = base_query_pedidos.count()

            vendas_concluidas_query = base_query_pedidos.filter(Order.status == 'Concluído')
            total_vendas_concluidas = vendas_concluidas_query.count()

            receita_total_raw = db.session.query(func.sum(Order.total_price))\
                                  .filter(Order.status == 'Concluído')\
                                  .filter(Order.created_at >= start_date, Order.created_at <= end_date)\
                                  .scalar()
            receita_total = receita_total_raw or 0.0

            taxa_conversao = 0.0
            if total_leads > 0:
                taxa_conversao = (total_vendas_concluidas / total_leads) * 100

            # 4. DADOS PARA GRÁFICOS
            status_data = db.session.query(Order.status, func.count(Order.id))\
                              .filter(Order.created_at >= start_date, Order.created_at <= end_date)\
                              .group_by(Order.status).all()
            dados_status_pizza = {
                'labels': [s[0] for s in status_data],
                'data': [s[1] for s in status_data]
            }

            receita_por_dia_raw = db.session.query(
                                    func.date(Order.created_at), 
                                    func.sum(Order.total_price)
                                 ).filter(
                                    Order.status == 'Concluído',
                                    Order.created_at >= start_date,
                                    Order.created_at <= end_date
                                 ).group_by(
                                    func.date(Order.created_at)
                                 ).order_by(
                                    func.date(Order.created_at)
                                 ).all()
            
            dados_receita_linha = {
                'labels': [datetime.strptime(d[0], '%Y-%m-%d').strftime('%d/%m') for d in receita_por_dia_raw],
                'data': [float(d[1]) for d in receita_por_dia_raw]
            }
            
            top_produtos = Product.query.filter(Product.cart_add_count > 0)\
                                  .order_by(Product.cart_add_count.desc())\
                                  .limit(5).all()
            dados_produtos_carrinho = {
                'labels': [p.name for p in top_produtos],
                'data': [p.cart_add_count for p in top_produtos]
            }

            # 5. ENVIAR DADOS PARA O TEMPLATE
            template_args.update({
                'start_date_str': start_date_str,
                'end_date_str': end_date_str,
                'receita_total': receita_total,
                'total_leads': total_leads,
                'total_vendas_concluidas': total_vendas_concluidas,
                'taxa_conversao': taxa_conversao,
                'dados_status_pizza': dados_status_pizza,
                'dados_receita_linha': dados_receita_linha,
                'dados_produtos_carrinho': dados_produtos_carrinho,
                'recent_pending_orders': recent_pending_orders,
                'recent_pending_orders': []
            })

        # --- 6. 'EXCEPT' CORRIGIDO E PAREADO ---
        except Exception as e:
            flash(f'Erro ao carregar o dashboard: {e}', 'danger')
            template_args.update({
                'start_date_str': start_date_str, 'end_date_str': end_date_str,
                'receita_total': 0, 'total_leads': 0,
                'total_vendas_concluidas': 0, 'taxa_conversao': 0,
                'dados_status_pizza': {'labels': [], 'data': []},
                'dados_receita_linha': {'labels': [], 'data': []},
                'dados_produtos_carrinho': {'labels': [], 'data': []}
            })
        
        # --- 7. RENDERIZAR NO FINAL ---
        return self.render(
            self._template,
            **template_args
        )
class HeaderCategoryView(SecureModelView):
    form_columns = ('name', 'category', 'order')
    column_list = ('name', 'category', 'order')
    column_default_sort = ('order', False)

    form_args = {
        'category': {
            'label': 'Link da Categoria',
            'description': 'Selecione a categoria de produto para a qual este link deve apontar.'
        }
    }   

class CategoryView(SecureModelView):
    form_columns = ('name', 'description', 'products')
    column_list = ('name', 'slug', 'products')
    
    form_args = {
         'products': {
            'label': 'Produtos nesta Categoria'
         }
    }

    def on_model_change(self, form, model, is_created):
        model.slug = slugify(model.name)
        check_slug = Category.query.filter_by(slug=model.slug).first()
        if check_slug and check_slug.id != model.id:
            model.slug = f"{model.slug}-{model.id or 'novo'}"
            flash(f'O slug foi alterado para "{model.slug}" pois o original já existia.', 'warning')
        super().on_model_change(form, model, is_created)

    def on_model_delete(self, model):
        if model.products:
            flash(f'Não é possível excluir a categoria "{model.name}", pois ela contém produtos. Mova os produtos para outra categoria primeiro.', 'error')
            raise ValidationError("Categoria não está vazia.")
        super().on_model_delete(model)
    


class ProductView(SecureModelView):
    form_overrides = {
        'image': ImageUploadField,
        'description': CKEditorField
    }
    
    form_args = {
        'image': {
            'label': 'Imagem do Produto',
            'base_path': upload_path,
            'url_relative_path': 'uploads/',
            'namegen': lambda obj, file_data: f'product_{file_data.filename}',
            'allowed_extensions': ('jpg', 'jpeg', 'png', 'gif', 'webp'),
        },
        'description': {
            'label': 'Descrição Completa'
        },
        'slug': {
            'label': 'URL (slug)',
            'description': 'Deixe em branco para gerar automaticamente a partir do nome.' 
        },
        'categories': {
            'label': 'Categorias',
            'description': 'Selecione uma ou mais categorias para o produto.'
        },
        
        'price': {
            'label': 'Preço Normal (Cheio)'
        }
    }
    
    column_list = ('name', 'categories', 'price',  'image', 'active', 'total_stock', 'view_count', 'cart_add_count', 'slug')
    form_columns = ('name', 'categories', 'description', 'price',  'image', 'active', 'slug', 'sections')
    
    column_searchable_list = ('name',) 
    column_filters = ('categories', 'sections', 'active')

    inline_models = [(Variation, {
        'form_label': 'Variação',
        'form_columns': ['id', 'size', 'stock'],
        'min_entries': 1,
    })]

    def on_model_change(self, form, model, is_created):
        if form.slug.data:
            model.slug = slugify(form.slug.data)
        else:
            model.slug = slugify(model.name)
        query = self.model.query.filter_by(slug=model.slug)
        if model.id:
            query = query.filter(self.model.id != model.id)
        check_slug = query.first()
        if check_slug:
            unique_suffix = model.id or 'novo' 
            model.slug = f"{model.slug}-{unique_suffix}"
            flash(f'O slug foi alterado para "{model.slug}" pois o original já existia.', 'warning')
        super().on_model_change(form, model, is_created)

    @action('duplicate', 'Duplicar', 'Tem certeza que deseja duplicar os produtos selecionados?')
    def action_duplicate(self, ids):
        try:
            product_query = self.model.query.filter(self.model.id.in_(ids))
            
            for product in product_query.all():
                new_name = f"{product.name} (Cópia)"
                new_slug = slugify(new_name)
                
                check_slug = self.model.query.filter_by(slug=new_slug).first()
                if check_slug:
                    new_slug = f"{new_slug}-{product.id}"

                new_product = self.model(
                    name=new_name,
                    slug=new_slug,
                    description=product.description,
                    price=product.price,
                    image=product.image,
                    active=False 
                )
                new_product.categories = list(product.categories)
                new_product.sections = list(product.sections)
                new_vars = []
                for var in product.variations:
                    new_var = Variation(
                        size=var.size,
                        stock=var.stock
                    )
                    new_vars.append(new_var)
                
                new_product.variations = new_vars
                self.session.add(new_product)
            
            self.session.commit()
            flash(f"{len(ids)} produto(s) duplicado(s) com sucesso. Lembre-se de ativá-los após a edição.", 'success')
        
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(f"Falha ao duplicar produtos: {ex}", 'error')

class PromotionView(SecureModelView):
    # Colunas que você vê na lista
    column_list = ('name', 'is_active', 'start_date', 'end_date', 'discount_percent', 'products')
    
    # Campos que você preenche no formulário
    form_columns = ('name', 'is_active', 'start_date', 'end_date', 'discount_percent', 'products')
    
    # Isso faz os campos de data usarem um seletor de calendário
    form_overrides = {
        'start_date': DateField,
        'end_date': DateField
    }
    
    form_args = {
        'name': {'label': 'Nome da Campanha (Ex: Black Friday)'},
        'is_active': {'label': 'Ativar esta promoção?'},
        'start_date': {'label': 'Data de Início (Opcional)', 'description': 'Deixe em branco para começar imediatamente.'},
        'end_date': {'label': 'Data de Fim (Opcional)', 'description': 'Deixe em branco para nunca expirar.'},
        'discount_percent': {'label': 'Desconto (%)', 'description': 'Ex: digite 15 para 15% de desconto.'},
        'products': {'label': 'Produtos nesta Promoção', 'description': 'Selecione os produtos que farão parte desta campanha.'}
    }

class BannerView(SecureModelView):
    form_overrides = {
        'image_url_desktop': ImageUploadField,
        'image_url_mobile': ImageUploadField,
    }
    form_args = {
        'image_url_desktop': {
            'label': 'Imagem Desktop (1920x600)',
            'base_path': upload_path,
            'url_relative_path': 'uploads/',
            'namegen': lambda obj, file_data: f'banner_d_{file_data.filename}',
            'allowed_extensions': ('jpg', 'jpeg', 'png', 'gif', 'webp'),
        },
        'image_url_mobile': {
            'label': 'Imagem Mobile (opcional) (600x600)',
            'base_path': upload_path,
            'url_relative_path': 'uploads/',
            'namegen': lambda obj, file_data: f'banner_m_{file_data.filename}',
            'allowed_extensions': ('jpg', 'jpeg', 'png', 'gif', 'webp'),
        },
        'link_url': {
            'label': 'URL Externa (Opcional)',
            'description': 'Preencha este campo APENAS se o banner for para um site externo.'
        },
        'product': {
            'label': 'Link para Produto (Opcional)',
            'description': 'Selecione um produto da loja para o banner linkar diretamente para ele.'
        }
    }
    column_list = ('title', 'image_url_desktop','product', 'link_url', 'order')
    form_columns = ('title', 'subtitle', 'image_url_desktop', 'image_url_mobile', 'link_url', 'product', 'order')
    column_default_sort = ('order', False)

class FooterLinkView(SecureModelView):
    form_columns = ('title', 'url', 'order', 'column')
    column_list = ('title', 'url', 'order', 'column')
    column_default_sort = ('column', False)
    column_filters = ('column',)

class CircularCategoryView(SecureModelView):
    form_overrides = {
        'image_url': ImageUploadField
    }
    form_args = {
        'image_url': {
            'label': 'Imagem (100x100)',
            'base_path': upload_path,
            'url_relative_path': 'uploads/',
            'namegen': lambda obj, file_data: f'cat_{file_data.filename}',
            'allowed_extensions': ('jpg', 'jpeg', 'png', 'gif', 'webp'),
        },
        'category': {
            'label': 'Link da Categoria',
            'description': 'Selecione a categoria de produto para a qual esta bolinha deve apontar.'
        }
    }
    
    column_list = ('name', 'image_url', 'category', 'section', 'order')
    form_columns = ('name', 'image_url', 'category', 'section', 'order')
    column_default_sort = ('order', False)
    column_filters = ('section',) 

class TextSectionView(SecureModelView):
    form_overrides = {
        'content': CKEditorField
    }
    form_columns = ('key', 'title', 'content')
    column_list = ('key', 'title')
    can_create = True
    can_delete = True

class ProductSectionView(SecureModelView):
    column_list = ('title',)
    form_columns = ('title', 'products')
    form_args = dict(
        products=dict(
            label='Produtos nesta seção',
            description='Selecione no máximo 4 produtos.' 
        ),
        title=dict(
            label='Título da Seção (ex: Destaques)'
        )
    )

    def on_model_change(self, form, model, is_created):
        # Esta é a ÚNICA verificação que deve estar aqui
        if hasattr(form, 'products') and form.products.data:
            selected_products_count = len(form.products.data)
            if selected_products_count > 4:
                flash(f'ERRO AO SALVAR: Você selecionou {selected_products_count} produtos. O máximo permitido por seção é 4. Por favor, remova o(s) excedente(s).', 'error')
                raise ValidationError('Limite de 4 produtos por seção excedido.')
        
        # O 'super()' deve ser chamado apenas uma vez, no final.
        super().on_model_change(form, model, is_created)

class OrderView(SecureModelView):
    """Visualização para os Pedidos/Leads"""
    can_create = True # criar pedidos manualmente
    can_edit = True   # Não editar pedidos
    can_delete = True  # Pode apagar pedidos antigos

    form_choices = {
        'status': [
            ('Pendente', 'Pendente'),
            ('Concluído', 'Concluído'),
            ('Cancelado', 'Cancelado')
        ]
    }

    column_editable_list = ['status']
    
    column_list = ('id', 'status','created_at', 'total_price', 'items_summary', 'whatsapp_url')
    column_default_sort = ('created_at', True) # Ordenar por mais novo
    column_searchable_list = ('items_summary',)
    column_filters = ('created_at', 'total_price')

class SiteStatView(SecureModelView):
    """Visualização para as Estatísticas"""
    can_create = False # Não criar novas chaves
    can_delete = False # Não deletar chaves
    
    # Permite editar o valor (ex: para zerar um contador)
    can_edit = True 
    
    column_list = ('key', 'value')


def init_admin(app):
    """Inicializa o Flask-Admin."""
    admin = Admin(
        app, 
        name='Obá Moda Afro - Dashboard', 
        url='/admin',
        index_view=SecureAdminIndexView() # <-- Define a view de index segura
        
    )

    admin.add_view(CategoryView(Category, db.session, name='Categorias',
                   menu_icon_value='fa-bookmark'))
    admin.add_view(ProductView(Product, db.session, name='Produtos',
                   menu_icon_value='fa-tags'))
    admin.add_view(HeaderCategoryView(HeaderCategory, db.session, name='Categorias (Header)',
                   menu_icon_value='fa-list-alt'))
    admin.add_view(CircularCategoryView(CircularCategory, db.session, name='Categorias (Bolinhas)',
                   menu_icon_value='fa-dot-circle-o'))
    admin.add_view(BannerView(Banner, db.session, name='Banners (Carrossel)',
                   menu_icon_value='fa-image'))
    admin.add_view(ProductSectionView(ProductSection, db.session, name='Seções de Produto',
                   menu_icon_value='fa-folder-open'))
    admin.add_view(TextSectionView(TextSection, db.session, name='Seções de Texto',
                   menu_icon_value='fa-file-text-alt'))
    admin.add_view(FooterLinkView(FooterLink, db.session, name='Links (Rodapé)',
                   menu_icon_value='fa-link'))
    admin.add_view(OrderView(Order, db.session, name='Pedidos (Leads)',
                   menu_icon_value='fa-money'))
    admin.add_view(SiteStatView(SiteStat, db.session, name='Estatísticas',
                   menu_icon_value='fa-bar-chart'))
    admin.add_view(PromotionView(Promotion, db.session, name='Promoções (Campanhas)',
                   menu_icon_value='fa-bullhorn'))
    admin.add_link(MenuLink(name='Voltar ao Site', category='', url='/',
                   icon_value='fa-home'))