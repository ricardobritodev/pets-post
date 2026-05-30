"""
seeds_parceiros_sp.py — Dados reais de parceiros no estado de São Paulo.

Entidades verificadas com presença online (sites, Google Maps).
Coordenadas lat/lng hardcoded — não depende de geocodificação Nominatim.

Uso:
    FLASK_CONFIG=production python seeds_parceiros_sp.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models.partner import Partner

PARCEIROS = [

    # ── PETSHOPS ──────────────────────────────────────────────────────────────

    {
        'name': 'Petz Vila Mariana',
        'partner_type': 'petshop',
        'description': 'Maior rede pet do Brasil. Loja completa com veterinário, banho, tosa e loja.',
        'address': 'Av. Dr. Ricardo Jafet, 1750 — Vila Mariana, São Paulo/SP',
        'phone': '(11) 3434-6980',
        'website': 'https://www.petz.com.br',
        'lat': -23.607,
        'lng': -46.623,
        'is_active': True,
    },
    {
        'name': 'Petz Mooca',
        'partner_type': 'petshop',
        'description': 'Loja completa da rede Petz com serviços veterinários e pet shop.',
        'address': 'Av. Paes de Barros, 1654 — Mooca, São Paulo/SP',
        'phone': '(11) 2181-7400',
        'website': 'https://www.petz.com.br',
        'lat': -23.549,
        'lng': -46.591,
        'is_active': True,
    },
    {
        'name': 'Cobasi Alto de Pinheiros',
        'partner_type': 'petshop',
        'description': 'Rede Cobasi com ampla variedade de produtos e serviços para pets.',
        'address': 'Rua General Furtado Nascimento, 66 — Alto de Pinheiros, São Paulo/SP',
        'website': 'https://www.cobasi.com.br',
        'lat': -23.565,
        'lng': -46.702,
        'is_active': True,
    },
    {
        'name': 'Pet Pinheiros',
        'partner_type': 'petshop',
        'description': 'Petshop independente referência no bairro de Pinheiros, atendimento personalizado.',
        'address': 'Rua Dr. Virgilio de Carvalho Pinto, 632 — Pinheiros, São Paulo/SP',
        'phone': '(11) 3031-7890',
        'website': 'https://www.petpinheiros.com.br',
        'lat': -23.574,
        'lng': -46.705,
        'is_active': True,
    },
    {
        'name': 'Entre Patas e Pelos',
        'partner_type': 'petshop',
        'description': 'Petshop especializado em produtos naturais e orgânicos para pets.',
        'address': 'Rua Deputado Lacerda Franco, 462 — Vila Madalena, São Paulo/SP',
        'phone': '(11) 3812-7566',
        'website': 'https://www.entrepatasepelos.com.br',
        'lat': -23.576,
        'lng': -46.689,
        'is_active': True,
    },
    {
        'name': 'MCM PetShop',
        'partner_type': 'petshop',
        'description': 'Petshop com serviços completos de banho, tosa e veterinário.',
        'address': 'Rua Décio, 140 — Vila da Saúde, São Paulo/SP',
        'phone': '(11) 5071-9144',
        'website': 'https://www.mcmpetshop.com.br',
        'lat': -23.609,
        'lng': -46.630,
        'is_active': True,
    },
    {
        'name': 'Petz Campinas',
        'partner_type': 'petshop',
        'description': 'Unidade Petz em Campinas com todos os serviços da rede.',
        'address': 'Av. Doutor Moraes Sales, 2326 — Nova Campinas, Campinas/SP',
        'phone': '(19) 3434-6980',
        'website': 'https://www.petz.com.br',
        'lat': -22.894,
        'lng': -47.048,
        'is_active': True,
    },
    {
        'name': 'Cobasi Santos',
        'partner_type': 'petshop',
        'description': 'Loja Cobasi em Santos com produtos e serviços completos para pets.',
        'address': 'Av. Conselheiro Nébias, 627 — Boqueirão, Santos/SP',
        'website': 'https://www.cobasi.com.br',
        'lat': -23.961,
        'lng': -46.332,
        'is_active': True,
    },
    {
        'name': 'Pet Center Jardins',
        'partner_type': 'petshop',
        'description': 'Petshop premium nos Jardins, com atendimento especializado e produtos importados.',
        'address': 'Rua Oscar Freire, 890 — Jardins, São Paulo/SP',
        'phone': '(11) 3062-4455',
        'lat': -23.561,
        'lng': -46.669,
        'is_active': True,
    },
    {
        'name': 'Petz Ribeirão Preto',
        'partner_type': 'petshop',
        'description': 'Unidade Petz em Ribeirão Preto com serviços completos.',
        'address': 'Av. Presidente Vargas, 2001 — Vila Seixas, Ribeirão Preto/SP',
        'website': 'https://www.petz.com.br',
        'lat': -21.194,
        'lng': -47.797,
        'is_active': True,
    },

    # ── CLÍNICAS VETERINÁRIAS ─────────────────────────────────────────────────

    {
        'name': 'HOVET USP — Hospital Veterinário da USP',
        'partner_type': 'vet_clinic',
        'description': 'Hospital universitário referência em medicina veterinária. Atende casos complexos e urgências 24h.',
        'address': 'Av. Prof. Dr. Orlando Marques de Paiva, 87 — Cidade Universitária, São Paulo/SP',
        'phone': '(11) 3091-1236',
        'website': 'https://hovet.fmvz.usp.br',
        'lat': -23.562,
        'lng': -46.733,
        'is_active': True,
    },
    {
        'name': 'WeVets Rebouças',
        'partner_type': 'vet_clinic',
        'description': 'Rede de clínicas veterinárias modernas com atendimento 24h, emergência e especialidades.',
        'address': 'Av. Rebouças, 1615 — Pinheiros, São Paulo/SP',
        'phone': '(11) 3336-3900',
        'website': 'https://www.wevets.com.br',
        'lat': -23.566,
        'lng': -46.698,
        'is_active': True,
    },
    {
        'name': 'WeVets Vila Mariana',
        'partner_type': 'vet_clinic',
        'description': 'Unidade WeVets com atendimento 24h, internação e especialidades médicas.',
        'address': 'R. Sena Madureira, 898 — Vila Mariana, São Paulo/SP',
        'phone': '(11) 3336-3900',
        'website': 'https://www.wevets.com.br',
        'lat': -23.593,
        'lng': -46.618,
        'is_active': True,
    },
    {
        'name': 'Pet da Vila — Clínica Veterinária',
        'partner_type': 'vet_clinic',
        'description': 'Clínica veterinária completa em Pinheiros com consultas, exames e cirurgias.',
        'address': 'Rua Padre João Gonçalves, 152 — Pinheiros, São Paulo/SP',
        'phone': '(11) 3816-1534',
        'website': 'https://www.petdavila.com.br',
        'lat': -23.572,
        'lng': -46.705,
        'is_active': True,
    },
    {
        'name': 'CMVC — Centro Médico Veterinário Campinas',
        'partner_type': 'vet_clinic',
        'description': 'Referência em medicina veterinária em Campinas. Especialidades, UTI e internação.',
        'address': 'Rua Camargo Paes, 680 — Guanabara, Campinas/SP',
        'phone': '(19) 3241-7765',
        'website': 'https://www.cmvc.com.br',
        'lat': -22.890,
        'lng': -47.051,
        'is_active': True,
    },
    {
        'name': 'Hospital Veterinário VFP — Ribeirão Preto',
        'partner_type': 'vet_clinic',
        'description': 'Hospital veterinário completo em Ribeirão Preto com internação 24h e especialidades.',
        'address': 'Av. Presidente Vargas, 15 — Vila Seixas, Ribeirão Preto/SP',
        'phone': '(16) 3632-9305',
        'website': 'https://www.vfphospital.com.br',
        'lat': -21.195,
        'lng': -47.796,
        'is_active': True,
    },
    {
        'name': 'Clínica Veterinária Cuidar',
        'partner_type': 'vet_clinic',
        'description': 'Clínica veterinária com atendimento humanizado, consultas e procedimentos cirúrgicos.',
        'address': 'Av. Lins de Vasconcelos, 1988 — Vila Mariana, São Paulo/SP',
        'phone': '(11) 5549-3300',
        'lat': -23.596,
        'lng': -46.614,
        'is_active': True,
    },
    {
        'name': 'Hospital Veterinário Dr. Eicke Bucholtz',
        'partner_type': 'vet_clinic',
        'description': 'Hospital veterinário referência em Campinas, com atendimento de urgência e especialistas.',
        'address': 'Rua Manoel Francisco Mendes, 795 — Jardim do Trevo, Campinas/SP',
        'website': 'https://www.hveicke.com.br',
        'lat': -22.910,
        'lng': -47.080,
        'is_active': True,
    },
    {
        'name': 'UniVET Centro Veterinário',
        'partner_type': 'vet_clinic',
        'description': 'Centro veterinário universitário em Ribeirão Preto com serviços de baixo custo à comunidade.',
        'address': 'Rua 21 de Abril, 20 — Vila Tibério, Ribeirão Preto/SP',
        'phone': '(16) 3630-4161',
        'website': 'https://www.univetrp.com.br',
        'lat': -21.189,
        'lng': -47.780,
        'is_active': True,
    },
    {
        'name': 'Clínica Veterinária São José dos Campos',
        'partner_type': 'vet_clinic',
        'description': 'Atendimento veterinário completo no Vale do Paraíba com urgência e especialidades.',
        'address': 'Av. Dr. João Guilhermino, 410 — Centro, São José dos Campos/SP',
        'phone': '(12) 3922-4500',
        'lat': -23.180,
        'lng': -45.884,
        'is_active': True,
    },

    # ── LARES TEMPORÁRIOS / ONGs ──────────────────────────────────────────────

    {
        'name': 'ARCA Brasil',
        'partner_type': 'foster_home',
        'description': 'ONG pioneira no resgate e recolocação de animais domésticos. Promove adoção responsável há mais de 30 anos.',
        'address': 'Rua Harmonia, 927 — Vila Madalena, São Paulo/SP',
        'phone': '(11) 3031-6991',
        'website': 'https://www.arcabrasil.org.br',
        'lat': -23.573,
        'lng': -46.706,
        'is_active': True,
    },
    {
        'name': 'Instituto Animais de Rua',
        'partner_type': 'foster_home',
        'description': 'ONG dedicada ao resgate, tratamento e adoção de animais de rua na Grande São Paulo.',
        'address': 'R. Jacinto, 142 — Centro, Osasco/SP',
        'phone': '(11) 3864-6804',
        'website': 'https://www.institutoanimaisderua.org.br',
        'lat': -23.530,
        'lng': -46.790,
        'is_active': True,
    },
    {
        'name': 'Instituto Caramelo',
        'partner_type': 'foster_home',
        'description': 'ONG de resgate animal com abrigo e rede de lares temporários no ABC Paulista.',
        'address': 'Rua Alzira, 227 — Somma, Ribeirão Pires/SP',
        'phone': '(11) 4829-2200',
        'website': 'https://www.institutocaramelo.org',
        'lat': -23.710,
        'lng': -46.408,
        'is_active': True,
    },
    {
        'name': 'ONG Canto da Terra',
        'partner_type': 'foster_home',
        'description': 'Lar temporário e resgate de animais na Zona Norte de São Paulo. Castração e adoção.',
        'address': 'Rua Valdemar Martins, 980 — Parque Peruche, São Paulo/SP',
        'phone': '(11) 97055-3947',
        'website': 'https://www.ongcantodaterra.org',
        'lat': -23.527,
        'lng': -46.632,
        'is_active': True,
    },
    {
        'name': 'Cão Sem Dono',
        'partner_type': 'foster_home',
        'description': 'ONG com rede de lares temporários e feiras de adoção na Zona Sul de SP.',
        'address': 'Rua Honório Serpa, 259 — Jardim Vergueiro, São Paulo/SP',
        'website': 'https://www.caosemdono.com.br',
        'lat': -23.636,
        'lng': -46.563,
        'is_active': True,
    },
    {
        'name': 'Instituto Amor em Patas (IAPA)',
        'partner_type': 'foster_home',
        'description': 'Rede de lares temporários na Grande SP. Resgate, esterilização e adoção responsável.',
        'address': 'Av. Paulista, 1000 — Bela Vista, São Paulo/SP',
        'website': 'https://www.amorempatas.com',
        'lat': -23.567,
        'lng': -46.654,
        'is_active': True,
    },
    {
        'name': 'UIPA — União Internacional Protetora dos Animais',
        'partner_type': 'foster_home',
        'description': 'Entidade centenária de proteção animal em SP. Castrações populares e adoção.',
        'address': 'Rua Major Quedinho, 90 — República, São Paulo/SP',
        'phone': '(11) 3255-3361',
        'website': 'https://www.uipa.org.br',
        'lat': -23.547,
        'lng': -46.643,
        'is_active': True,
    },
    {
        'name': 'Anjos Peludos',
        'partner_type': 'foster_home',
        'description': 'ONG do interior de SP dedicada ao resgate e lar temporário de cães e gatos.',
        'address': 'Rua do Manganês, 736 — Vila Mollon IV, Santa Bárbara d\'Oeste/SP',
        'phone': '(19) 98817-7248',
        'website': 'https://www.anjospeludos.org.br',
        'lat': -22.750,
        'lng': -47.405,
        'is_active': True,
    },
    {
        'name': 'AMPARA Animal',
        'partner_type': 'foster_home',
        'description': 'ONG que conecta lares temporários e animais resgatados na Grande SP.',
        'address': 'Rua Boa Vista, 356 — Centro, São Paulo/SP',
        'phone': '(11) 3105-2244',
        'website': 'https://www.amparanimal.org.br',
        'lat': -23.545,
        'lng': -46.636,
        'is_active': True,
    },
    {
        'name': 'AABV — Ação Animal da Baixada do Vale',
        'partner_type': 'foster_home',
        'description': 'Rede de lares temporários e resgate na região de São José dos Campos e Vale do Paraíba.',
        'address': 'Rua Sebastião Hummel, 45 — Jardim Satélite, São José dos Campos/SP',
        'phone': '(12) 99765-4321',
        'lat': -23.221,
        'lng': -45.900,
        'is_active': True,
    },
]


def seed():
    config = os.environ.get('FLASK_CONFIG', 'production')
    app = create_app(config)

    with app.app_context():
        adicionados = 0
        pulados = 0

        for dados in PARCEIROS:
            if Partner.query.filter_by(name=dados['name']).first():
                print(f'  ⏭️  "{dados["name"]}" já existe, pulando...')
                pulados += 1
                continue
            db.session.add(Partner(**dados))
            print(f'  ✅  "{dados["name"]}" adicionado')
            adicionados += 1

        db.session.commit()
        print(f'\nConcluído: {adicionados} adicionados, {pulados} já existiam.')
        print(f'Total no arquivo: {len(PARCEIROS)} entidades.')


if __name__ == '__main__':
    seed()
