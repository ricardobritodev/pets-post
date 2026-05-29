"""
run.py — Ponto de entrada da aplicação PetPost

Execute este arquivo para iniciar o servidor de desenvolvimento:
    python run.py

Ou use o Flask CLI:
    flask run
"""

from app import create_app
from app.extensions import db

# Cria a instância da aplicação usando o padrão Application Factory
app = create_app()


@app.cli.command('create-db')
def create_db():
    """
    Cria todas as tabelas no banco de dados diretamente.

    Use este comando quando flask db upgrade não funcionar:
        flask create-db
    """
    with app.app_context():
        db.create_all()
        print('✅ Tabelas criadas com sucesso!')
        print('   Agora rode: python seeds.py')


@app.cli.command('geocode-posts')
def geocode_posts():
    """
    Geocodifica posts que ainda não têm lat/lng armazenados.

    Use após habilitar a feature de mapa para cobrir posts já existentes:
        flask geocode-posts

    Respeita o rate limit de 1 req/s do Nominatim.
    """
    import time
    from app.models.pet_post import PetPost
    from app.services.geocoding import geocode_address

    with app.app_context():
        posts = PetPost.query.filter(PetPost.last_seen_lat.is_(None)).all()

        if not posts:
            print('Nenhum post sem coordenadas encontrado.')
            return

        print(f'Geocodificando {len(posts)} post(s)...')

        for post in posts:
            lat, lng = geocode_address(post.last_seen_location)
            if lat and lng:
                post.last_seen_lat = lat
                post.last_seen_lng = lng
                db.session.commit()
                print(f'  ✓ Post {post.id}: ({lat:.5f}, {lng:.5f}) — {post.last_seen_location[:50]}')
            else:
                print(f'  ✗ Post {post.id}: endereço não encontrado — {post.last_seen_location[:50]}')

            time.sleep(1.1)  # Respeita o limite de 1 req/s do Nominatim

        print('Concluído!')


@app.cli.command('geocode-adoption')
def geocode_adoption():
    """
    Geocodifica posts de adoção que ainda não têm lat/lng armazenados.

        flask geocode-adoption
    """
    import time
    from app.models.adoption_post import AdoptionPost
    from app.services.geocoding import geocode_address

    with app.app_context():
        posts = AdoptionPost.query.filter(AdoptionPost.location_lat.is_(None)).all()

        if not posts:
            print('Nenhum post de adoção sem coordenadas encontrado.')
            return

        print(f'Geocodificando {len(posts)} post(s) de adoção...')

        for post in posts:
            lat, lng = geocode_address(post.location)
            if lat and lng:
                post.location_lat = lat
                post.location_lng = lng
                db.session.commit()
                print(f'  ✓ Post {post.id}: ({lat:.5f}, {lng:.5f}) — {post.location[:50]}')
            else:
                print(f'  ✗ Post {post.id}: endereço não encontrado — {post.location[:50]}')

            time.sleep(1.1)

        print('Concluído!')


@app.cli.command('geocode-partners')
def geocode_partners():
    """Geocodifica parceiros que ainda não têm coordenadas: flask geocode-partners"""
    import time
    from app.models.partner import Partner
    from app.services.geocoding import geocode_address

    with app.app_context():
        partners = Partner.query.filter(Partner.lat.is_(None)).all()

        if not partners:
            print('Nenhum parceiro sem coordenadas encontrado.')
            return

        print(f'Geocodificando {len(partners)} parceiro(s)...')
        for partner in partners:
            lat, lng = geocode_address(partner.address)
            if lat and lng:
                partner.lat = lat
                partner.lng = lng
                db.session.commit()
                print(f'  ✓ {partner.name}: ({lat:.5f}, {lng:.5f})')
            else:
                print(f'  ✗ {partner.name}: endereço não encontrado — {partner.address}')
            time.sleep(1.1)

        print('Concluído!')


if __name__ == '__main__':
    # debug só ativa em desenvolvimento — nunca em produção
    import os
    is_dev = os.environ.get('FLASK_CONFIG', 'development') == 'development'
    app.run(debug=is_dev)
