# create_admin.py
from app import create_app
from extensions import db, bcrypt
from models import User

# Configure o email e senha do seu admin
ADMIN_EMAIL = "admin@loja.com"
ADMIN_PASSWORD = "admin123" 

app = create_app()

with app.app_context():
    db.create_all()
    # Verifica se o usuário já existe
    existing_user = User.query.filter_by(email=ADMIN_EMAIL).first()
    
    if existing_user:
        print(f"Usuário {ADMIN_EMAIL} já existe.")
    else:
        # Cria o novo usuário
        new_admin = User(email=ADMIN_EMAIL)
        new_admin.set_password(ADMIN_PASSWORD) 
        
        db.session.add(new_admin)
        db.session.commit()
        print(f"Usuário {ADMIN_EMAIL} criado com sucesso!")

    print("Script concluído.")