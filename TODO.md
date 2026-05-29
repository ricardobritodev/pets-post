# 📋 TODO List — PetPost

> Tarefas divididas por área. Marque com `[x]` ao concluir cada tarefa.
>
> **Legenda de prioridade:**
> 🔴 Sprint 1 — Alta prioridade (base do projeto)
> 🟡 Sprint 2 — Média prioridade (funcionalidades core)
> 🟢 Sprint 3 — Baixa prioridade (melhorias e módulos futuros)

---

## 🎨 FRONTEND — Interface, Templates, CSS e JavaScript

### 🔴 Sprint 1 — Base Visual

- [x] **F-01 · Template Base** (`base.html`)
  - Navbar com logo 🐾, menu de navegação, flash messages e footer
  - **Arquivo:** `app/templates/base.html`
  - **Dica:** `Jinja2 template inheritance`, `Flask flash messages`

- [x] **F-02 · CSS Global e Design System** (`main.css`)
  - Variáveis CSS de cor, tipografia, espaçamento. Estilos de botões, inputs, cards e grid
  - **Arquivo:** `app/static/css/main.css`
  - **Dica:** `CSS custom properties`, `CSS Grid`, `Flexbox`

- [x] **F-03 · Página Inicial — Feed de Posts** (`index.html`)
  - Hero section, grid de cards dos posts recentes, filtros por status e tipo de pet
  - **Arquivo:** `app/templates/main/index.html`
  - **Dica:** `CSS card layout`, `Jinja2 for loop`, `Flask url_for`

- [x] **F-04 · Formulários de Login e Cadastro**
  - Campos grandes e legíveis, erros inline, feedback visual de validação
  - **Arquivos:** `app/templates/auth/login.html` e `register.html`
  - **Dica:** `WTForms render_field`, `Flask-WTF CSRF`, `CSS form styling`

---

### 🟡 Sprint 2 — Funcionalidades Core

- [x] **F-05 · Formulário de Criação de Post** (`create.html`)
  - Upload de múltiplas fotos com preview, campos de localização, informações e contato
  - **Arquivo:** `app/templates/posts/create.html`
  - **Dica:** `JavaScript FileReader API`, `HTML multiple file input`, `Flask file upload`

- [x] **F-06 · Página de Detalhe do Post** (`detail.html`)
  - Galeria de fotos, dados do pet, localização, contato e botão "Marcar como resolvido"
  - **Arquivo:** `app/templates/posts/detail.html`
  - **Dica:** `CSS image gallery`, `Jinja2 macros`, `responsive images`

- [x] **F-07 · Badges e Status Visual dos Posts**
  - Badge "PERDIDO" em vermelho, "ENCONTRADO" em verde, "RESOLVIDO" em cinza
  - **Arquivo:** `app/static/css/main.css` (seção badges)
  - **Dica:** `CSS badges pills`, `color contrast WCAG`

- [x] **F-08 · Lista/Feed com Paginação** (`list.html`)
  - Filtros por tipo de pet e status, paginação com Anterior/Próximo
  - **Arquivo:** `app/templates/posts/list.html`
  - **Dica:** `Flask-SQLAlchemy paginate`, `Jinja2 pagination`, `CSS filter`

---

### 🟢 Sprint 3 — Melhorias e Módulos Futuros

- [x] **F-09 · Painel do Administrador** (`dashboard.html`)
  - Tabela de usuários, tabela de posts, contadores no topo
  - **Arquivo:** `app/templates/admin/dashboard.html`
  - **Dica:** `CSS data tables`, `Flask admin pattern`

- [x] **F-10 · Filtros Dinâmicos sem Recarregar Página**
  - Filtros de busca usando Fetch API (sem recarregar a página) 
  - **Arquivo:** `app/static/js/main.js`
  - **Dica:** `JavaScript Fetch API`, `Flask JSON response`, `DOM manipulation`

- [x] **F-11 · Menu Hambúrguer para Mobile**
  - Implementar menu responsivo para telas pequenas (atualmente escondido)
  - **Arquivo:** `app/static/js/main.js` e `app/static/css/main.css`
  - **Dica:** `CSS hamburger menu`, `JavaScript toggle class`

- [x] **F-12 · Integração com Leaflet.js + OpenStreetMap (Mapa de Localização)**
  - Mapa interativo na página de detalhe com marcador onde o pet foi visto
  - **Arquivo:** `app/templates/posts/detail.html`
  - **Dica:** `Google Maps JavaScript API`, `Leaflet.js (gratuito)`, `lat/lng no template`

- [x] **F-13 · Templates do Módulo de Adoção**
  - Lista de pets para adoção, formulário de cadastro e página de detalhe
  - **Arquivos:** `app/templates/adoption/list.html`, `detail.html`, `create.html`
  - **Dica:** Reutilizar estrutura dos templates de `posts/`

- [x] **F-14 · Mapa de Lares Temporários e Petshops**
  - Mapa com lares temporários e petshops parceiros próximos ao usuário
  - **Arquivo:** `app/templates/map/index.html`
  - **Dica:** `Geolocation API browser`, `Leaflet.js marker clusters`

---

---

## ⚙️ BACKEND — Lógica, Banco de Dados, API e Segurança

### 🔴 Sprint 1 — Infraestrutura Base

- [x] **B-01 · Application Factory e Extensões**
  - Padrão Application Factory, SQLAlchemy, Flask-Login, Flask-Migrate, Flask-WTF
  - **Arquivos:** `app/__init__.py` e `app/extensions.py`
  - **Dica:** `Flask Application Factory pattern`, `Flask Blueprint register`

- [x] **B-02 · Models do Banco de Dados**
  - Models `User`, `PetPost` e `Photo` com relacionamentos, constraints e métodos
  - **Arquivos:** `app/models/user.py`, `pet_post.py`, `photo.py`
  - **Dica:** `Flask-SQLAlchemy models`, `SQLAlchemy relationships`

- [x] **B-03 · Sistema de Migrações**
  - Flask-Migrate configurado, migração inicial criada
  - **Pasta:** `migrations/`
  - **Comandos:** `flask db init` → `flask db migrate` → `flask db upgrade`

- [x] **B-04 · Autenticação — Login e Registro**
  - Login com hash de senha, registro com email único, logout, `@login_required`
  - **Arquivo:** `app/routes/auth.py`
  - **Dica:** `Flask-Login tutorial`, `Werkzeug password hashing`

- [x] **B-05 · Perfis de Usuário — Admin vs Usuário Comum**
  - Sistema de roles, decorator `@admin_required`, permissões nas rotas
  - **Arquivo:** `app/routes/admin.py`
  - **Dica:** `Flask custom decorator`, `Flask-Login current_user`

---

### 🟡 Sprint 2 — Funcionalidades Core

- [x] **B-06 · CRUD de Posts**
  - Criar, listar, detalhar, editar, excluir posts. Apenas dono ou admin pode editar/excluir
  - **Arquivo:** `app/routes/posts.py`
  - **Dica:** `Flask CRUD pattern`, `SQLAlchemy query filter`, `Flask abort 403`

- [x] **B-07 · Upload e Processamento de Fotos**
  - Upload de até 5 fotos por post, validação de extensão, UUID único, resize para 800px
  - **Função:** `save_photo()` em `app/routes/posts.py`
  - **Dica:** `Flask file upload werkzeug`, `Pillow image resize`, `Python uuid`

- [x] **B-08 · Filtros e Paginação na Listagem**
  - Filtros por status e tipo de pet, paginação com 12 posts por página
  - **Arquivo:** `app/routes/posts.py` (rota `list_posts`)
  - **Dica:** `SQLAlchemy filter`, `Flask-SQLAlchemy paginate`, `Flask request.args`

- [x] **B-09 · Formulários com Validação de Dados**
  - WTForms com validações de campos obrigatórios, email, comprimento mínimo/máximo
  - **Arquivos:** `app/forms/auth_forms.py` e `post_forms.py`
  - **Dica:** `WTForms validators`, `Flask-WTF custom validator`

- [x] **B-10 · Seeds — Dados de Desenvolvimento**
  - 1 admin, 4 usuários e 5 posts fictícios para facilitar o desenvolvimento
  - **Arquivo:** `seeds.py`
  - **Comando:** `python seeds.py`

---

### 🟢 Sprint 3 — Melhorias e Módulos Futuros

- [x] **B-11 · Painel Administrativo — Backend**
  - Listar usuários (ativar/desativar), listar posts, estatísticas
  - **Arquivo:** `app/routes/admin.py`
  - **Dica:** `Flask admin Blueprint`, `SQLAlchemy count query`

- [x] **B-12 · Testes Automatizados**
  - Testes de autenticação e posts com pytest
  - **Arquivos:** `tests/test_auth.py` e `tests/test_posts.py`
  - **Comando:** `pytest -v`

- [x] **B-13 · Integração com API de CEP (ViaCEP)**
  - Preencher endereço automaticamente ao informar o CEP no formulário de post
  - **Dica:** `ViaCEP API Python requests`, `Flask AJAX endpoint`, `JavaScript fetch CEP`
  - **URL da API:** `https://viacep.com.br/ws/{CEP}/json/`

- [x] **B-14 · Módulo de Adoção**
  - Model `AdoptionPost`, rotas CRUD, lógica de matching entre adotantes
  - **Arquivos:** `app/models/adoption_post.py` e `app/routes/adoption.py`
  - **Dica:** Reutilizar o padrão de `pet_post.py`

- [x] **B-15 · Módulo de Lares Temporários e Petshops**
  - Models `TemporaryHome` e `Petshop` com localização, endpoint `/api/map/locations`
  - **Dica:** `SQLAlchemy geographic queries`, `Haversine formula`, `Flask JSON API`

- [ ] **B-16 · Notificações por Email**
  - Email quando um post similar ao pet perdido for criado na mesma região
  - **Arquivo:** `app/services/email_service.py`
  - **Dica:** `Flask-Mail tutorial`, `SendGrid Python API`

- [ ] **B-17 · Chat entre Usuários**
  - Sistema de mensagens entre quem encontrou o pet e o dono
  - **Dica:** `Flask-SocketIO WebSocket`, ou mensagens simples via banco de dados

- [x] **B-18 · Integração com WhatsApp**
  - Botão de contato direto via WhatsApp na página de detalhe do post
  - **Dica:** `WhatsApp API link wa.me`, `Flask template tag WA`

---

## 📊 Progresso Geral

| Área | Concluídas | Total | % |
|------|-----------|-------|---|
| Frontend | 9 | 14 | 64% |
| Backend | 12 | 18 | 67% |
| **Total** | **21** | **32** | **66%** |

---

## 🔄 Como usar este arquivo

1. Ao **começar** uma tarefa: mude `[ ]` para `[~]` (em andamento)
2. Ao **concluir** uma tarefa: mude para `[x]`
3. Ao criar uma **nova tarefa** não prevista: adicione com `[ ]` no sprint adequado

**No terminal, para ver as tarefas pendentes:**
```bash
grep -n "\[ \]" TODO.md
```
