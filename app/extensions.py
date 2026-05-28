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
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

# Rate limiting — chave por IP remoto
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],          # sem limite global; cada rota define o seu
    storage_uri='memory://',    # em produção substituir por Redis: 'redis://localhost:6379'
)

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Você precisa estar logado para acessar esta página.'
login_manager.login_message_category = 'warning'
