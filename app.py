# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from extensions import db, login_manager, bcrypt
from admin import init_admin
from flask_ckeditor import CKEditor
import math
import os
import datetime
from flask import send_from_directory
from models import Order
from sqlalchemy import not_
from urllib.parse import quote_plus as url_escape 
from flask_login import login_user, logout_user, current_user

WHATSAPP_NUMBER = '+5515997479931' 

basedir = os.path.abspath(os.path.dirname(__file__))
IS_PRODUCTION = os.environ.get('RENDER')
if IS_PRODUCTION: 
    persistent_data_path = '/var/data' 
    db_path = os.path.join(persistent_data_path, 'oba_afro.db') 
    upload_folder = os.path.join(persistent_data_path, 'uploads') 
else: 
    db_path = os.path.join(basedir, 'oba_afro.db') 
    upload_folder = os.path.join(basedir, 'static', 'uploads')

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte' 
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    app.config['FLASK_ADMIN_EXTRA_CSS'] = ['css/admin_custom.css']

    

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    CKEditor(app)
    init_admin(app) 

    from models import (HeaderCategory, CircularCategory, Banner, Product, 
                        ProductSection, TextSection, Variation,
                        Category,
                        User,
                        FooterLink,
                        Order, SiteStat
                        )
    
    @login_manager.user_loader
    def load_user(user_id):
        """Função que o Flask-Login usa para recarregar o usuário da sessão."""
        return User.query.get(int(user_id))


    @app.route('/admin/order/quick_update', methods=['POST'])
    def quick_update_status():
        """
        Recebe um POST dos botões 'OK' e 'X' do dashboard
        e atualiza o status do pedido.
        """
        # Proteção: só admin logado pode fazer isso
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
            
        try:
            order_id = request.form.get('order_id')
            new_status = request.form.get('new_status') # Será "Concluído" ou "Cancelado"

            if not order_id or not new_status:
                flash('Erro na solicitação: dados ausentes.', 'danger')
                return redirect(url_for('admin.index'))

            order = Order.query.get(order_id)
            if order:
                order.status = new_status
                db.session.commit()
                flash(f'Pedido #{order.id} atualizado para "{new_status}"!', 'success')
            else:
                flash(f'Pedido #{order.id} não encontrado.', 'danger')
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar pedido: {e}', 'danger')

        # Redireciona de volta para o dashboard
        return redirect(url_for('admin.index'))
    
    @app.context_processor
    def inject_global_data():
        header_categories = HeaderCategory.query.order_by(HeaderCategory.order).all()
        
        cart = session.get('cart', {})
        cart_item_count = sum(cart.values()) 
        
        all_categories = Category.query.order_by(Category.name).all()
        
        return {
            'now': datetime.datetime.now(),
            'header_categories': header_categories,
            'math': math,
            'cart_item_count': cart_item_count,
            'all_categories': all_categories, 
            'current_user': current_user
        }
    def get_stat(key):
        """Busca ou cria uma estatística e retorna o objeto."""
        stat = SiteStat.query.filter_by(key=key).first()
        if not stat:
            stat = SiteStat(key=key, value=0)
            db.session.add(stat)
            # Tenta salvar imediatamente
            try:
                db.session.commit()
            except:
                db.session.rollback()
                stat = SiteStat.query.filter_by(key=key).first()
        return stat
    
    # --- Rotas da Loja ---

    @app.route('/')
    def index():
        try:
            stat = get_stat('total_visitas')
            stat.value += 1
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao contar visita: {e}")
        circular_categories_1 = CircularCategory.query.filter_by(section=1).order_by(CircularCategory.order).all()
        banners = Banner.query.order_by(Banner.order).all()
        product_sections = ProductSection.query.all()
        circular_categories_2 = CircularCategory.query.filter_by(section=2).order_by(CircularCategory.order).all()
        about_section = TextSection.query.filter_by(key='sobre-nos').first()
        return render_template(
            'index.html',
            circular_categories_1=circular_categories_1,
            banners=banners,
            product_sections=product_sections,
            circular_categories_2=circular_categories_2,
            about_section=about_section
        )

    @app.route('/produtos')
    def produtos():
        produtos_list = Product.query.filter_by(active=True).all()
        return render_template('produtos.html', produtos=produtos_list)

    @app.route('/categoria/<slug>')
    def categoria_produtos(slug):
        category = Category.query.filter_by(slug=slug).first_or_404()
        produtos_list = [product for product in category.products if product.active]
        return render_template(
            'categoria_produtos.html', 
            produtos=produtos_list,
            category=category
        )

    @app.route('/produto/<slug>')
    def produto_detalhe(slug):
        produto = Product.query.filter_by(slug=slug, active=True).first_or_404()
        
        # --- RASTREAMENTO DE VISUALIZAÇÃO DE PRODUTO ---
        try:
            produto.view_count += 1
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao contar view do produto: {e}")
        # --- FIM DO RASTREAMENTO ---

        return render_template(
            'produto_detalhe.html', 
            produto=produto
        )

    @app.route('/carrinho')
    def carrinho():
        cart_session = session.get('cart', {})
        cart_items = []
        total_price = 0
        
        # Não vamos mais gerar a URL do zap aqui.
        # Vamos gerar apenas o texto.
        whatsapp_message_lines = ["Olá! Gostaria de fazer o seguinte pedido:\n"]
        
        for var_id_str, quantity in cart_session.items():
            # ... (código para calcular cart_items e total_price) ...
            variation = Variation.query.get(var_id_str)
            if variation:
                product = variation.product
                subtotal = product.current_price * quantity
                total_price += subtotal
                
                cart_items.append({
                    'product': product,
                    'variation': variation,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                # Adiciona ao texto da mensagem
                whatsapp_message_lines.append(
                    f"- {quantity}x {product.name} (Tamanho: {variation.size}) - R$ {subtotal:.2f}"
                )

        whatsapp_message_lines.append(f"\n*Total: R$ {total_price:.2f}*")
        
        # Salva o texto da mensagem na sessão para a próxima rota usar
        session['whatsapp_message'] = "\n".join(whatsapp_message_lines)
        
        return render_template(
            'carrinho.html', 
            cart_items=cart_items, 
            total_price=total_price
            # Removemos o whatsapp_url daqui
        )
        return render_template(
            'carrinho.html', 
            cart_items=cart_items, 
            total_price=total_price,
            whatsapp_url=whatsapp_url
        )
    
    @app.route('/checkout/criar-pedido', methods=['POST'])
    def criar_pedido():
        """
        Esta rota é chamada quando o usuário clica em "Finalizar Pedido".
        Ela cria o "Lead" (Pedido) no banco antes de redirecionar ao WhatsApp.
        """
        cart_session = session.get('cart', {})
        whatsapp_message = session.get('whatsapp_message', 'Erro: Carrinho vazio.')
        
        if not cart_session:
            flash('Seu carrinho está vazio.', 'warning')
            return redirect(url_for('carrinho'))

        # Recalcula o preço total para segurança
        total_price = 0
        items_summary_list = []
        for var_id_str, quantity in cart_session.items():
            variation = Variation.query.get(var_id_str)
            if variation:
                total_price += variation.product.current_price * quantity
                items_summary_list.append(f"{quantity}x {variation.product.name} ({variation.size})")

        items_summary_text = ", ".join(items_summary_list)
        whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={url_escape(whatsapp_message)}"
        
        # 1. Cria o Pedido (Lead) no banco de dados
        novo_pedido = Order(
            total_price=total_price,
            items_summary=items_summary_text,
            whatsapp_url=whatsapp_url
        )
        db.session.add(novo_pedido)
        
        # 2. Incrementa a estatística de "checkout"
        stat = get_stat('total_checkouts_whatsapp')
        stat.value += 1
        
        db.session.commit()
        
        # 3. Limpa o carrinho
        session.pop('cart', None)
        session.pop('whatsapp_message', None)
        session.modified = True
        
        # 4. Redireciona o usuário para o WhatsApp
        flash('Seu pedido foi registrado! Estamos te redirecionando para o WhatsApp.', 'success')
        return redirect(whatsapp_url)
    
    @app.route('/carrinho/adicionar/<int:produto_id>', methods=['POST'])
    def adicionar_carrinho(produto_id):
        if 'cart' not in session:
            session['cart'] = {}
        
        variation_id = request.form.get('variation_id')
        produto = Product.query.get_or_404(produto_id) # <-- Já busca o produto

        if not variation_id:
             flash('Por favor, selecione um tamanho.', 'danger')
             return redirect(url_for('produto_detalhe', slug=produto.slug))
        
        # ... (try/except para quantity) ...
        quantity = 1 # (seu código de quantity)

        variacao = Variation.query.get(variation_id)
        if not variacao or variacao.product_id != produto.id:
            flash('Variação inválida.', 'danger')
            return redirect(url_for('produto_detalhe', slug=produto.slug))

        var_id_str = str(variation_id)
        current_in_cart = session['cart'].get(var_id_str, 0)
        total_wanted = current_in_cart + quantity

        if total_wanted > variacao.stock:
            flash(f'Desculpe, temos apenas {variacao.stock} unidades de {produto.name} ({variacao.size}) em estoque.', 'danger')
        else:
            session['cart'][var_id_str] = total_wanted
            session.modified = True 
            
            # --- ADICIONADO: Rastreamento de Adição ao Carrinho ---
            try:
                produto.cart_add_count += 1
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao salvar contagem de carrinho: {e}")
            # --- FIM DA ADIÇÃO ---
            
            flash(f'{quantity}x {produto.name} ({variacao.size}) adicionado ao carrinho!', 'success')
            
        return redirect(url_for('carrinho'))

    @app.route('/carrinho/atualizar', methods=['POST'])
    def atualizar_carrinho():
        if 'cart' not in session:
            return redirect(url_for('carrinho'))
        for var_id_str, new_quantity_str in request.form.items():
            if var_id_str in session['cart']:
                try:
                    new_quantity = int(new_quantity_str)
                    if new_quantity < 1: 
                        session['cart'].pop(var_id_str, None)
                        continue
                    variation = Variation.query.get(var_id_str)
                    if new_quantity > variation.stock:
                        flash(f'Estoque máximo para {variation.product.name} ({variation.size}) é {variation.stock}.', 'warning')
                        session['cart'][var_id_str] = variation.stock
                    else:
                        session['cart'][var_id_str] = new_quantity
                except (ValueError, TypeError):
                    pass 
        session.modified = True
        return redirect(url_for('carrinho'))

    @app.route('/carrinho/remover/<int:variation_id>')
    def remover_do_carrinho(variation_id):
        var_id_str = str(variation_id)
        if 'cart' in session and var_id_str in session['cart']:
            session['cart'].pop(var_id_str, None)
            session.modified = True
            flash('Item removido do carrinho.', 'success')
        return redirect(url_for('carrinho'))

    # --- Rotas de Autenticação (Login/Logout) ---

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Se o usuário já estiver logado, redireciona para o admin
        if current_user.is_authenticated:
            return redirect(url_for('admin.index'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            senha = request.form.get('senha')
                
            # Busca o usuário pelo email
            user = User.query.filter_by(email=email).first()
                
            # Verifica se o usuário existe e se a senha está correta
            if user and user.check_password(senha):
                login_user(user) # <-- Função do Flask-Login que cria a sessão
                    
                # Redireciona para a página 'next' se ela existir (ex: /admin)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('admin.index'))
            else:
                flash('Email ou senha inválidos. Tente novamente.', 'danger')
                    
        return render_template('login.html') # <-- Renderiza seu login.html

    @app.route('/logout')
    def logout():
        logout_user() # <-- Função do Flask-Login que limpa a sessão
        flash('Você saiu da sua conta.', 'success')
        return redirect(url_for('login'))
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename): 
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # --- Fim da Função create_app ---
    return app

# --- Bloco de Execução Principal ---
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
