"""
routes/auth.py — Rotas de Autenticação

Blueprint responsável por: login, logout e cadastro de usuários.

Um Blueprint é um grupo de rotas relacionadas.
Ele é registrado no app principal em app/__init__.py.
"""

import logging
from urllib.parse import urlparse, urljoin

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db, limiter
from app.models.user import User
from app.forms.auth_forms import LoginForm, RegisterForm

security_log = logging.getLogger('petpost.security')


def _is_safe_redirect(url: str) -> bool:
    """Aceita apenas redirects para o mesmo host — bloqueia open redirects."""
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, url))
    return test.scheme in ('http', 'https') and ref.netloc == test.netloc


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute; 50 per hour")
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

        if user is None or not user.check_password(form.password.data):
            security_log.warning(
                'login_failed email=%s ip=%s',
                form.email.data.lower(), request.remote_addr
            )
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            security_log.warning(
                'login_blocked_inactive user_id=%s ip=%s',
                user.id, request.remote_addr
            )
            flash('Esta conta foi desativada. Entre em contato com o suporte.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember.data)
        security_log.info(
            'login_success user_id=%s ip=%s',
            user.id, request.remote_addr
        )

        flash(f'Bem-vindo de volta, {user.name}!', 'success')

        next_page = request.args.get('next')
        if next_page and not _is_safe_redirect(next_page):
            next_page = None
        return redirect(next_page or url_for('main.index'))

    return render_template('auth/login.html', form=form, title='Login')


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute; 20 per hour")
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

        security_log.info(
            'register_success user_id=%s email=%s ip=%s',
            user.id, user.email, request.remote_addr
        )
        flash('Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form, title='Criar conta')


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """POST /auth/logout — Encerra a sessão do usuário (requer CSRF token)."""
    security_log.info('logout user_id=%s ip=%s', current_user.id, request.remote_addr)
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('main.index'))

# TODO: Implementar recuperação de senha por email (Flask-Mail)
# TODO: Implementar verificação de email no cadastro
# TODO: Implementar login com Google OAuth
