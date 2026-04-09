"""
models/pet_post.py — Model de Post de Pet

Representa a tabela 'pet_posts' no banco de dados.
Cada post é um anúncio de um pet perdido ou encontrado.
"""

from datetime import datetime
from app.extensions import db


class PetPost(db.Model):
    """Model de post de pet perdido ou encontrado."""

    __tablename__ = 'pet_posts'

    # -----------------------------------------------
    # Colunas da tabela
    # -----------------------------------------------

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Título do anúncio, ex: "Cachorro encontrado no Parque Ibirapuera"
    title = db.Column(db.String(150), nullable=False)

    # Descrição detalhada do pet e da situação
    description = db.Column(db.Text, nullable=False)

    # Status: 'lost' = pet perdido (dono procura), 'found' = pet encontrado (alguém achou)
    status = db.Column(
        db.Enum('lost', 'found', name='post_status'),
        default='lost',
        nullable=False
    )

    # Nome do pet (opcional — nem sempre se sabe)
    pet_name = db.Column(db.String(100), nullable=True)

    # Tipo de animal
    pet_type = db.Column(
        db.Enum('dog', 'cat', 'bird', 'other', name='pet_type'),
        nullable=False
    )

    # Raça do animal (opcional)
    pet_breed = db.Column(db.String(100), nullable=True)

    # Cor ou padrão de cores do pet
    pet_color = db.Column(db.String(100), nullable=True)

    # Porte do animal
    pet_size = db.Column(
        db.Enum('small', 'medium', 'large', name='pet_size'),
        nullable=True
    )

    # Endereço ou região onde foi visto pela última vez
    last_seen_location = db.Column(db.String(255), nullable=False)

    # Coordenadas geográficas — para uso futuro com Google Maps
    last_seen_lat = db.Column(db.Float, nullable=True)
    last_seen_lng = db.Column(db.Float, nullable=True)

    # Contato de quem criou o post
    contact_phone = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(120), nullable=True)

    # Recompensa oferecida (opcional), ex: "R$ 200"
    reward = db.Column(db.String(100), nullable=True)

    # Se False, o post foi desativado/removido da listagem pública
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Se True, o pet foi encontrado/reunido com o dono — post encerrado
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)

    # Datas automáticas
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Chave estrangeira — referência ao usuário que criou o post
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # -----------------------------------------------
    # Relacionamentos
    # -----------------------------------------------

    # Acesso ao usuário dono do post: post.user retorna o objeto User
    user = db.relationship('User', back_populates='posts')

    # Um post pode ter várias fotos (one-to-many)
    # cascade='all, delete-orphan' deleta as fotos quando o post é deletado
    photos = db.relationship(
        'Photo',
        back_populates='post',
        cascade='all, delete-orphan',
        lazy='select'
    )

    # -----------------------------------------------
    # Propriedades auxiliares
    # -----------------------------------------------

    @property
    def primary_photo(self):
        """Retorna a foto principal do post, ou None se não houver fotos."""
        for photo in self.photos:
            if photo.is_primary:
                return photo
        # Se nenhuma está marcada como principal, retorna a primeira
        return self.photos[0] if self.photos else None

    @property
    def status_label(self):
        """Retorna o rótulo legível do status em português."""
        labels = {'lost': 'Perdido', 'found': 'Encontrado'}
        return labels.get(self.status, self.status)

    @property
    def pet_type_label(self):
        """Retorna o rótulo legível do tipo de pet em português."""
        labels = {'dog': 'Cachorro', 'cat': 'Gato', 'bird': 'Pássaro', 'other': 'Outro'}
        return labels.get(self.pet_type, self.pet_type)

    @property
    def pet_size_label(self):
        """Retorna o rótulo legível do porte em português."""
        labels = {'small': 'Pequeno', 'medium': 'Médio', 'large': 'Grande'}
        return labels.get(self.pet_size, '') if self.pet_size else ''

    def __repr__(self):
        return f'<PetPost {self.id}: {self.title}>'

    # TODO: Integrar Google Maps API para geocodificar last_seen_location automaticamente
    # TODO: Módulo de Adoção — criar model Adoption relacionado a PetPost
    # TODO: Módulo de Lares Temporários — criar model FosterHome
    # TODO: Implementar sistema de tags para facilitar busca
    # TODO: Adicionar campo de visualizações (view_count) para estatísticas
