# PetPost

Sistema web para divulgar pets perdidos e encontrados. Qualquer pessoa pode criar um post com foto e informações do animal.

# DEMO

https://www.petspost.com.br

## O que tem no projeto

- Cadastro e login de usuarios
- Criar posts de pet perdido ou encontrado com até 5 fotos
- Filtrar posts por tipo de animal e status
- Mapa com lares temporarios, petshops e veterinarios parceiros
- Modulo de adoção
- Painel de admin pra moderar posts e usuarios
- Contato direto via WhatsApp

## Como rodar localmente

### Requisitos

- Python 3.11 ou superior
- MySQL rodando localmente
- Git

### Passo a passo

**1. Clonar o repositório**

```bash
git clone <url-do-repo>
cd petpost
```

**2. Criar ambiente virtual e instalar dependencias**

```bash
python -m venv venv
source venv/bin/activate  # no windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Criar o banco de dados no MySQL**

Entre no MySQL e crie o banco:

```sql
CREATE DATABASE petpost_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**4. Configurar o arquivo .env**

Copie o arquivo de exemplo e preencha com os seus dados:

```bash
cp .env.example .env
```

Edite o `.env`:

```
FLASK_APP=run.py
FLASK_CONFIG=development
SECRET_KEY=qualquer-coisa-aqui-mude-em-producao
DATABASE_URL=mysql+pymysql://root:suasenha@localhost/petpost_dev
```

**5. Criar as tabelas no banco**

```bash
flask db upgrade
```

Se der erro, tente:

```bash
flask create-db
```

**6. Popular o banco com dados de exemplo (opcional)**

```bash
python seeds.py
```

Isso cria um admin e alguns posts de teste.
- Admin: `admin@petpost.com` / `Admin@123`

**7. Rodar o servidor**

```bash
flask run
```

Acesse em: http://localhost:5000

## Rodando os testes

```bash
pytest
```

Para ver mais detalhes:

```bash
pytest -v
```

## Estrutura do projeto

```
app/
  models/      # tabelas do banco de dados
  routes/      # rotas e lógica de cada módulo
  forms/       # formulários com validação
  templates/   # paginas HTML
  static/      # css, js e uploads
  services/    # geocoding via OpenStreetMap
  utils/       # funções auxiliares
migrations/    # migrações do banco de dados
tests/         # testes automatizados
seeds.py       # dados de exemplo pra desenvolvimento
run.py         # ponto de entrada da aplicação
```
