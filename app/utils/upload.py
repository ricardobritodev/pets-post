import os
import uuid

from flask import current_app
from PIL import Image, UnidentifiedImageError

MAX_PIXELS = 20_000_000  # 20 MP — bloqueia decompression bombs


def allowed_file(filename: str) -> bool:
    """Verifica se a extensão do arquivo está na allowlist."""
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower()
        in current_app.config['ALLOWED_EXTENSIONS']
    )


def save_photo(file_storage) -> str:
    """
    Valida e salva uma imagem enviada pelo usuário.

    Proteções aplicadas:
    - Extensão verificada contra allowlist antes de chegar aqui
    - Image.verify() detecta arquivos corrompidos / não-imagens
    - Limite de pixels bloqueia decompression bombs
    - Pillow regenera o arquivo — o conteúdo original nunca é salvo
    - Nome gerado por UUID, sem relação com o filename do usuário

    Retorna o nome do arquivo salvo (ex: "a1b2c3...hex.jpg").
    Lança ValueError se o arquivo não for uma imagem válida ou for muito grande.
    """
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    filepath = os.path.join(upload_folder, filename)

    # Primeira passagem: verify() detecta dados corrompidos / não-imagem
    try:
        probe = Image.open(file_storage)
        probe.verify()
    except (UnidentifiedImageError, Exception) as exc:
        raise ValueError('Arquivo não é uma imagem válida.') from exc

    # verify() consome o stream — é preciso reabrir
    file_storage.seek(0)

    try:
        img = Image.open(file_storage)
    except Exception as exc:
        raise ValueError('Não foi possível abrir a imagem.') from exc

    # Bloqueia decompression bombs (ex: PNG 1×1 com IDAT gigante)
    if img.width * img.height > MAX_PIXELS:
        raise ValueError(
            f'Imagem muito grande: {img.width}×{img.height} px (máx. 20 MP).'
        )

    # Converte para RGB — elimina canal alfa e modo P (paleta)
    if img.mode in ('RGBA', 'P', 'LA'):
        img = img.convert('RGB')
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Redimensiona mantendo proporção — máx. 800 px de largura
    max_width = 800
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)

    # Pillow regenera o arquivo — o conteúdo original nunca toca o disco
    img.save(filepath, quality=85, optimize=True)

    return filename
