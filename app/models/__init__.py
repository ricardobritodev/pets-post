"""
models/__init__.py — Pacote de Models

Importa todos os models para facilitar o acesso de outros módulos.
Também garante que o Flask-Migrate encontre todas as tabelas.
"""

from app.models.user import User
from app.models.pet_post import PetPost
from app.models.photo import Photo

__all__ = ['User', 'PetPost', 'Photo']
