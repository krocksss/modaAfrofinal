```markdown
# Obá Moda Afro - Loja Virtual Flask

Sistema completo de e-commerce desenvolvido com o framework Flask em Python para a marca Obá Moda Afro. Possui uma interface pública moderna para clientes e um painel administrativo robusto (Flask-Admin) para gerenciamento da loja.

---

## 📑 Índice

1.  [Visão Geral](#-visão-geral)
2.  [Estrutura do Projeto](#-estrutura-do-projeto)
3.  [Tecnologias Utilizadas](#-tecnologias-utilizadas)
4.  [Instalação e Execução](#-instalação-e-execução)
5.  [Arquitetura do Sistema](#-arquitetura-do-sistema)
6.  [Explicação do Código](#-explicação-do-código)
    * [models.py - Modelos de Dados](#1-modelspy---modelos-de-dados)
    * [app.py - Aplicação Principal](#2-apppy---aplicação-principal)
    * [admin.py - Painel Administrativo](#3-adminpy---painel-administrativo)
    * [Templates (Jinja2)](#4-templates-jinja2)
    * [CSS & JavaScript](#5-css--javascript)
7.  [Conceitos Aplicados](#-conceitos-aplicados)
8.  [Observações (Desenvolvimento)](#-observações-desenvolvimento)

---

## 🎯 Visão Geral

Este projeto é uma loja virtual completa que demonstra conceitos de desenvolvimento web aplicados a um e-commerce real:

### 🛍️ **Área Pública (E-commerce)**

* Design moderno e responsivo (Bootstrap 5).
* Página inicial com Banners (Carrossel), Categorias Circulares e Seções de Produtos customizáveis via admin.
* Navegação por Categorias de Produto (`/categoria/<slug>`).
* Página de detalhes do produto (`/produto/<slug>`) com descrição rica (CKEditor), seleção de Variações (tamanho) e exibição da categoria principal.
* Carrinho de compras funcional utilizando a sessão do Flask.
* Finalização de pedido simplificada via link direto para o WhatsApp com a mensagem pré-formatada.

### 🔧 **Área Administrativa (Dashboard - Flask-Admin)**

* Interface administrativa gerada automaticamente pelo Flask-Admin (`/admin`).
* Gerenciamento completo (CRUD) de **Produtos**:
    * Associação a múltiplas **Categorias** (Relacionamento Muitos-para-Muitos).
    * Gerenciamento de **Variações** (tamanho e estoque) diretamente na página do produto (inline).
    * Upload de imagens com preview.
    * Geração automática e edição manual de **slug** (URL amigável).
    * Ação para **duplicar** produtos selecionados.
* Gerenciamento completo (CRUD) de **Categorias de Produto**:
    * Geração automática de **slug**.
    * Associação de produtos diretamente pela página da categoria.
    * Prevenção de exclusão se a categoria contiver produtos.
* Gerenciamento de outros conteúdos do site: Banners, Categorias Circulares, Seções de Texto (com CKEditor), Links do Cabeçalho estático, Seções de Produtos da Home.

---

## 📂 Estrutura do Projeto

```

oba-moda-afro/
│
├── app.py              \# ❤️ Aplicação principal Flask, rotas públicas, lógica do carrinho
├── models.py           \# 💾 Modelos do banco de dados (SQLAlchemy)
├── admin.py            \# ⚙️ Configuração do painel Flask-Admin (views, customizações)
├── extensions.py       \# (Provavelmente) Inicialização de extensões Flask (db, etc.)
├── requirements.txt    \# 📦 Dependências Python do projeto
├── oba\_afro.db         \# 🗄️ Banco de dados SQLite (criado na execução)
│
├── static/             \# 🎨 Arquivos estáticos
│   ├── css/
│   │   └── style.css   \# Estilos CSS personalizados (baseado em Bootstrap)
│   └── uploads/        \# 🖼️ Pasta para imagens de produtos, banners, etc.
│
└── templates/          \# 📄 Templates HTML (Jinja2)
├── base.html       \# Template base (header, footer, mensagens flash)
├── index.html      \# Página inicial
├── produtos.html   \# Página com todos os produtos
├── categoria\_produtos.html \# Página de produtos por categoria
├── produto\_detalhe.html  \# Página de detalhes do produto
├── carrinho.html   \# Página do carrinho de compras
└── ...             \# Outros templates parciais (se houver)

````

---

## 🛠️ Tecnologias Utilizadas

### Backend

* **Python 3.x**
* [cite_start]**Flask 3.0.0** - Microframework web principal [cite: 116]
* [cite_start]**Flask-SQLAlchemy 3.1.1** - ORM para interação com banco de dados [cite: 116]
* [cite_start]**Werkzeug 3.0.1** - Utilitários WSGI (uploads seguros, etc.) [cite: 116]
* **Flask-Admin** - Geração automática de interface administrativa CRUD.
* **Flask-CKEditor** - Integração do editor de texto rico CKEditor.
* **python-slugify** - Geração de URLs amigáveis (slugs).
* **SQLite** - Banco de dados relacional em arquivo (padrão).

### Frontend

* **HTML5** - Estrutura das páginas.
* **CSS3** - Estilização (com personalizações sobre **Bootstrap 5**).
* **JavaScript (ES6+)** - Interatividade no frontend (ex: seleção de variação, atualização de estoque).

### Conceitos

* **MVC/MTV Pattern (Adaptado)** - Separação de responsabilidades (Modelos, Views/Templates, Controller/Rotas).
* **ORM (Object-Relational Mapping)** - Mapeamento de classes Python para tabelas do banco.
* **Relacionamentos Muitos-para-Muitos** - Implementado entre Produtos e Categorias.
* **Session Management** - Gerenciamento do carrinho de compras na sessão do usuário.
* **RESTful Routes (Parcial)** - Padrão de URLs para recursos (produtos, categorias).
* **File Upload Seguro** - Utilização de `secure_filename` e armazenamento organizado.
* **Slugification** - Criação automática de URLs amigáveis.
* **Template Inheritance (Jinja2)** - Reutilização de código HTML (`base.html`).
* **Flash Messages** - Exibição de mensagens de feedback para o usuário.

---

## 🚀 Instalação e Execução

### Pré-requisitos

* Python 3.7 ou superior.
* pip (gerenciador de pacotes Python).

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/LandLandeiro/oba-moda-afro.git](https://github.com/LandLandeiro/oba-moda-afro.git)
    cd oba-moda-afro
    ```

2.  **(Recomendado) Crie e ative um ambiente virtual:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação:**
    ```bash
    python app.py
    ```
    *O Flask criará o arquivo de banco de dados (`oba_afro.db`) automaticamente na primeira execução.*

5.  **Acesse no navegador:**
    * **Loja:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/) (ou `http://localhost:5000/`)
    * **Admin:** [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)

### Configuração Importante

* **Número do WhatsApp:** Verifique e atualize a constante `WHATSAPP_NUMBER` no topo do arquivo `app.py` com o número correto para receber os pedidos.

---

## 🏗️ Arquitetura do Sistema

### Padrão MVC Adaptado com Flask-Admin

````

┌─────────────────────────────────────────┐
│           USUÁRIO / NAVEGADOR           │
└────┬───────────────────────────────┬────┘
│ (Loja Pública)                │ (Admin)
▼                               ▼
┌──────────────────┐   ┌────────────────────────────┐
│ TEMPLATES (Jinja2) │   │ FLASK-ADMIN (Gera Views Admin) │
│ (Views Públicas) │   └─────────────┬──────────────┘
└────────┬─────────┘                 │
│                           │
▼                           ▼
┌─────────────────────────────────────────┐
│              APP.PY (Controller)        │
│    (Rotas Públicas, Lógica do Carrinho) │
└──────────────────┬──────────────────────┘
│
▼
┌─────────────────────────────────────────┐
│       MODELS.PY (Model - Dados)         │
│  (Product, Category, Variation, etc.)   │
│  (+ Lógica de Negócio em Propriedades)  │
└──────────────────┬──────────────────────┘
│
▼
┌─────────────────────────────────────────┐
│         OBA\_AFRO.DB (SQLite)            │
└─────────────────────────────────────────┘

````
* **Fluxo Admin:** O Flask-Admin interage diretamente com os `models.py` para gerar as páginas CRUD, passando pelo `admin.py` para customizações.
* **Fluxo Público:** O `app.py` define as rotas, busca dados nos `models.py` (via SQLAlchemy) e renderiza os `templates/`.

---

## 💻 Explicação do Código

### 1. `models.py` - Modelos de Dados

Define a estrutura do banco de dados usando SQLAlchemy ORM.

**Relacionamento Muitos-para-Muitos (Produtos e Categorias):**

```python
# Tabela de associação que liga produtos a categorias
product_category_association = db.Table('product_category_association',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Category(db.Model):
    # ... outros campos ...
    # Define a relação M2M a partir da Categoria
    products = relationship('Product',
                            secondary=product_category_association,
                            back_populates='categories')

class Product(db.Model):
    # ... outros campos ...
    # Define a relação M2M a partir do Produto
    categories = relationship('Category',
                              secondary=product_category_association,
                              back_populates='products')
````

  * `db.Table`: Cria a tabela intermediária essencial para a relação M2M.
  * `relationship(secondary=...)`: Configura o SQLAlchemy para usar a tabela de associação.
  * `back_populates`: Garante que a relação funcione nos dois sentidos (`produto.categories` e `categoria.products`).

**Variações (Relacionamento Um-para-Muitos):**

```python
class Product(db.Model):
    # ...
    # Um produto tem muitas variações
    variations = relationship('Variation', backref='product', lazy=True, cascade='all, delete-orphan')

class Variation(db.Model):
    # ...
    # Uma variação pertence a um produto
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
```

  * `relationship('Variation', ...)`: Define que `product.variations` será uma lista de objetos `Variation`.
  * `backref='product'`: Permite acessar o produto a partir da variação (`variation.product`).
  * `cascade='all, delete-orphan'`: Garante que ao deletar um produto, suas variações também sejam deletadas.
  * `db.ForeignKey('product.id')`: Chave estrangeira que liga a Variação ao Produto.

### 2\. `app.py` - Aplicação Principal

Contém a configuração do Flask, rotas públicas e lógica do carrinho.

**Context Processor (Dados Globais):**

```python
@app.context_processor
def inject_global_data():
    # ... busca header_categories ...
    cart = session.get('cart', {})
    cart_item_count = sum(cart.values())
    all_categories = Category.query.order_by(Category.name).all()
    
    return {
        # ... outros dados ...
        'cart_item_count': cart_item_count, # Para o header
        'all_categories': all_categories    # Para o menu (se usado)
    }
```

  * Disponibiliza variáveis (como contador do carrinho e lista de categorias) para *todos* os templates.

**Rota de Categoria:**

```python
@app.route('/categoria/<slug>')
def categoria_produtos(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    # Filtra produtos ativos DENTRO da lista da categoria (M2M)
    produtos_list = [product for product in category.products if product.active]
    return render_template('categoria_produtos.html', 
                           produtos=produtos_list, category=category)
```

  * Busca a categoria pelo `slug` na URL.
  * Filtra os produtos associados para mostrar apenas os ativos.

**Lógica do Carrinho (Sessão):**

```python
# Adicionar ao Carrinho
@app.route('/carrinho/adicionar/<int:produto_id>', methods=['POST'])
def adicionar_carrinho(produto_id):
    # ... validações ...
    var_id_str = str(variation_id)
    if 'cart' not in session:
        session['cart'] = {}
    
    current_in_cart = session['cart'].get(var_id_str, 0)
    # ... checa estoque ...
    
    session['cart'][var_id_str] = total_wanted
    session.modified = True # Força o Flask a salvar a sessão modificada
    # ... flash message e redirect ...

# Visualizar Carrinho
@app.route('/carrinho')
def carrinho():
    cart_session = session.get('cart', {})
    cart_items = []
    total_price = 0
    for var_id_str, quantity in cart_session.items():
        variation = Variation.query.get(var_id_str)
        # ... busca produto, calcula subtotal ...
        cart_items.append({ 'product': product, 'variation': variation, ... })
    # ... monta mensagem WhatsApp ...
    return render_template('carrinho.html', cart_items=cart_items, ...)
```

  * `session`: Dicionário do Flask que armazena dados no cookie do navegador (criptografado). Usado para guardar `{ variation_id: quantity }`.
  * `session.modified = True`: Essencial após modificar dicionários ou listas dentro da `session` para garantir que as alterações sejam salvas.

### 3\. `admin.py` - Painel Administrativo

Configura como os modelos (`models.py`) são exibidos e editados no Flask-Admin.

**Slug Automático e Editável (Produto):**

```python
class ProductView(SecureModelView):
    # ...
    form_columns = ('name', 'categories', ..., 'slug', ...) # Slug no formulário
    form_args = { 'slug': { 'description': 'Deixe em branco...' } }

    def on_model_change(self, form, model, is_created):
        if form.slug.data: # Usa o slug digitado
            model.slug = slugify(form.slug.data)
        else: # Gera do nome
            model.slug = slugify(model.name)
        # ... verifica unicidade ...
        super().on_model_change(form, model, is_created)
```

  * O campo `slug` é incluído no formulário.
  * `on_model_change` verifica se o campo foi preenchido; se não, gera automaticamente. A unicidade é sempre verificada.

**Variações Inline:**

```python
class ProductView(SecureModelView):
    # ...
    inline_models = [(Variation, {
        'form_label': 'Variação',
        'form_columns': ['id', 'size', 'stock'], # Inclui 'id' oculto
        'min_entries': 1,
    })]
```

  * Permite editar as Variações diretamente na página de Edição do Produto.

**Ação de Duplicar:**

```python
from flask_admin.actions import action

class ProductView(SecureModelView):
    # ...
    @action('duplicate', 'Duplicar', 'Confirmar duplicação?')
    def action_duplicate(self, ids):
        try:
            for product in self.model.query.filter(self.model.id.in_(ids)).all():
                # ... cria new_product com nome e slug modificados ...
                # ... copia relações M2M (categories, sections) ...
                # ... copia relações 1-M (variations) ...
                self.session.add(new_product)
            self.session.commit()
            flash('Produtos duplicados.', 'success')
        except Exception as ex:
            # ... tratamento de erro ...
```

  * Adiciona a opção "Duplicar" ao menu de Ações na lista de produtos.
  * Cria cópias profundas, incluindo relacionamentos.

### 4\. Templates (Jinja2)

Utilizam o motor de templates Jinja2.

**Herança (`base.html`):**

```html
<!DOCTYPE html>
<html> <head> ... {% block title %}{% endblock %} ... </head>
<body>
    <header>...</header>
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>...</footer>
</body>
</html>

{% extends 'base.html' %}
{% block title %}{{ produto.name }}{% endblock %}
{% block content %}
    {% endblock %}
```

  * `{% extends %}`: Define que o template filho herda do `base.html`.
  * `{% block %}`: Define seções que podem ser sobrescritas pelo template filho.

**Exibindo Dados:**

```html
<h1>{{ produto.name }}</h1>
<p>R$ {{ "%.2f"|format(produto.price) }}</p>
<a href="{{ url_for('categoria_produtos', slug=produto.categories[0].slug) }}">
    {{ produto.categories[0].name }}
</a>
<div>{{ produto.description | safe }}</div>
```

  * `{{ variable }}`: Exibe o valor de uma variável Python.
  * `|format(...)`, `|safe`: Filtros Jinja para formatar ou tratar a saída.
  * `url_for('nome_da_rota', parametro=valor)`: Gera URLs de forma segura e dinâmica.

### 5\. CSS & JavaScript

  * **CSS (`static/css/style.css`):** Baseado em Bootstrap 5, com personalizações de cores (`:root` variáveis), fontes e estilos específicos para componentes como `.product-card`, `.section-circular-categories`, `.footer-oba`, etc.
  * **JavaScript:** Usado principalmente para interatividade no frontend:
      * Atualizar o campo `max` da quantidade e habilitar/desabilitar botões na página de produto com base no estoque da variação selecionada.
      * (Possivelmente) Controlar carrosséis, modals, etc., via Bootstrap JS.

-----

## 🎓 Conceitos Aplicados

  * **ORM (Object-Relational Mapping):** Flask-SQLAlchemy mapeia classes Python (`models.py`) para tabelas de banco de dados, simplificando consultas e manipulações.
  * **Relacionamentos:** O projeto utiliza relacionamentos Um-para-Muitos (Produto -\> Variações) e Muitos-para-Muitos (Produto \<-\> Categorias) gerenciados pelo SQLAlchemy.
  * **Session Management:** O carrinho de compras é armazenado na `session` do Flask, que utiliza cookies seguros para persistir dados entre requisições do mesmo usuário.
  * **Slugification:** Geração automática de URLs amigáveis (`meu-produto-incrivel`) a partir de nomes ("Meu Produto Incrível") usando `python-slugify`, crucial para SEO e URLs legíveis.
  * **Template Inheritance:** O uso de `base.html` e `{% block %}` permite reutilizar a estrutura comum (header, footer) em todas as páginas.
  * **Flask-Admin:** Framework poderoso que auto-gera interfaces CRUD baseadas nos modelos SQLAlchemy, com extensas opções de customização (`admin.py`).
  * **File Uploads:** Processamento e armazenamento seguro de imagens enviadas pelo usuário, incluindo sanitização de nomes de arquivo (`secure_filename`).
  * **Flash Messages:** Sistema do Flask para exibir mensagens temporárias de feedback ao usuário (ex: "Produto adicionado ao carrinho\!").

-----

## 📝 Observações (Desenvolvimento)

  * **Alterações no `models.py`:** Qualquer modificação na estrutura das tabelas (campos, relacionamentos) em `models.py` **exige** que o arquivo de banco de dados (`oba_afro.db`) seja **deletado** antes da próxima execução (`python app.py`). O Flask recriará o banco com a nova estrutura, mas **todos os dados anteriores serão perdidos**. Para ambientes de produção ou para preservar dados durante o desenvolvimento, utilize uma ferramenta de migração como `Flask-Migrate`.
  * **Chave Secreta:** A `app.config['SECRET_KEY']` em `app.py` deve ser alterada para um valor longo, aleatório e secreto em um ambiente de produção.
  * **Debug Mode:** Não execute a aplicação com `debug=True` em produção.

-----

## Autor

  * Lucca Landeiro ([@LandLandeiro](https://www.google.com/search?q=https://github.com/LandLandeiro))

<!-- end list -->

```
```

#   m o d a A f r o f i n a l  
 