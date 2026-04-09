<div align="center">

# 🐾 PetPost

### Plataforma para localização de pets perdidos

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)](https://mysql.com)
[![License](https://img.shields.io/badge/Licença-MIT-green)](LICENSE)

*Projeto acadêmico — Desenvolvido com 🧡 pela equipe*

</div>

---

## 📌 Sobre o Projeto

O **PetPost** é uma plataforma web que conecta pessoas que encontraram pets perdidos com seus donos. Qualquer pessoa pode criar um post com fotos e informações do animal encontrado, ajudando famílias a reencontrar seus pets.

### Funcionalidades Principais
- 📢 Criar posts de pets perdidos ou encontrados com fotos
- 🔍 Filtrar posts por tipo de animal e status
- 👤 Cadastro e login de usuários
- 🛡️ Painel administrativo para moderação
- 📱 Interface responsiva e acessível

### Módulos Futuros (TODO)
- 🏠 Adoção de pets disponíveis
- 🗺️ Mapa de lares temporários
- 🏪 Localização de petshops parceiros
- 💬 Chat entre usuários

---

## 🛠️ Tecnologias

| Categoria | Tecnologia |
|-----------|------------|
| Linguagem | Python 3.11+ |
| Framework | Flask 3.0 |
| Banco de Dados | MySQL 8.0 |
| ORM | SQLAlchemy + Flask-Migrate |
| Autenticação | Flask-Login |
| Formulários | Flask-WTF + WTForms |
| Frontend | HTML5, CSS3 puro, JavaScript vanilla |

---

## 🚀 Como Configurar o Projeto

### Pré-requisitos

Você precisa ter instalado na sua máquina:
- [Python 3.11+](https://python.org/downloads/)
- [MySQL 8.0+](https://dev.mysql.com/downloads/)
- [Git](https://git-scm.com/downloads)

---

### 🍎 Configuração no macOS

**1. Clone o repositório**
```bash
git clone https://github.com/SEU-USUARIO/petpost.git
cd petpost
```

**2. Crie e ative o ambiente virtual**
```bash
python3 -m venv venv
source venv/bin/activate
```
> Você verá `(venv)` no início do terminal — isso significa que está ativo.

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure o banco de dados MySQL**

Abra o MySQL no terminal:
```bash
mysql -u root -p
```

Execute os comandos:
```sql
CREATE DATABASE petpost_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'petpost_user'@'localhost' IDENTIFIED BY 'petpost123';
GRANT ALL PRIVILEGES ON petpost_dev.* TO 'petpost_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**5. Configure as variáveis de ambiente**
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-aqui-mude-isso
DATABASE_URL=mysql+pymysql://petpost_user:petpost123@localhost/petpost_dev
```

**6. Crie as tabelas do banco**

Tente primeiro com Flask-Migrate (recomendado):
```bash
flask db init
flask db migrate -m "Criação inicial das tabelas"
flask db upgrade
```

Se der erro no `flask db upgrade`, use o comando alternativo:
```bash
flask create-db
```
> Este comando cria todas as tabelas diretamente, sem depender das migrations.

**7. Popule o banco com dados de exemplo (opcional)**
```bash
python seeds.py
```

**8. Rode o servidor**
```bash
flask run
```

Acesse: [http://localhost:5000](http://localhost:5000) 🎉

---

### 🪟 Configuração no Windows

**1. Clone o repositório**
```cmd
git clone https://github.com/SEU-USUARIO/petpost.git
cd petpost
```

**2. Crie e ative o ambiente virtual**
```cmd
python -m venv venv
venv\Scripts\activate
```
> Você verá `(venv)` no início do terminal.

**3. Instale as dependências**
```cmd
pip install -r requirements.txt
```

**4. Configure o banco de dados MySQL**

Abra o MySQL Command Line Client ou MySQL Workbench e execute:
```sql
CREATE DATABASE petpost_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'petpost_user'@'localhost' IDENTIFIED BY 'petpost123';
GRANT ALL PRIVILEGES ON petpost_dev.* TO 'petpost_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**5. Configure as variáveis de ambiente**
```cmd
copy .env.example .env
```

Abra o arquivo `.env` com o Bloco de Notas e edite:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-aqui-mude-isso
DATABASE_URL=mysql+pymysql://petpost_user:petpost123@localhost/petpost_dev
```

**6. Crie as tabelas do banco**

Tente primeiro com Flask-Migrate (recomendado):
```cmd
flask db init
flask db migrate -m "Criação inicial das tabelas"
flask db upgrade
```

Se der erro no `flask db upgrade`, use o comando alternativo:
```cmd
flask create-db
```
> Este comando cria todas as tabelas diretamente, sem depender das migrations.

**7. Popule o banco com dados de exemplo (opcional)**
```cmd
python seeds.py
```

**8. Rode o servidor**
```cmd
flask run
```

Acesse: [http://localhost:5000](http://localhost:5000) 🎉

---

## 👤 Usuário Admin Padrão (após rodar seeds.py)

| Campo | Valor |
|-------|-------|
| Email | admin@petpost.com |
| Senha | Admin@123 |

> ⚠️ **IMPORTANTE:** Mude a senha em produção!

---

## 🗃️ Estrutura do Projeto

```
petpost/
├── app/
│   ├── __init__.py        # App factory — cria a instância do Flask
│   ├── config.py          # Configurações (dev, test, prod)
│   ├── extensions.py      # Extensões Flask (db, login, etc.)
│   ├── models/            # Modelos do banco de dados
│   │   ├── user.py        # Usuários
│   │   ├── pet_post.py    # Posts de pets
│   │   └── photo.py       # Fotos dos posts
│   ├── routes/            # Rotas e controllers
│   │   ├── auth.py        # Login, cadastro, logout
│   │   ├── main.py        # Home e sobre
│   │   ├── posts.py       # CRUD de posts
│   │   └── admin.py       # Painel admin
│   ├── forms/             # Formulários WTForms
│   │   ├── auth_forms.py  # Login e cadastro
│   │   └── post_forms.py  # Criar/editar post
│   ├── static/            # CSS, JS, imagens
│   │   ├── css/main.css   # Estilos globais
│   │   └── js/main.js     # Scripts globais
│   └── templates/         # Templates HTML (Jinja2)
│       ├── base.html      # Template base com navbar e footer
│       ├── auth/          # Login e cadastro
│       ├── main/          # Home e sobre
│       ├── posts/         # CRUD de posts
│       └── admin/         # Painel admin
├── migrations/            # Migrações do banco (gerado pelo Flask-Migrate)
├── tests/                 # Testes automatizados
├── .env.example           # Variáveis de ambiente (modelo)
├── .gitignore             # Arquivos ignorados pelo Git
├── requirements.txt       # Dependências Python
├── seeds.py               # Script para popular o banco com dados de exemplo
├── run.py                 # Ponto de entrada da aplicação
└── README.md              # Este arquivo
```

---

## 🧪 Rodando os Testes

```bash
# Rodar todos os testes
pytest

# Rodar com detalhes
pytest -v

# Rodar um arquivo específico
pytest tests/test_auth.py -v
```

---

## 🔄 Fluxo para Contribuir (Git Flow)

1. **Nunca commite diretamente na `main`**
2. Crie uma branch com o padrão:
   - `feat/nome-da-funcionalidade` — para novas features
   - `fix/nome-do-bug` — para correções
   - `docs/o-que-documentou` — para documentação

```bash
# Exemplo
git checkout -b feat/modulo-adocao
```

3. Faça seus commits com mensagens claras em português:
```bash
git commit -m "feat: adiciona modelo de adoção de pets"
git commit -m "fix: corrige validação do formulário de post"
```

4. Faça push e abra um **Pull Request** para a branch `develop`:
```bash
git push origin feat/modulo-adocao
```

5. O PR deve ser revisado por pelo menos **1 membro** antes de fazer merge.

---

## 🤝 Equipe

| Nome | Função | GitHub |
|------|--------|--------|
| Nome 1 | Backend | @usuario1 |
| Nome 2 | Frontend | @usuario2 |
| Nome 3 | Banco de Dados | @usuario3 |
| Nome 4 | Full Stack | @usuario4 |

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
