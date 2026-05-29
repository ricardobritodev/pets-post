"""
extensions.py — Extensões do Flask

Aqui criamos as instâncias das extensões SEM ligá-las ao app ainda.
Isso é necessário para o padrão Application Factory funcionar corretamente.

As extensões são "registradas" no app dentro da função create_app() em __init__.py.
"""

import os

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

# Rate limiting — chave por IP real do cliente (requer ProxyFix configurado no __init__.py)
# RATELIMIT_STORAGE_URI no .env ativa Redis em produção; sem ela usa memória por processo
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri=os.environ.get('RATELIMIT_STORAGE_URI', 'memory://'),
)

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Você precisa estar logado para acessar esta página.'
login_manager.login_message_category = 'warning'
