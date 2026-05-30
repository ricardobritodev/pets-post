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
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import config
from app.extensions import db, login_manager, migrate, csrf, limiter

# CSP compatível com os recursos usados pela app:
#   - Leaflet (unpkg.com), Google Fonts, OpenStreetMap tiles
#   - unsafe-inline necessário para os poucos estilos inline nos templates
_PRODUCTION_CSP = {
    'default-src': "'self'",
    'script-src': ["'self'", 'unpkg.com'],
    'style-src': ["'self'", "'unsafe-inline'", 'fonts.googleapis.com', 'unpkg.com'],
    'font-src': ["'self'", 'fonts.gstatic.com'],
    'img-src': ["'self'", 'data:', '*.tile.openstreetmap.org', 'unpkg.com'],
    'connect-src': ["'self'", 'fonts.googleapis.com', 'fonts.gstatic.com'],
    'frame-ancestors': "'none'",
}


def create_app(config_name=None):
    """
    Cria e configura a aplicação Flask.

    Parâmetros:
        config_name: 'development', 'testing' ou 'production'
                     Se não informado, usa a variável FLASK_ENV do .env
    """

    # Determina qual configuração usar.
    # FLASK_ENV foi removido no Flask 2.3 — usamos FLASK_CONFIG.
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    # Cria a instância do Flask
    # __name__ diz ao Flask onde procurar templates e arquivos estáticos
    app = Flask(__name__)

    cfg = config.get(config_name, config['default'])
    app.config.from_object(cfg)

    # Valida variáveis obrigatórias em produção (SECRET_KEY, DATABASE_URL)
    if hasattr(cfg, 'init_app'):
        cfg.init_app(app)

    # -----------------------------------------------
    # Registra as extensões no app
    # -----------------------------------------------
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    # ProxyFix: faz o Flask enxergar o IP real do cliente quando roda atrás do Nginx.
    # Sem isso, request.remote_addr e o rate limiting veem o IP do próprio Nginx.
    if config_name == 'production':
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Security headers — apenas em produção para não quebrar dev/testes
    if config_name == 'production':
        Talisman(
            app,
            force_https=True,
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,
            content_security_policy=_PRODUCTION_CSP,
            referrer_policy='strict-origin-when-cross-origin',
            feature_policy={
                'geolocation': "'none'",
                'camera': "'none'",
                'microphone': "'none'",
            },
        )

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
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(adoption_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(api_bp)

    # -----------------------------------------------
    # Filtros e globals Jinja2 customizados
    # -----------------------------------------------
    from app.utils.phone import to_whatsapp_url
    from app.utils.icons import get_icon
    from markupsafe import Markup

    app.jinja_env.filters['whatsapp_url'] = to_whatsapp_url
    app.jinja_env.globals['icon'] = lambda name, **kw: Markup(get_icon(name, **kw))

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
