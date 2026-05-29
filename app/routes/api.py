import re
import json
import urllib.request

from flask import Blueprint, jsonify

from app.extensions import limiter

api_bp = Blueprint('api', __name__, url_prefix='/api')

_CEP_RE = re.compile(r'^\d{8}$')
_VIACEP_URL = 'https://viacep.com.br/ws/{}/json/'
_ALLOWED_FIELDS = ('logradouro', 'bairro', 'localidade', 'uf')


@api_bp.route('/cep/<cep>')
@limiter.limit("30 per minute")
def lookup_cep(cep):
    clean = re.sub(r'\D', '', cep)
    if not _CEP_RE.match(clean):
        return jsonify({'erro': 'Formato de CEP inválido'}), 400

    req = urllib.request.Request(
        _VIACEP_URL.format(clean),
        headers={'User-Agent': 'PetsPost/1.0 (projeto-academico)'},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception:
        return jsonify({'erro': 'Serviço de CEP indisponível'}), 502

    if data.get('erro'):
        return jsonify({'erro': 'CEP não encontrado'}), 404

    return jsonify({field: data.get(field, '') for field in _ALLOWED_FIELDS})
