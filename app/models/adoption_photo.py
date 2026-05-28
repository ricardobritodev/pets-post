from datetime import datetime
from app.extensions import db


class AdoptionPhoto(db.Model):
    __tablename__ = 'adoption_photos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    adoption_post_id = db.Column(db.Integer, db.ForeignKey('adoption_posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    adoption_post = db.relationship('AdoptionPost', back_populates='photos')

    def __repr__(self):
        return f'<AdoptionPhoto {self.filename} (adoption {self.adoption_post_id})>'
