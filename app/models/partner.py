from datetime import datetime
from app.extensions import db


class Partner(db.Model):
    __tablename__ = 'partners'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    partner_type = db.Column(
        db.Enum('foster_home', 'petshop', 'vet_clinic', name='partner_type'),
        nullable=False
    )
    address = db.Column(db.String(255), nullable=False)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def type_label(self):
        return {
            'foster_home': 'Lar Temporário',
            'petshop': 'Petshop Parceiro',
            'vet_clinic': 'Clínica Veterinária',
        }.get(self.partner_type, self.partner_type)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.partner_type,
            'type_label': self.type_label,
            'address': self.address,
            'lat': self.lat,
            'lng': self.lng,
            'phone': self.phone or '',
            'email': self.email or '',
            'website': self.website or '',
        }

    def __repr__(self):
        return f'<Partner {self.id}: {self.name}>'
