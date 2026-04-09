"""
models/photo.py — Model de Foto

Cada post de pet pode ter até 5 fotos.
Este model armazena os metadados de cada foto (nome do arquivo, URL).
O arquivo físico fica salvo em app/static/uploads/.
"""

from datetime import datetime
from app.extensions import db


class Photo(db.Model):
    """Model de foto associada a um post de pet."""

    __tablename__ = 'photos'

    # -----------------------------------------------
    # Colunas da tabela
    # -----------------------------------------------

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Nome do arquivo salvo em disco, ex: "a3f8b2c1-uuid.jpg"
    filename = db.Column(db.String(256), nullable=False)

    # URL para exibir a foto no HTML, ex: "/static/uploads/a3f8b2c1.jpg"
    url = db.Column(db.String(512), nullable=False)

    # Se True, é a foto de capa exibida no card do post
    is_primary = db.Column(db.Boolean, default=False, nullable=False)

    # Chave estrangeira — a qual post esta foto pertence
    post_id = db.Column(db.Integer, db.ForeignKey('pet_posts.id'), nullable=False)

    # Data de upload
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # -----------------------------------------------
    # Relacionamentos
    # -----------------------------------------------

    # Acesso ao post pai: photo.post retorna o objeto PetPost
    post = db.relationship('PetPost', back_populates='photos')

    def __repr__(self):
        return f'<Photo {self.filename} (post {self.post_id})>'

    # TODO: Armazenar fotos em serviço de nuvem (ex: AWS S3, Cloudflare R2)
    # TODO: Gerar thumbnails em múltiplos tamanhos automaticamente
    # TODO: Adicionar campo alt_text para acessibilidade
