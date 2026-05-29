"""
services/geocoding.py — Geocodificação de endereços via Nominatim (OpenStreetMap)

Converte um texto de endereço (ex: "Parque Ibirapuera, São Paulo")
em coordenadas geográficas (latitude, longitude).

Por que server-side:
  - A URL da API nunca é exposta ao browser
  - Timeout e erros são tratados silenciosamente no servidor
  - Nominatim exige User-Agent identificado — controlado aqui

Termos de uso do Nominatim:
  - User-Agent obrigatório (identificado abaixo)
  - Máximo de 1 requisição por segundo
  - Sem uso comercial pesado — adequado para projeto acadêmico
  - https://operations.osmfoundation.org/policies/nominatim/
"""

import json
import urllib.parse
import urllib.request

_NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'
_USER_AGENT = 'PetsPost/1.0 (projeto-academico; contato: admin@petspost.com)'
_TIMEOUT_S = 5


def geocode_address(address: str) -> tuple[float | None, float | None]:
    """
    Retorna (latitude, longitude) para o endereço informado.
    Retorna (None, None) se a geocodificação falhar por qualquer motivo.

    Parâmetros:
        address: string de endereço livre (ex: "Rua das Flores, Curitiba/PR")
    """
    if not address or not address.strip():
        return None, None

    params = urllib.parse.urlencode({
        'q': address.strip(),
        'format': 'json',
        'limit': 1,
        'countrycodes': 'br',       # Restringe ao Brasil
        'addressdetails': 0,
    })

    req = urllib.request.Request(
        f'{_NOMINATIM_URL}?{params}',
        headers={'User-Agent': _USER_AGENT},
    )

    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        # Falha silenciosa — o post é salvo normalmente sem coordenadas
        pass

    return None, None
