from datetime import datetime
from app.extensions import db


class AdoptionPost(db.Model):
    __tablename__ = 'adoption_posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    pet_name = db.Column(db.String(100), nullable=True)
    pet_type = db.Column(
        db.Enum('dog', 'cat', 'bird', 'other', name='adoption_pet_type'),
        nullable=False
    )
    pet_breed = db.Column(db.String(100), nullable=True)
    pet_color = db.Column(db.String(100), nullable=True)
    pet_size = db.Column(
        db.Enum('small', 'medium', 'large', name='adoption_pet_size'),
        nullable=True
    )

    is_neutered = db.Column(db.Boolean, default=False, nullable=False)
    is_vaccinated = db.Column(db.Boolean, default=False, nullable=False)

    # Requisitos que o adotante deve atender (texto livre)
    adopter_requirements = db.Column(db.Text, nullable=True)

    location = db.Column(db.String(255), nullable=False)
    location_lat = db.Column(db.Float, nullable=True)
    location_lng = db.Column(db.Float, nullable=True)

    contact_phone = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(120), nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_adopted = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='adoption_posts')
    photos = db.relationship(
        'AdoptionPhoto',
        back_populates='adoption_post',
        cascade='all, delete-orphan',
        lazy='select'
    )

    @property
    def primary_photo(self):
        for photo in self.photos:
            if photo.is_primary:
                return photo
        return self.photos[0] if self.photos else None

    @property
    def pet_type_label(self):
        return {'dog': 'Cachorro', 'cat': 'Gato', 'bird': 'Pássaro', 'other': 'Outro'}.get(self.pet_type, self.pet_type)

    @property
    def pet_size_label(self):
        return {'small': 'Pequeno', 'medium': 'Médio', 'large': 'Grande'}.get(self.pet_size, '') if self.pet_size else ''

    def __repr__(self):
        return f'<AdoptionPost {self.id}: {self.title}>'
