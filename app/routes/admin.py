"""
routes/admin.py — Rotas do Painel Administrativo

Apenas usuários com role='admin' podem acessar estas rotas.
O decorator @admin_required verifica isso automaticamente.
"""

from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.user import User
from app.models.pet_post import PetPost

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """
    Decorator customizado que verifica se o usuário é admin.

    Como usar:
        @admin_bp.route('/alguma-rota')
        @login_required
        @admin_required
        def minha_rota():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)  # Acesso proibido
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """GET /admin — Painel principal com estatísticas gerais."""

    # Estatísticas para o dashboard
    total_users = User.query.count()
    total_posts = PetPost.query.count()
    active_posts = PetPost.query.filter_by(is_active=True, is_resolved=False).count()
    resolved_posts = PetPost.query.filter_by(is_resolved=True).count()
    lost_posts = PetPost.query.filter_by(status='lost', is_active=True, is_resolved=False).count()
    found_posts = PetPost.query.filter_by(status='found', is_active=True, is_resolved=False).count()

    # Posts mais recentes para exibir no dashboard
    recent_posts = (
        PetPost.query
        .order_by(PetPost.created_at.desc())
        .limit(5)
        .all()
    )

    # Usuários mais recentes
    recent_users = (
        User.query
        .order_by(User.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        'admin/dashboard.html',
        title='Painel Administrativo',
        total_users=total_users,
        total_posts=total_posts,
        active_posts=active_posts,
        resolved_posts=resolved_posts,
        lost_posts=lost_posts,
        found_posts=found_posts,
        recent_posts=recent_posts,
        recent_users=recent_users
    )


@admin_bp.route('/usuarios')
@login_required
@admin_required
def users():
    """GET /admin/usuarios — Lista todos os usuários cadastrados."""
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/dashboard.html', users=all_users, title='Gerenciar Usuários', view='users')


@admin_bp.route('/usuarios/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    """POST /admin/usuarios/<id>/toggle — Ativa ou desativa um usuário."""
    user = User.query.get_or_404(user_id)

    # Impede que o admin desative a própria conta
    if user.id == current_user.id:
        flash('Você não pode desativar sua própria conta.', 'danger')
        return redirect(url_for('admin.users'))

    user.is_active = not user.is_active
    db.session.commit()

    status = 'ativado' if user.is_active else 'desativado'
    flash(f'Usuário {user.name} foi {status}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/posts')
@login_required
@admin_required
def posts():
    """GET /admin/posts — Lista todos os posts para moderação."""
    all_posts = PetPost.query.order_by(PetPost.created_at.desc()).all()
    return render_template('admin/dashboard.html', posts=all_posts, title='Gerenciar Posts', view='posts')

# TODO: Implementar painel de moderação com aprovação de posts
# TODO: Adicionar relatórios e gráficos de estatísticas
# TODO: Módulo de Petshops parceiros — cadastro e gerenciamento
# TODO: Sistema de notificações para admins quando há novos posts
