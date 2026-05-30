"""
forms/auth_forms.py — Formulários de Autenticação

WTForms valida os dados antes de chegar ao banco de dados.
Cada campo tem validadores que garantem os dados corretos.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Optional, Regexp, ValidationError
)


class LoginForm(FlaskForm):
    """Formulário de login — campos email e senha."""

    email = StringField(
        'Email',
        validators=[
            DataRequired(message='O email é obrigatório.'),
            Email(check_deliverability=False, message='Informe um email válido.')
        ],
        render_kw={'placeholder': 'seu@email.com', 'autocomplete': 'email', 'type': 'email'}
    )

    password = PasswordField(
        'Senha',
        validators=[
            DataRequired(message='A senha é obrigatória.')
        ],
        render_kw={'placeholder': '••••••••', 'autocomplete': 'current-password'}
    )

    # Checkbox "Lembrar de mim" — mantém o usuário logado por mais tempo
    remember = BooleanField('Lembrar de mim')

    submit = SubmitField('Entrar')


class RegisterForm(FlaskForm):
    """Formulário de cadastro de novo usuário."""

    name = StringField(
        'Nome completo',
        validators=[
            DataRequired(message='O nome é obrigatório.'),
            Length(min=2, max=100, message='O nome deve ter entre 2 e 100 caracteres.')
        ],
        render_kw={'placeholder': 'João Silva'}
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(message='O email é obrigatório.'),
            Email(check_deliverability=False, message='Informe um email válido.')
        ],
        render_kw={'placeholder': 'seu@email.com', 'autocomplete': 'email', 'type': 'email'}
    )

    phone = StringField(
        'Telefone (opcional)',
        validators=[
            Optional(),
            Regexp(r'^\(\d{2}\) \d{4,5}-\d{4}$', message='Telefone inválido. Use (XX) XXXX-XXXX ou (XX) XXXXX-XXXX.')
        ],
        render_kw={'placeholder': '(11) 99999-9999', 'type': 'tel', 'maxlength': '15'}
    )

    password = PasswordField(
        'Senha',
        validators=[
            DataRequired(message='A senha é obrigatória.'),
            Length(min=8, message='A senha deve ter pelo menos 8 caracteres.')
        ],
        render_kw={'placeholder': 'Mínimo 8 caracteres', 'autocomplete': 'new-password'}
    )

    confirm_password = PasswordField(
        'Confirmar senha',
        validators=[
            DataRequired(message='Confirme sua senha.'),
            EqualTo('password', message='As senhas não coincidem.')
        ],
        render_kw={'placeholder': 'Repita a senha', 'autocomplete': 'new-password'}
    )

    submit = SubmitField('Criar conta')

    def validate_email(self, field):
        """
        Validação customizada: verifica se o email já está cadastrado.
        O método validate_<nome_do_campo> é chamado automaticamente pelo WTForms.
        """
        from app.models.user import User
        user = User.query.filter_by(email=field.data.lower()).first()
        if user:
            raise ValidationError('Este email já está cadastrado. Faça login ou use outro email.')
