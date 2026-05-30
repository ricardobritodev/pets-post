import os
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, abort, current_app
)
from flask_login import login_required, current_user

from app.extensions import db
from app.models.adoption_post import AdoptionPost
from app.models.adoption_photo import AdoptionPhoto
from app.forms.adoption_forms import AdoptionForm
from app.services.geocoding import geocode_address
from app.utils.upload import allowed_file, save_photo

adoption_bp = Blueprint('adoption', __name__, url_prefix='/adocao')


@adoption_bp.route('/')
def list_posts():
    type_filter = request.args.get('pet_type', '')
    page = request.args.get('page', 1, type=int)

    query = AdoptionPost.query.filter_by(is_active=True, is_adopted=False)

    if type_filter in ('dog', 'cat', 'bird', 'other'):
        query = query.filter_by(pet_type=type_filter)

    posts = (
        query
        .order_by(AdoptionPost.created_at.desc())
        .paginate(page=page, per_page=12, error_out=False)
    )

    template_vars = dict(posts=posts, type_filter=type_filter, title='Adoção')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('adoption/_grid.html', **template_vars)

    return render_template('adoption/list.html', **template_vars)


@adoption_bp.route('/<int:post_id>')
def detail(post_id):
    post = db.session.get(AdoptionPost, post_id)
    if post is None:
        abort(404)

    if not post.is_active:
        if not current_user.is_authenticated:
            abort(404)
        if current_user.id != post.user_id and not current_user.is_admin():
            abort(404)

    return render_template('adoption/detail.html', post=post, title=post.title)


@adoption_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def create():
    form = AdoptionForm()

    if form.validate_on_submit():
        post = AdoptionPost(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            pet_name=form.pet_name.data.strip() if form.pet_name.data else None,
            pet_type=form.pet_type.data,
            pet_breed=form.pet_breed.data.strip() if form.pet_breed.data else None,
            pet_color=form.pet_color.data.strip() if form.pet_color.data else None,
            pet_size=form.pet_size.data if form.pet_size.data else None,
            is_neutered=form.is_neutered.data,
            is_vaccinated=form.is_vaccinated.data,
            adopter_requirements=form.adopter_requirements.data.strip() if form.adopter_requirements.data else None,
            location=form.location.data.strip(),
            contact_phone=form.contact_phone.data.strip(),
            contact_email=form.contact_email.data.strip() if form.contact_email.data else None,
            user_id=current_user.id
        )

        db.session.add(post)
        db.session.flush()

        if form.photos.data:
            is_first = True
            for file in form.photos.data:
                if file and file.filename and allowed_file(file.filename):
                    try:
                        filename = save_photo(file)
                        photo = AdoptionPhoto(
                            filename=filename,
                            url=f'/static/uploads/{filename}',
                            is_primary=is_first,
                            adoption_post_id=post.id
                        )
                        db.session.add(photo)
                        is_first = False
                    except Exception as e:
                        current_app.logger.warning('Erro ao salvar foto: %s', e)
                        flash('Não foi possível salvar uma das fotos. Tente novamente.', 'warning')

        db.session.commit()

        lat, lng = geocode_address(post.location)
        if lat and lng:
            post.location_lat = lat
            post.location_lng = lng
            db.session.commit()

        flash('Anúncio de adoção publicado com sucesso!', 'success')
        return redirect(url_for('adoption.detail', post_id=post.id))

    return render_template('adoption/create.html', form=form, title='Colocar para adoção')


@adoption_bp.route('/<int:post_id>/editar', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = db.session.get(AdoptionPost, post_id)
    if post is None:
        abort(404)

    if current_user.id != post.user_id and not current_user.is_admin():
        abort(403)

    form = AdoptionForm(obj=post)

    if form.validate_on_submit():
        post.title = form.title.data.strip()
        post.description = form.description.data.strip()
        post.pet_name = form.pet_name.data.strip() if form.pet_name.data else None
        post.pet_type = form.pet_type.data
        post.pet_breed = form.pet_breed.data.strip() if form.pet_breed.data else None
        post.pet_color = form.pet_color.data.strip() if form.pet_color.data else None
        post.pet_size = form.pet_size.data if form.pet_size.data else None
        post.is_neutered = form.is_neutered.data
        post.is_vaccinated = form.is_vaccinated.data
        post.adopter_requirements = form.adopter_requirements.data.strip() if form.adopter_requirements.data else None
        post.location = form.location.data.strip()
        post.contact_phone = form.contact_phone.data.strip()
        post.contact_email = form.contact_email.data.strip() if form.contact_email.data else None

        # Deleta fotos marcadas pelo usuário
        photos_to_delete = request.form.get('photos_to_delete', '')
        if photos_to_delete:
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            for raw_id in photos_to_delete.split(','):
                try:
                    photo_id = int(raw_id.strip())
                except ValueError:
                    continue
                photo = AdoptionPhoto.query.filter_by(id=photo_id, adoption_post_id=post.id).first()
                if photo:
                    filepath = os.path.join(upload_folder, photo.filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    db.session.delete(photo)
            db.session.flush()
            remaining = AdoptionPhoto.query.filter_by(adoption_post_id=post.id).all()
            if remaining and not any(p.is_primary for p in remaining):
                remaining[0].is_primary = True

        if form.photos.data:
            current_count = len(post.photos)
            for file in form.photos.data:
                if file and file.filename and allowed_file(file.filename):
                    if current_count >= 6:
                        flash('Limite de 6 fotos atingido. Novas fotos não foram adicionadas.', 'warning')
                        break
                    try:
                        filename = save_photo(file)
                        photo = AdoptionPhoto(
                            filename=filename,
                            url=f'/static/uploads/{filename}',
                            is_primary=(current_count == 0),
                            adoption_post_id=post.id
                        )
                        db.session.add(photo)
                        current_count += 1
                    except Exception as e:
                        current_app.logger.warning('Erro ao salvar foto: %s', e)
                        flash('Não foi possível salvar uma das fotos. Tente novamente.', 'warning')

        db.session.commit()

        lat, lng = geocode_address(post.location)
        if lat and lng:
            post.location_lat = lat
            post.location_lng = lng
            db.session.commit()

        flash('Anúncio atualizado com sucesso!', 'success')
        return redirect(url_for('adoption.detail', post_id=post.id))

    return render_template('adoption/edit.html', form=form, post=post, title='Editar anúncio de adoção')


@adoption_bp.route('/<int:post_id>/deletar', methods=['POST'])
@login_required
def delete(post_id):
    post = db.session.get(AdoptionPost, post_id)
    if post is None:
        abort(404)

    if current_user.id != post.user_id and not current_user.is_admin():
        abort(403)

    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    for photo in post.photos:
        filepath = os.path.join(upload_folder, photo.filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    db.session.delete(post)
    db.session.commit()

    flash('Anúncio de adoção removido com sucesso.', 'info')
    return redirect(url_for('adoption.list_posts'))


@adoption_bp.route('/<int:post_id>/adotado', methods=['POST'])
@login_required
def mark_adopted(post_id):
    post = db.session.get(AdoptionPost, post_id)
    if post is None:
        abort(404)

    if current_user.id != post.user_id and not current_user.is_admin():
        abort(403)

    post.is_adopted = True
    db.session.commit()

    flash('Que ótima notícia! O pet foi marcado como adotado. 🎉', 'success')
    return redirect(url_for('adoption.detail', post_id=post.id))
