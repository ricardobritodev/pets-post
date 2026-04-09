"""
tests/test_auth.py — Testes de Autenticação

Como rodar os testes:
    pytest tests/
    pytest tests/test_auth.py -v   (modo verbose, mostra cada teste)

Os testes usam um banco SQLite em memória — não afetam o banco de desenvolvimento.
"""

import pytest
from app import create_app
from app.extensions import db
from app.models.user import User


@pytest.fixture
def app():
    """
    Fixture: cria uma instância do app configurada para testes.
    É recriada para cada teste — banco limpo a cada execução.
    """
    app = create_app('testing')

    with app.app_context():
        db.create_all()  # Cria as tabelas no banco em memória
        yield app
        db.drop_all()    # Limpa tudo após o teste


@pytest.fixture
def client(app):
    """Fixture: cliente HTTP para fazer requisições nos testes."""
    return app.test_client()


@pytest.fixture
def user(app):
    """Fixture: cria um usuário comum para usar nos testes."""
    with app.app_context():
        u = User(name='João Teste', email='joao@teste.com')
        u.set_password('Senha@123')
        db.session.add(u)
        db.session.commit()
        return u


# -----------------------------------------------
# Testes de cadastro
# -----------------------------------------------

def test_register_page_loads(client):
    """A página de cadastro deve retornar status 200."""
    response = client.get('/auth/register')
    assert response.status_code == 200


def test_register_creates_user(client, app):
    """Um novo usuário deve ser criado após o cadastro com dados válidos."""
    response = client.post('/auth/register', data={
        'name': 'Maria Silva',
        'email': 'maria@teste.com',
        'password': 'Senha@123',
        'confirm_password': 'Senha@123',
        'csrf_token': 'test'  # CSRF desativado no modo testing
    }, follow_redirects=True)

    with app.app_context():
        user = User.query.filter_by(email='maria@teste.com').first()
        assert user is not None
        assert user.name == 'Maria Silva'


def test_register_duplicate_email(client, user, app):
    """Não deve permitir cadastro com email já existente."""
    response = client.post('/auth/register', data={
        'name': 'Outro Nome',
        'email': 'joao@teste.com',  # Email já cadastrado
        'password': 'Senha@123',
        'confirm_password': 'Senha@123',
    })
    # Deve retornar o formulário com erro (não redirecionar)
    assert response.status_code == 200


def test_register_password_mismatch(client):
    """Senhas diferentes devem retornar erro de validação."""
    response = client.post('/auth/register', data={
        'name': 'Teste',
        'email': 'teste@email.com',
        'password': 'Senha@123',
        'confirm_password': 'SenhaDiferente',
    })
    assert response.status_code == 200


# -----------------------------------------------
# Testes de login
# -----------------------------------------------

def test_login_page_loads(client):
    """A página de login deve retornar status 200."""
    response = client.get('/auth/login')
    assert response.status_code == 200


def test_login_success(client, user):
    """Login com credenciais corretas deve redirecionar para a home."""
    response = client.post('/auth/login', data={
        'email': 'joao@teste.com',
        'password': 'Senha@123',
        'remember': False
    }, follow_redirects=True)
    assert response.status_code == 200


def test_login_wrong_password(client, user):
    """Login com senha errada deve mostrar mensagem de erro."""
    response = client.post('/auth/login', data={
        'email': 'joao@teste.com',
        'password': 'SenhaErrada',
    }, follow_redirects=True)
    assert b'incorretos' in response.data


def test_login_nonexistent_email(client):
    """Login com email não cadastrado deve mostrar mensagem de erro."""
    response = client.post('/auth/login', data={
        'email': 'naocadastrado@email.com',
        'password': 'qualquercoisa',
    }, follow_redirects=True)
    assert b'incorretos' in response.data


# -----------------------------------------------
# Testes de logout
# -----------------------------------------------

def test_logout_redirects(client, user):
    """Logout deve redirecionar para a home."""
    # Primeiro faz login
    client.post('/auth/login', data={
        'email': 'joao@teste.com',
        'password': 'Senha@123',
    })
    # Depois faz logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200


# TODO: Adicionar testes para recuperação de senha
# TODO: Adicionar testes para verificação de email
# TODO: Adicionar testes para usuário inativo tentando logar
