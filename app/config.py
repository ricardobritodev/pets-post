"""
config.py — Configurações da aplicação PetPost

Existem três ambientes:
  - DevelopmentConfig: para rodar na sua máquina local
  - TestingConfig: para rodar os testes automatizados
  - ProductionConfig: para o servidor real na internet

A variável FLASK_ENV no arquivo .env decide qual configuração usar.
"""

import os

# Carrega as variáveis do arquivo .env automaticamente
from dotenv import load_dotenv
load_dotenv()


class Config:
    """Configurações base — compartilhadas por todos os ambientes."""

    # Chave secreta para proteger sessões e tokens de formulário
    # Gerada pelo arquivo .env — NUNCA deixe o valor padrão em produção!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'

    # Desativa rastreamento de modificações do SQLAlchemy (economiza memória)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Tamanho máximo de upload: 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Pasta onde as fotos enviadas pelos usuários são salvas
    UPLOAD_FOLDER = 'app/static/uploads'

    # Tipos de arquivo de imagem aceitos no upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # TODO: Adicionar configurações de email (Flask-Mail) para notificações


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

    # Em produção, o DATABASE_URL DEVE estar configurado no servidor
    # Se não estiver, a aplicação vai falhar — isso é intencional!
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # TODO: Configurar HTTPS obrigatório
    # TODO: Configurar rate limiting para evitar abuso


# Dicionário para selecionar a configuração pelo nome
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
