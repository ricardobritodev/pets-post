"""
tests/test_api.py — Testes do endpoint de lookup de CEP

Roda sem conexão real com o ViaCEP: urllib.request.urlopen é mockado.
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# Resposta completa do ViaCEP — inclui campos que NÃO devem vazar na resposta
_VIACEP_FULL = {
    'cep': '01310-100',
    'logradouro': 'Avenida Paulista',
    'complemento': 'de 610 a 1510 - lado par',
    'bairro': 'Bela Vista',
    'localidade': 'São Paulo',
    'uf': 'SP',
    'ibge': '3550308',
    'gia': '1004',
    'ddd': '11',
    'siafi': '7107',
}


def _mock_urlopen(payload, status=200):
    """Cria mock do urllib.request.urlopen com resposta JSON."""
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(payload).encode('utf-8')
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    return mock_response


# --- Casos de sucesso ---

def test_valid_cep_returns_200(client):
    with patch('urllib.request.urlopen', return_value=_mock_urlopen(_VIACEP_FULL)):
        res = client.get('/api/cep/01310100')
    assert res.status_code == 200
    data = res.get_json()
    assert data['logradouro'] == 'Avenida Paulista'
    assert data['bairro'] == 'Bela Vista'
    assert data['localidade'] == 'São Paulo'
    assert data['uf'] == 'SP'


def test_response_whitelist_excludes_extra_fields(client):
    """Campos como ibge, ddd, siafi não devem aparecer na resposta."""
    with patch('urllib.request.urlopen', return_value=_mock_urlopen(_VIACEP_FULL)):
        res = client.get('/api/cep/01310100')
    data = res.get_json()
    for field in ('ibge', 'gia', 'ddd', 'siafi', 'complemento', 'cep'):
        assert field not in data, f"Campo '{field}' não deveria estar na resposta"


def test_cep_with_mask_is_sanitized(client):
    """CEP com hífen (01310-100) deve ser aceito e sanitizado server-side."""
    with patch('urllib.request.urlopen', return_value=_mock_urlopen(_VIACEP_FULL)):
        res = client.get('/api/cep/01310-100')
    assert res.status_code == 200



# --- Casos de erro de formato ---

def test_letters_in_cep_returns_400(client):
    res = client.get('/api/cep/abcdefgh')
    assert res.status_code == 400
    assert 'erro' in res.get_json()


def test_short_cep_returns_400(client):
    res = client.get('/api/cep/0131010')  # 7 dígitos
    assert res.status_code == 400


def test_long_cep_returns_400(client):
    res = client.get('/api/cep/013101001')  # 9 dígitos
    assert res.status_code == 400


# --- CEP inexistente ---

def test_nonexistent_cep_returns_404(client):
    with patch('urllib.request.urlopen', return_value=_mock_urlopen({'erro': True})):
        res = client.get('/api/cep/00000000')
    assert res.status_code == 404
    assert 'erro' in res.get_json()


# --- Falha no serviço externo ---

def test_viacep_unavailable_returns_502(client):
    with patch('urllib.request.urlopen', side_effect=Exception('connection refused')):
        res = client.get('/api/cep/01310100')
    assert res.status_code == 502
    assert 'erro' in res.get_json()


def test_viacep_timeout_returns_502(client):
    import urllib.error
    with patch('urllib.request.urlopen', side_effect=TimeoutError('timed out')):
        res = client.get('/api/cep/01310100')
    assert res.status_code == 502
