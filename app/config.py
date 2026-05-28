"""
config.py — Configurações da aplicação PetPost

Existem três ambientes:
  - DevelopmentConfig: para rodar na sua máquina local
  - TestingConfig: para rodar os testes automatizados
  - ProductionConfig: para o servidor real na internet

A variável FLASK_CONFIG no arquivo .env decide qual configuração usar.
(FLASK_ENV foi removido no Flask 2.3 e não deve mais ser usado.)
"""

import os
from datetime import timedelta

from dotenv import load_dotenv
load_dotenv()


class Config:
    """Configurações base — compartilhadas por todos os ambientes."""

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Tamanho máximo de upload: 8 MB
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024

    UPLOAD_FOLDER = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Sessão expira após 2h de inatividade; renovada a cada request
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_REFRESH_EACH_REQUEST = True

    # Cookies de sessão: HttpOnly sempre ativo; Secure e SameSite sobrescritos por ambiente
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Cookie "remember me" do Flask-Login
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DURATION = timedelta(days=7)


class DevelopmentConfig(Config):
    """Configurações para desenvolvimento local."""

    # Ativa o modo debug: recarrega o servidor e mostra erros detalhados
    DEBUG = True

    # URL do banco de dados — lida do arquivo .env
    # Fallback padrão para quem não configurou o .env ainda
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or 'mysql+pymysql://root:password@localhost/petpost_dev'
    )


class TestingConfig(Config):
    """Configurações para testes automatizados."""

    TESTING = True
    DEBUG = True

    # Usa um banco de dados em memória (SQLite) para os testes
    # Isso evita poluir o banco de desenvolvimento com dados de teste
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Desativa proteção CSRF nos formulários durante testes
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Configurações para o servidor em produção."""

    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Cookies transmitidos apenas via HTTPS em produção
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    @classmethod
    def init_app(cls, app):
        """Valida variáveis obrigatórias ao iniciar em produção."""
        super().init_app(app) if hasattr(super(), 'init_app') else None

        required = {
            'SECRET_KEY': os.environ.get('SECRET_KEY'),
            'DATABASE_URL': os.environ.get('DATABASE_URL'),
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise RuntimeError(
                f"Variáveis de ambiente obrigatórias não definidas: {', '.join(missing)}. "
                "Configure o arquivo .env antes de subir em produção."
            )


# Dicionário para selecionar a configuração pelo nome
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
