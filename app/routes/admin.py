"""
routes/admin.py — Rotas do Painel Administrativo

Apenas usuários com role='admin' podem acessar estas rotas.
O decorator @admin_required verifica isso automaticamente.
"""

from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.user import User
from app.models.pet_post import PetPost
from app.models.partner import Partner
from app.forms.partner_forms import PartnerForm
from app.services.geocoding import geocode_address

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """
    Decorator que verifica autenticação e role admin.

    Autossuficiente: não depende de @login_required estar empilhado antes.
    Retorna 401 para não autenticados, 403 para usuários sem role admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin():
            abort(403)
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

@admin_bp.route('/parceiros')
@login_required
@admin_required
def partners():
    all_partners = Partner.query.order_by(Partner.created_at.desc()).all()
    return render_template(
        'admin/dashboard.html',
        partners=all_partners,
        title='Gerenciar Parceiros',
        view='partners'
    )


@admin_bp.route('/parceiros/criar', methods=['GET', 'POST'])
@login_required
@admin_required
def partner_create():
    form = PartnerForm()

    if form.validate_on_submit():
        partner = Partner(
            name=form.name.data.strip(),
            partner_type=form.partner_type.data,
            description=form.description.data.strip() if form.description.data else None,
            address=form.address.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            email=form.email.data.strip() if form.email.data else None,
            website=form.website.data.strip() if form.website.data else None,
            is_active=form.is_active.data,
        )
        db.session.add(partner)
        db.session.flush()

        lat, lng = geocode_address(partner.address)
        if lat and lng:
            partner.lat = lat
            partner.lng = lng
        else:
            flash('Endereço não encontrado no mapa. Verifique e edite se necessário.', 'warning')

        db.session.commit()
        flash(f'Parceiro "{partner.name}" cadastrado com sucesso!', 'success')
        return redirect(url_for('admin.partners'))

    return render_template('admin/partner_form.html', form=form, title='Novo Parceiro', partner=None)


@admin_bp.route('/parceiros/<int:partner_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def partner_edit(partner_id):
    partner = db.session.get(Partner, partner_id)
    if partner is None:
        abort(404)

    form = PartnerForm(obj=partner)

    if form.validate_on_submit():
        old_address = partner.address
        partner.name = form.name.data.strip()
        partner.partner_type = form.partner_type.data
        partner.description = form.description.data.strip() if form.description.data else None
        partner.address = form.address.data.strip()
        partner.phone = form.phone.data.strip() if form.phone.data else None
        partner.email = form.email.data.strip() if form.email.data else None
        partner.website = form.website.data.strip() if form.website.data else None
        partner.is_active = form.is_active.data

        if partner.address != old_address or not partner.lat:
            lat, lng = geocode_address(partner.address)
            if lat and lng:
                partner.lat = lat
                partner.lng = lng
            else:
                flash('Endereço não encontrado no mapa. Verifique e tente novamente.', 'warning')

        db.session.commit()
        flash(f'Parceiro "{partner.name}" atualizado com sucesso!', 'success')
        return redirect(url_for('admin.partners'))

    return render_template('admin/partner_form.html', form=form, title='Editar Parceiro', partner=partner)


@admin_bp.route('/parceiros/<int:partner_id>/deletar', methods=['POST'])
@login_required
@admin_required
def partner_delete(partner_id):
    partner = db.session.get(Partner, partner_id)
    if partner is None:
        abort(404)

    name = partner.name
    db.session.delete(partner)
    db.session.commit()

    flash(f'Parceiro "{name}" removido.', 'info')
    return redirect(url_for('admin.partners'))
