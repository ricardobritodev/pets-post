"""
forms/__init__.py — Pacote de Formulários
"""

from app.forms.auth_forms import LoginForm, RegisterForm
from app.forms.post_forms import PetPostForm

__all__ = ['LoginForm', 'RegisterForm', 'PetPostForm']
