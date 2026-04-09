"""
extensions.py — Extensões do Flask

Aqui criamos as instâncias das extensões SEM ligá-las ao app ainda.
Isso é necessário para o padrão Application Factory funcionar corretamente.

As extensões são "registradas" no app dentro da função create_app() em __init__.py.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# ORM para banco de dados — permite trabalhar com tabelas como classes Python
db = SQLAlchemy()

# Gerenciamento de login/logout e sessões de usuário
login_manager = LoginManager()

# Migrações do banco de dados — controla alterações nas tabelas ao longo do tempo
migrate = Migrate()

# Proteção CSRF — previne ataques de falsificação de requisição
csrf = CSRFProtect()

# Configura o Flask-Login
# Se o usuário tenta acessar uma página que requer login, redireciona para 'auth.login'
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Você precisa estar logado para acessar esta página.'
login_manager.login_message_category = 'warning'
