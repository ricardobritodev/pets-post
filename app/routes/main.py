"""
routes/main.py — Rotas Principais

Blueprint responsável pela página inicial e sobre o projeto.
"""

from flask import Blueprint, render_template
from app.models.pet_post import PetPost

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """GET / — Página inicial com feed dos últimos 12 posts ativos."""

    # Busca os 12 posts mais recentes que estão ativos e não resolvidos
    posts = (
        PetPost.query
        .filter_by(is_active=True, is_resolved=False)
        .order_by(PetPost.created_at.desc())
        .limit(12)
        .all()
    )

    return render_template('main/index.html', posts=posts)


@main_bp.route('/sobre')
def about():
    """GET /sobre — Página sobre o projeto."""
    return render_template('main/about.html', title='Sobre')

# TODO: Implementar busca por CEP com ViaCEP API para filtrar posts por região
# TODO: Adicionar página de estatísticas (pets reencontrados, posts ativos)
