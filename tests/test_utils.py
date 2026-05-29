"""
tests/test_utils.py — Testes dos utilitários internos
"""

import pytest
from app.utils.phone import to_whatsapp_url


# ── Números válidos ────────────────────────────────────────────────────────────

def test_numero_com_mascara_completa():
    url = to_whatsapp_url('(11) 99999-9999')
    assert url == 'https://wa.me/5511999999999'


def test_numero_com_ddd_sem_mascara():
    url = to_whatsapp_url('11999999999')
    assert url == 'https://wa.me/5511999999999'


def test_numero_ja_com_codigo_pais():
    url = to_whatsapp_url('+55 11 99999-9999')
    assert url == 'https://wa.me/5511999999999'


def test_numero_com_55_sem_sinal():
    url = to_whatsapp_url('5511999999999')
    assert url == 'https://wa.me/5511999999999'


def test_numero_fixo_8_digitos_com_ddd():
    url = to_whatsapp_url('(11) 3333-4444')
    assert url == 'https://wa.me/551133334444'


def test_numero_movel_9_digitos_com_ddd():
    url = to_whatsapp_url('11 9 8888-7777')
    assert url == 'https://wa.me/5511988887777'


def test_numero_com_espacos_e_hifens():
    url = to_whatsapp_url('55 11 9 8765-4321')
    assert url == 'https://wa.me/5511987654321'


# ── Mensagem pré-preenchida ────────────────────────────────────────────────────

def test_url_sem_mensagem():
    url = to_whatsapp_url('11999999999')
    assert '?text=' not in url


def test_url_com_mensagem_inclui_text_param():
    url = to_whatsapp_url('11999999999', 'Olá!')
    assert '?text=' in url
    assert 'Ol%C3%A1' in url  # 'á' codificado como %C3%A1


def test_mensagem_com_emoji_e_asterisco():
    url = to_whatsapp_url('11999999999', 'Olá! *Pet perdido* 🐾')
    assert url is not None
    assert '?text=' in url


# ── Números inválidos → retornam None ─────────────────────────────────────────

def test_0800_retorna_none():
    assert to_whatsapp_url('0800 123 4567') is None


def test_0300_retorna_none():
    assert to_whatsapp_url('0300 123 456') is None


def test_numero_sem_ddd_retorna_none():
    assert to_whatsapp_url('99999-9999') is None


def test_string_vazia_retorna_none():
    assert to_whatsapp_url('') is None


def test_none_retorna_none():
    assert to_whatsapp_url(None) is None


def test_apenas_letras_retorna_none():
    assert to_whatsapp_url('sem numero') is None


def test_numero_curto_demais_retorna_none():
    assert to_whatsapp_url('1234') is None
