import re
from urllib.parse import quote


def to_whatsapp_url(phone: str, message: str = '') -> str | None:
    """
    Converte um número de telefone brasileiro para uma URL wa.me pronta para uso.

    Sanitiza qualquer formato comum de entrada:
        (11) 99999-9999  →  https://wa.me/5511999999999?text=...
        +55 11 98888-7777 →  https://wa.me/5511988887777?text=...
        11 9 9999-9999    →  https://wa.me/5511999999999?text=...

    Retorna None se o número for inválido ou não aplicável ao WhatsApp
    (ex: 0800, string vazia, menos de 8 dígitos).
    """
    if not phone:
        return None

    digits = re.sub(r'\D', '', phone)

    # Números 0800 / 0300 / 0500 não funcionam no WhatsApp
    if digits.startswith('0'):
        return None

    # Remove o código do país se já veio com 55 + DDD (12-13 dígitos)
    if digits.startswith('55') and len(digits) in (12, 13):
        pass  # já está no formato correto
    elif len(digits) in (10, 11):
        # Número brasileiro sem código de país — adiciona 55
        digits = '55' + digits
    elif len(digits) == 8 or len(digits) == 9:
        # Número sem DDD — não há como determinar a área correta
        return None
    else:
        return None

    if not message:
        return f'https://wa.me/{digits}'

    return f'https://wa.me/{digits}?text={quote(message)}'
