"""
routes/auth.py — Rotas de Autenticação

Blueprint responsável por: login, logout e cadastro de usuários.

Um Blueprint é um grupo de rotas relacionadas.
Ele é registrado no app principal em app/__init__.py.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.models.user import User
from app.forms.auth_forms import LoginForm, RegisterForm

# Cria o blueprint com o prefixo de URL /auth
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET  /auth/login — Exibe o formulário de login
    POST /auth/login — Processa o formulário e autentica o usuário
    """
    # Se o usuário já está logado, redireciona para a home
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        # Busca o usuário pelo email (normalizado para minúsculas)
        user = User.query.filter_by(email=form.email.data.lower()).first()

        # Verifica se o usuário existe, a senha está correta e a conta está ativa
        if user is None or not user.check_password(form.password.data):
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Esta conta foi desativada. Entre em contato com o suporte.', 'warning')
            return redirect(url_for('auth.login'))

        # Loga o usuário — Flask-Login cria a sessão
        login_user(user, remember=form.remember.data)

        flash(f'Bem-vindo de volta, {user.name}!', 'success')

        # Redireciona para a página que o usuário tentou acessar antes do login
        # ou para a home se não havia página anterior
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))

    return render_template('auth/login.html', form=form, title='Login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET  /auth/register — Exibe o formulário de cadastro
    POST /auth/register — Processa e cria o novo usuário
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()

    if form.validate_on_submit():
        # Cria o novo usuário
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            phone=form.phone.data.strip() if form.phone.data else None
        )
        # Define a senha como hash (nunca salvar em texto puro!)
        user.set_password(form.password.data)

        # Salva no banco de dados
        db.session.add(user)
        db.session.commit()

        flash('Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form, title='Criar conta')


@auth_bp.route('/logout')
@login_required  # Só pode fazer logout quem está logado
def logout():
    """GET /auth/logout — Encerra a sessão do usuário."""
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('main.index'))

# TODO: Implementar recuperação de senha por email (Flask-Mail)
# TODO: Implementar verificação de email no cadastro
# TODO: Implementar login com Google OAuth
