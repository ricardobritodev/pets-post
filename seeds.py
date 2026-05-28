"""
seeds.py — Script para popular o banco com dados de exemplo

Execute após criar as tabelas:
    python seeds.py

O que este script faz:
  1. Cria o usuário admin padrão
  2. Cria alguns usuários comuns
  3. Cria posts de exemplo de pets perdidos e encontrados

⚠️  ATENÇÃO: Execute este script apenas em desenvolvimento!
    Não rode em produção — ele cria dados fictícios e pode sobrescrever dados reais.
"""

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.pet_post import PetPost

# Cria o app em modo de desenvolvimento
app = create_app('development')


def seed_users():
    """Cria usuários de exemplo."""
    print('👤 Criando usuários...')

    usuarios = [
        {
            'name': 'Admin PetPost',
            'email': 'admin@petpost.com',
            'password': 'Admin@123',
            'role': 'admin',
            'phone': '(11) 91234-5678',
        },
        {
            'name': 'Maria Silva',
            'email': 'maria@exemplo.com',
            'password': 'Senha@123',
            'phone': '(11) 98765-4321',
        },
        {
            'name': 'Carlos Santos',
            'email': 'carlos@exemplo.com',
            'password': 'Senha@123',
            'phone': '(21) 99111-2222',
        },
        {
            'name': 'Ana Ferreira',
            'email': 'ana@exemplo.com',
            'password': 'Senha@123',
            'phone': '(31) 97654-3210',
        },
    ]

    criados = []
    for dados in usuarios:
        # Verifica se já existe para não duplicar
        if User.query.filter_by(email=dados['email']).first():
            print(f'  ⏭️  Usuário {dados["email"]} já existe, pulando...')
            continue

        user = User(
            name=dados['name'],
            email=dados['email'],
            role=dados.get('role', 'user'),
            phone=dados.get('phone')
        )
        user.set_password(dados['password'])
        db.session.add(user)
        criados.append(dados['name'])

    db.session.commit()

    for nome in criados:
        print(f'  ✅ Usuário "{nome}" criado')

    return User.query.all()


def seed_posts(users):
    """Cria posts de exemplo."""
    print('\n📋 Criando posts de exemplo...')

    # Pega usuários para associar aos posts
    maria = User.query.filter_by(email='maria@exemplo.com').first()
    carlos = User.query.filter_by(email='carlos@exemplo.com').first()
    ana = User.query.filter_by(email='ana@exemplo.com').first()

    if not all([maria, carlos, ana]):
        print('  ⚠️  Usuários não encontrados. Execute seed_users() primeiro.')
        return

    posts_data = [
        {
            'title': 'Cachorro caramelo perdido no Parque Ibirapuera',
            'description': 'Meu cachorro fugiu durante o passeio no domingo. Ele é muito dócil e obedece quando chamado pelo nome "Rex". Tem uma mancha branca no pescoço.',
            'status': 'lost',
            'pet_name': 'Rex',
            'pet_type': 'dog',
            'pet_breed': 'Vira-lata',
            'pet_color': 'Caramelo com mancha branca no pescoço',
            'pet_size': 'medium',
            'last_seen_location': 'Parque Ibirapuera, São Paulo, SP',
            'contact_phone': '(11) 98765-4321',
            'contact_email': 'maria@exemplo.com',
            'reward': 'R$ 300,00 de recompensa',
            'user_id': maria.id,
        },
        {
            'title': 'Gato preto e branco encontrado no Jardim América',
            'description': 'Encontrei este gato meando muito na calçada. Parece bem cuidado, tem coleira mas sem identificação. Está guardado na minha casa.',
            'status': 'found',
            'pet_name': None,
            'pet_type': 'cat',
            'pet_breed': 'SRD (vira-lata)',
            'pet_color': 'Preto e branco',
            'pet_size': 'small',
            'last_seen_location': 'Jardim América, São Paulo, SP',
            'contact_phone': '(11) 98765-4321',
            'contact_email': 'maria@exemplo.com',
            'user_id': maria.id,
        },
        {
            'title': 'Golden Retriever perdido em Copacabana',
            'description': 'Nossa Golden Retriever fêmea se perdeu durante a caminhada da manhã. Ela usa uma coleira azul com plaquinha. É muito carinhosa com estranhos.',
            'status': 'lost',
            'pet_name': 'Mel',
            'pet_type': 'dog',
            'pet_breed': 'Golden Retriever',
            'pet_color': 'Dourada',
            'pet_size': 'large',
            'last_seen_location': 'Copacabana, Rio de Janeiro, RJ',
            'contact_phone': '(21) 99111-2222',
            'contact_email': 'carlos@exemplo.com',
            'reward': 'R$ 500,00 de recompensa',
            'user_id': carlos.id,
        },
        {
            'title': 'Papagaio verde encontrado no bairro Savassi',
            'description': 'Um papagaio pousou na minha varanda e não foi embora. Sabe falar algumas palavras. Está bem alimentado e parece ser de estimação.',
            'status': 'found',
            'pet_name': None,
            'pet_type': 'bird',
            'pet_breed': 'Papagaio',
            'pet_color': 'Verde com cabeça amarela',
            'pet_size': None,
            'last_seen_location': 'Savassi, Belo Horizonte, MG',
            'contact_phone': '(31) 97654-3210',
            'contact_email': 'ana@exemplo.com',
            'user_id': ana.id,
        },
        {
            'title': 'Gato siamês perdido no Centro de Curitiba',
            'description': 'Meu gato siamês escapou pela janela. Olhos azuis, muito assustado. Responde pelo nome "Simba". Por favor, não tente pegá-lo na força.',
            'status': 'lost',
            'pet_name': 'Simba',
            'pet_type': 'cat',
            'pet_breed': 'Siamês',
            'pet_color': 'Bege com pontas escuras',
            'pet_size': 'small',
            'last_seen_location': 'Praça Osório, Curitiba, PR',
            'contact_phone': '(41) 98888-7777',
            'user_id': ana.id,
        },
    ]

    for dados in posts_data:
        # Verifica se já existe um post com o mesmo título
        if PetPost.query.filter_by(title=dados['title']).first():
            print(f'  ⏭️  Post "{dados["title"][:40]}..." já existe, pulando...')
            continue

        post = PetPost(**dados)
        db.session.add(post)
        print(f'  ✅ Post "{dados["title"][:40]}..." criado')

    db.session.commit()


def main():
    """Função principal que executa todos os seeds."""
    print('🌱 Iniciando seeds do PetPost...\n')

    with app.app_context():
        users = seed_users()
        seed_posts(users)

    print('\n✨ Seeds concluídos com sucesso!')
    print('\n📋 Credenciais do admin:')
    print('   Email: admin@petpost.com')
    print('   Senha: Admin@123')
    print('\n⚠️  Lembre-se de trocar a senha do admin em produção!')


if __name__ == '__main__':
    main()
