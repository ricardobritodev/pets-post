"""
app/__init__.py — Application Factory do PetPost

O padrão Application Factory permite criar múltiplas instâncias do app
(ex: uma para desenvolvimento, outra para testes) sem conflitos.

Como funciona:
  1. A função create_app() cria e configura o Flask
  2. Registra todas as extensões (banco, login, etc.)
  3. Registra todos os blueprints (grupos de rotas)
  4. Retorna o app pronto para uso
"""

import os
from datetime import datetime
from flask import Flask

from app.config import config
from app.extensions import db, login_manager, migrate, csrf


def create_app(config_name=None):
    """
    Cria e configura a aplicação Flask.

    Parâmetros:
        config_name: 'development', 'testing' ou 'production'
                     Se não informado, usa a variável FLASK_ENV do .env
    """

    # Determina qual configuração usar
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    # Cria a instância do Flask
    # __name__ diz ao Flask onde procurar templates e arquivos estáticos
    app = Flask(__name__)

    # Carrega as configurações (do arquivo config.py)
    app.config.from_object(config.get(config_name, config['default']))

    # -----------------------------------------------
    # Registra as extensões no app
    # -----------------------------------------------
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # -----------------------------------------------
    # Importa os models para que o Flask-Migrate os encontre
    # (necessário para gerar as migrações corretamente)
    # -----------------------------------------------
    with app.app_context():
        from app.models import user, pet_post, photo, adoption_post, adoption_photo, partner  # noqa: F401

    # -----------------------------------------------
    # Registra os blueprints (grupos de rotas)
    # Cada blueprint é um módulo independente de funcionalidade
    # -----------------------------------------------
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.posts import posts_bp
    from app.routes.admin import admin_bp
    from app.routes.adoption import adoption_bp
    from app.routes.map import map_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(adoption_bp)
    app.register_blueprint(map_bp)

    # -----------------------------------------------
    # Variáveis globais disponíveis em todos os templates
    # -----------------------------------------------
    @app.context_processor
    def inject_globals():
        return {'current_year': datetime.utcnow().year}

    # -----------------------------------------------
    # Garante que a pasta de uploads existe
    # -----------------------------------------------
    uploads_path = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(uploads_path, exist_ok=True)

    return app
