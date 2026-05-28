from flask import Blueprint, render_template, jsonify
from app.models.partner import Partner

map_bp = Blueprint('map', __name__)


@map_bp.route('/mapa')
def index():
    return render_template('map/index.html', title='Mapa de Parceiros')


@map_bp.route('/api/parceiros')
def api_partners():
    partners = (
        Partner.query
        .filter_by(is_active=True)
        .filter(Partner.lat.isnot(None))
        .all()
    )
    return jsonify([p.to_dict() for p in partners])
