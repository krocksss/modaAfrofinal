# models.py
from extensions import db, bcrypt
from sqlalchemy.orm import relationship
from flask_login import UserMixin
import datetime

# --- 1. NOVA TABELA DE ASSOCIAÇÃO (Muitos-para-Muitos) ---
# Esta tabela "liga" produtos a categorias
product_category_association = db.Table('product_category_association',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

promotion_product_association = db.Table('promotion_product_association',
    db.Column('promotion_id', db.Integer, db.ForeignKey('promotion.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

class Promotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True) # Ex: "Black Friday"
    is_active = db.Column(db.Boolean, default=False)
    
    # Datas de início e fim que você pediu
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    
    # Tipo de desconto (Vamos começar com porcentagem)
    discount_percent = db.Column(db.Float, default=0.0)
    
    # Relação M2M: "Quais produtos estão nesta promoção?"
    products = relationship('Product',
                            secondary=promotion_product_association,
                            back_populates='promotions')

    def __str__(self):
        return f"{self.name} ({self.discount_percent}%)"

    @property
    def is_currently_active(self):
        """Verifica se a promoção está ativa E dentro da data"""
        if not self.is_active:
            return False
        
        now = datetime.datetime.now()
        # Se tem data de início e ainda não começou
        if self.start_date and now < self.start_date:
            return False
        # Se tem data de fim e já terminou
        if self.end_date and now > self.end_date:
            return False
            
        return True
    
# --- 2. MODELO DE CATEGORIA ATUALIZADO ---
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relação "muitos-para-muitos"
    products = relationship('Product', 
                            secondary=product_category_association,
                            back_populates='categories')

    def __str__(self):
        return self.name

# Modelos para o Header (sem alterações)
class HeaderCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    order = db.Column(db.Integer, default=0)
    def __str__(self): return self.name
    category = db.relationship('Category', backref='header_links', lazy=True)

    def __str__(self):
        # Mostra o nome da categoria se estiver vinculada
        if self.category:
            return f"{self.name} (Links para: {self.category.name})"
        return self.name
    
# Modelos para as Categorias Circulares (Bolinhas) (sem alterações)
class CircularCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    category = db.relationship('Category', backref='circular_links', lazy=True)
    order = db.Column(db.Integer, default=0)
    section = db.Column(db.Integer, default=1) 
    def __str__(self): return f"{self.name} (Seção {self.section})"

    def __str__(self):
        # Mostra o nome da categoria se estiver vinculada
        if self.category:
            return f"{self.name} (Link: {self.category.name}) (Seção {self.section})"
        return f"{self.name} (Seção {self.section})"

# Modelos para os Banners do Carrossel (sem alterações)
class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url_desktop = db.Column(db.String(200), nullable=False)
    image_url_mobile = db.Column(db.String(200), nullable=True)
    link_url = db.Column(db.String(200), default="#", nullable=True)
    title = db.Column(db.String(150))
    subtitle = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    product = db.relationship('Product', backref='banners', lazy=True)
    def __str__(self): return self.title or f"Banner {self.id}"

# --- 3. MODELO DE PRODUTO ATUALIZADO ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=True)
    slug = db.Column(db.String(150), unique=True, nullable=True)
    active = db.Column(db.Boolean, default=True)
    cart_add_count = db.Column(db.Integer, default=0)

    view_count = db.Column(db.Integer, default=0) 
    
    categories = relationship('Category', ...)
    variations = relationship('Variation', ...)
    promotions = relationship('Promotion',
                              secondary=promotion_product_association,
                              back_populates='products')    
    
    categories = relationship('Category',
                              secondary=product_category_association,
                              back_populates='products')

    
    variations = relationship('Variation', backref='product', lazy=True, cascade='all, delete-orphan')

    @property
    def active_promotion(self):
        """Encontra a primeira promoção ativa para este produto."""
        if not self.promotions:
            return None
        
        for promo in self.promotions:
            if promo.is_currently_active:
                return promo # Retorna a primeira promoção válida
        return None

    @property
    def is_on_sale(self):
        """Retorna True se houver uma promoção ativa."""
        return self.active_promotion is not None

    @property
    def current_price(self):
        """Retorna o preço final (promocional ou cheio)."""
        promo = self.active_promotion
        if promo:
            # Calcula o desconto
            discount_factor = 1.0 - (promo.discount_percent / 100.0)
            return round(self.price * discount_factor, 2)
        
        return self.price
    
    @property
    def total_stock(self):
        if not self.variations:
            return 0
        return sum(var.stock for var in self.variations)

    def __str__(self):
        return self.name

# Novo Modelo para Variações (Tamanho/Estoque) (sem alterações)
class Variation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    def __str__(self):
        return f"{self.product.name} - {self.size} ({self.stock} unid.)"

# Tabela de associação (para seções da Home) (sem alterações)
product_section_association = db.Table('product_section_association',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('section_id', db.Integer, db.ForeignKey('product_section.id'))
)

# Modelo para a Seção de Produtos (ex: "Destaques") (sem alterações)
class ProductSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, default="Destaques")
    products = db.relationship('Product', secondary=product_section_association,
                               backref=db.backref('sections', lazy='dynamic'))
    def __str__(self): return self.title

# Modelo para Seções de Texto Genéricas (ex: "Sobre Nós") (sem alterações)
class TextSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False, default='sobre-nos')
    title = db.Column(db.String(150), nullable=False, default="Sobre Nós")
    content = db.Column(db.Text, nullable=True)
    def __str__(self): return self.title

# Modelo para Links do Footer (sem alterações)
class FooterLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), default="#")
    order = db.Column(db.Integer, default=0)
    column = db.Column(db.Integer, default=1)
    def __str__(self): return f"{self.title} (Coluna {self.column})"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    total_price = db.Column(db.Float, nullable=False)
    
    # Salva os itens do carrinho como um texto simples
    items_summary = db.Column(db.Text, nullable=True) 
    
    # Gera uma URL do WhatsApp para referência
    whatsapp_url = db.Column(db.String(1000), nullable=True)

    status = db.Column(db.String(30), nullable=False, default='Pendente')

    def __str__(self):
        return f"Pedido #{self.id} - R${self.total_price:.2f} ({self.status})"

# --- NOVO MODELO 2: Estatísticas do Site ---
# Um lugar simples para guardar contadores (ex: "total_visitas")
class SiteStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Integer, default=0)

    def __str__(self):
        return f"{self.key}: {self.value}"

# --- 4. MODELO DE USUÁRIO PARA AUTENTICAÇÃO ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        """Cria um hash seguro para a senha."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __str__(self):
        return self.email