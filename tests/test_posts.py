"""
tests/test_posts.py — Testes de Posts de Pets

Testa as rotas de criação, listagem, detalhe, edição e exclusão de posts.
"""

import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.pet_post import PetPost


@pytest.fixture
def app():
    """Cria app de teste com banco em memória."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    """Cria e retorna um usuário comum logado."""
    with app.app_context():
        u = User(name='João Teste', email='joao@teste.com')
        u.set_password('Senha@123')
        db.session.add(u)
        db.session.commit()
        return u


@pytest.fixture
def admin_user(app):
    """Cria e retorna um usuário admin."""
    with app.app_context():
        u = User(name='Admin', email='admin@teste.com', role='admin')
        u.set_password('Admin@123')
        db.session.add(u)
        db.session.commit()
        return u


@pytest.fixture
def post(app, user):
    """Cria e retorna um post de teste."""
    with app.app_context():
        p = PetPost(
            title='Cachorro perdido no parque',
            description='Cachorro caramelo, porte médio, muito dócil.',
            status='lost',
            pet_type='dog',
            last_seen_location='Parque Ibirapuera, São Paulo/SP',
            contact_phone='(11) 99999-9999',
            user_id=1  # ID do usuário criado pelo fixture user
        )
        db.session.add(p)
        db.session.commit()
        return p


def login(client, email, password):
    """Função auxiliar para logar um usuário nos testes."""
    return client.post('/auth/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)


# -----------------------------------------------
# Testes de listagem
# -----------------------------------------------

def test_list_posts_loads(client):
    """A página de listagem deve retornar status 200."""
    response = client.get('/posts/')
    assert response.status_code == 200


def test_home_page_loads(client):
    """A página inicial deve retornar status 200."""
    response = client.get('/')
    assert response.status_code == 200


# -----------------------------------------------
# Testes de criação
# -----------------------------------------------

def test_create_post_requires_login(client):
    """Visitante sem login deve ser redirecionado para a tela de login."""
    response = client.get('/posts/criar')
    # Deve redirecionar para /auth/login
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_create_post_form_loads_when_logged_in(client, user):
    """Usuário logado deve conseguir ver o formulário de criação."""
    login(client, 'joao@teste.com', 'Senha@123')
    response = client.get('/posts/criar')
    assert response.status_code == 200


# -----------------------------------------------
# Testes de detalhe
# -----------------------------------------------

def test_post_detail_loads(client, post):
    """A página de detalhe de um post existente deve retornar 200."""
    response = client.get('/posts/1')
    assert response.status_code == 200


def test_post_detail_404(client):
    """Acessar um post inexistente deve retornar 404."""
    response = client.get('/posts/99999')
    assert response.status_code == 404


# -----------------------------------------------
# Testes de permissão
# -----------------------------------------------

def test_edit_post_requires_owner_or_admin(client, user, post):
    """
    Outro usuário não deve conseguir editar o post.
    """
    # Cria um segundo usuário
    with client.application.app_context():
        outro = User(name='Outro', email='outro@teste.com')
        outro.set_password('Senha@123')
        db.session.add(outro)
        db.session.commit()

    # Loga como o segundo usuário
    login(client, 'outro@teste.com', 'Senha@123')
    response = client.get('/posts/1/editar')
    # Deve retornar 403 (Proibido)
    assert response.status_code == 403


# TODO: Adicionar testes para upload de fotos
# TODO: Adicionar testes para filtros de listagem
# TODO: Adicionar testes para paginação
# TODO: Adicionar testes para marcar post como resolvido
