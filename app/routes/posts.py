"""
routes/posts.py — Rotas de Posts de Pets

Blueprint responsável pelo CRUD (Create, Read, Update, Delete) de posts.
"""

import os
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, abort, current_app
)
from flask_login import login_required, current_user

from app.extensions import db
from app.models.pet_post import PetPost
from app.models.photo import Photo
from app.forms.post_forms import PetPostForm
from app.services.geocoding import geocode_address
from app.utils.upload import allowed_file, save_photo

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')


@posts_bp.route('/')
def list_posts():
    """
    GET /posts — Lista todos os posts com filtros e paginação.

    Parâmetros de query string:
        status: 'lost' ou 'found' (padrão: todos)
        pet_type: 'dog', 'cat', 'bird', 'other' (padrão: todos)
        page: número da página (padrão: 1)
    """
    # Pega os filtros da URL, ex: /posts?status=lost&pet_type=dog
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('pet_type', '')
    page = request.args.get('page', 1, type=int)

    # Começa a query com posts ativos
    query = PetPost.query.filter_by(is_active=True, is_resolved=False)

    # Aplica os filtros se foram informados
    if status_filter in ('lost', 'found'):
        query = query.filter_by(status=status_filter)

    if type_filter in ('dog', 'cat', 'bird', 'other'):
        query = query.filter_by(pet_type=type_filter)

    # Ordena por data e pagina os resultados
    posts = (
        query
        .order_by(PetPost.created_at.desc())
        .paginate(page=page, per_page=12, error_out=False)
    )

    template_vars = dict(
        posts=posts,
        status_filter=status_filter,
        type_filter=type_filter,
        title='Todos os posts'
    )

    # Requisições AJAX recebem apenas o partial do grid (sem page wrapper)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('posts/_grid.html', **template_vars)

    return render_template('posts/list.html', **template_vars)


@posts_bp.route('/<int:post_id>')
def detail(post_id):
    """GET /posts/<id> — Exibe os detalhes de um post."""

    # get_or_404 retorna o post ou exibe a página de erro 404 automaticamente
    post = PetPost.query.get_or_404(post_id)

    # Posts inativos só são visíveis para o dono ou admin
    if not post.is_active:
        if not current_user.is_authenticated:
            abort(404)
        if current_user.id != post.user_id and not current_user.is_admin():
            abort(404)

    return render_template('posts/detail.html', post=post, title=post.title)


@posts_bp.route('/criar', methods=['GET', 'POST'])
@login_required  # Redireciona para login se não estiver autenticado
def create():
    """
    GET  /posts/criar — Exibe o formulário de criação
    POST /posts/criar — Processa e cria o post
    """
    form = PetPostForm()

    if request.method == 'GET':
        status_param = request.args.get('status')
        if status_param in ('lost', 'found'):
            form.status.data = status_param

    if form.validate_on_submit():
        # Cria o post com os dados do formulário
        post = PetPost(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            status=form.status.data,
            pet_name=form.pet_name.data.strip() if form.pet_name.data else None,
            pet_type=form.pet_type.data,
            pet_breed=form.pet_breed.data.strip() if form.pet_breed.data else None,
            pet_color=form.pet_color.data.strip() if form.pet_color.data else None,
            pet_size=form.pet_size.data if form.pet_size.data else None,
            last_seen_location=form.last_seen_location.data.strip(),
            contact_phone=form.contact_phone.data.strip(),
            contact_email=form.contact_email.data.strip() if form.contact_email.data else None,
            reward=form.reward.data.strip() if form.reward.data else None,
            user_id=current_user.id
        )

        db.session.add(post)
        db.session.flush()  # Gera o ID do post antes de salvar as fotos

        # Processa as fotos enviadas
        if form.photos.data:
            is_first = True
            for i, file in enumerate(form.photos.data):
                if file and file.filename and allowed_file(file.filename):
                    try:
                        filename = save_photo(file)
                        photo = Photo(
                            filename=filename,
                            url=f'/static/uploads/{filename}',
                            is_primary=is_first,  # A primeira foto é a principal
                            post_id=post.id
                        )
                        db.session.add(photo)
                        is_first = False
                    except Exception as e:
                        current_app.logger.warning('Erro ao salvar foto: %s', e)
                        flash('Não foi possível salvar uma das fotos. Tente novamente.', 'warning')

        db.session.commit()

        # Geocodifica o endereço em background — falha silenciosa se a API estiver fora
        lat, lng = geocode_address(post.last_seen_location)
        if lat and lng:
            post.last_seen_lat = lat
            post.last_seen_lng = lng
            db.session.commit()

        flash('Seu anúncio foi publicado com sucesso!', 'success')
        return redirect(url_for('posts.detail', post_id=post.id))

    return render_template('posts/create.html', form=form, title='Criar anúncio')


@posts_bp.route('/<int:post_id>/editar', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    """
    GET  /posts/<id>/editar — Exibe o formulário de edição
    POST /posts/<id>/editar — Salva as alterações

    Apenas o dono do post ou um admin pode editar.
    """
    post = PetPost.query.get_or_404(post_id)

    # Verifica permissão
    if current_user.id != post.user_id and not current_user.is_admin():
        abort(403)  # Proibido

    form = PetPostForm(obj=post)

    if form.validate_on_submit():
        # Atualiza os campos do post
        post.title = form.title.data.strip()
        post.description = form.description.data.strip()
        post.status = form.status.data
        post.pet_name = form.pet_name.data.strip() if form.pet_name.data else None
        post.pet_type = form.pet_type.data
        post.pet_breed = form.pet_breed.data.strip() if form.pet_breed.data else None
        post.pet_color = form.pet_color.data.strip() if form.pet_color.data else None
        post.pet_size = form.pet_size.data if form.pet_size.data else None
        post.last_seen_location = form.last_seen_location.data.strip()
        post.contact_phone = form.contact_phone.data.strip()
        post.contact_email = form.contact_email.data.strip() if form.contact_email.data else None
        post.reward = form.reward.data.strip() if form.reward.data else None

        # Adiciona novas fotos se enviadas
        if form.photos.data:
            current_count = len(post.photos)
            for file in form.photos.data:
                if file and file.filename and allowed_file(file.filename):
                    if current_count >= 5:
                        flash('Limite de 5 fotos atingido. Novas fotos não foram adicionadas.', 'warning')
                        break
                    try:
                        filename = save_photo(file)
                        photo = Photo(
                            filename=filename,
                            url=f'/static/uploads/{filename}',
                            is_primary=(current_count == 0),
                            post_id=post.id
                        )
                        db.session.add(photo)
                        current_count += 1
                    except Exception as e:
                        current_app.logger.warning('Erro ao salvar foto: %s', e)
                        flash('Não foi possível salvar uma das fotos. Tente novamente.', 'warning')

        db.session.commit()

        # Re-geocodifica se o endereço foi alterado
        lat, lng = geocode_address(post.last_seen_location)
        if lat and lng:
            post.last_seen_lat = lat
            post.last_seen_lng = lng
            db.session.commit()

        flash('Anúncio atualizado com sucesso!', 'success')
        return redirect(url_for('posts.detail', post_id=post.id))

    return render_template('posts/edit.html', form=form, post=post, title='Editar anúncio')


@posts_bp.route('/<int:post_id>/deletar', methods=['POST'])
@login_required
def delete(post_id):
    """POST /posts/<id>/deletar — Deleta o post (apenas dono ou admin)."""
    post = PetPost.query.get_or_404(post_id)

    if current_user.id != post.user_id and not current_user.is_admin():
        abort(403)

    # Remove os arquivos de foto do disco
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    for photo in post.photos:
        filepath = os.path.join(upload_folder, photo.filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    db.session.delete(post)
    db.session.commit()

    flash('Anúncio removido com sucesso.', 'info')
    return redirect(url_for('posts.list_posts'))


@posts_bp.route('/<int:post_id>/resolver', methods=['POST'])
@login_required
def resolve(post_id):
    """POST /posts/<id>/resolver — Marca o post como resolvido (pet reencontrado!)."""
    post = PetPost.query.get_or_404(post_id)

    if current_user.id != post.user_id and not current_user.is_admin():
        abort(403)

    post.is_resolved = True
    db.session.commit()

    flash('Que ótima notícia! O post foi marcado como resolvido. 🎉', 'success')
    return redirect(url_for('posts.detail', post_id=post.id))

# TODO: Integrar Google Maps API para geocodificar o endereço e exibir no mapa
# TODO: Implementar busca por CEP com ViaCEP API
# TODO: Implementar sistema de notificações por email quando um post similar aparecer
# TODO: Chat entre usuário que encontrou e dono do pet
# TODO: Integração com WhatsApp para contato direto
