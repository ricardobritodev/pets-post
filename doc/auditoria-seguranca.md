# Auditoria de Segurança — PetPost

**Data:** 2026-05-28  
**Auditor:** Claude Code (Anthropic)  
**Versão analisada:** branch `HEAD` (commit `3900135`)  
**Escopo:** Código-fonte completo da aplicação Flask

---

## Resumo Executivo

**Nível de Maturidade de Segurança: 4/10 (Médio-Baixo — não apto para produção)**

A aplicação demonstra boas práticas de base: proteção CSRF via Flask-WTF, ORM com SQLAlchemy (proteção implícita contra SQL Injection), hashing de senha com Werkzeug (pbkdf2), verificação de ownership em todas as rotas de edição/deleção, e SRI (Subresource Integrity) nos scripts Leaflet. No entanto, há **duas vulnerabilidades críticas exploráveis remotamente** (open redirect e XSS no mapa via `javascript:` URL), ausência total de cabeçalhos de segurança HTTP, nenhum rate limiting em login/registro e configurações de cookie inseguras para produção. A aplicação **não deve ser exposta publicamente** sem as correções da Fase 1 e 2.

---

## Vulnerabilidades por Severidade

---

### CRÍTICO (Fase 1 — Bloqueia qualquer deploy)

#### CRIT-01 — Open Redirect no Login
- **Arquivo:** `app/routes/auth.py:53-54`
- **Descrição:** O parâmetro `next` da URL é redirecionado sem validação. Um atacante envia `https://petpost.com/auth/login?next=https://evil.com` e após login o usuário é enviado para o site malicioso.
- **Impacto:** Phishing, credential harvesting, session hijacking.
- **CVSS estimado:** 7.4 (High)
- **Código vulnerável:**
  ```python
  next_page = request.args.get('next')
  return redirect(next_page or url_for('main.index'))
  ```

#### CRIT-02 — XSS Stored via `javascript:` URL no Mapa
- **Arquivo:** `app/templates/map/index.html:132`
- **Descrição:** O campo `website` do Partner é inserido diretamente em `href` sem validação de scheme. Se `website = "javascript:fetch(...)"`, clicar em "Visitar site" executa JS no contexto da aplicação. Todos os outros campos (name, address, phone, email) são concatenados em HTML sem escape — também XSS stored.
- **Impacto:** Roubo de cookies de sessão, execução arbitrária de JS para todos os visitantes do mapa.
- **CVSS estimado:** 8.0 (High)
- **Código vulnerável:**
  ```javascript
  html += '<a href="' + p.website + '">' // p.website não escapado
  html += '<strong>' + p.name + '</strong>' // p.name não escapado
  ```

#### CRIT-03 — SECRET_KEY com Fallback Inseguro em Produção
- **Arquivo:** `app/config.py:24`
- **Descrição:** Se `SECRET_KEY` não estiver definida na VPS, a aplicação usa `'dev-secret-key-change-in-prod'` (hardcoded no repositório público). Com ela qualquer pessoa pode forjar cookies de sessão e tokens CSRF.
- **Impacto:** Assumir sessão de qualquer usuário incluindo admin. Bypass de toda proteção CSRF.
- **CVSS estimado:** 9.8 (Critical)
- **Código vulnerável:**
  ```python
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'
  ```

#### CRIT-04 — Ausência Total de Rate Limiting
- **Arquivos:** `app/routes/auth.py`, `app/routes/api.py`
- **Descrição:** Nenhuma rota possui limitação de requisições. `/auth/login` permite brute force ilimitado. `/auth/register` permite criação de contas em massa. `/api/cep/<cep>` é proxy gratuito para ViaCEP sem limite.
- **Impacto:** Comprometimento de contas por brute force, spam, blacklist do IP na ViaCEP.
- **CVSS estimado:** 7.5 (High)

---

### ALTO (Fase 2 — Implementar antes de expor publicamente)

#### HIGH-01 — Cookies de Sessão Inseguros para Produção
- **Arquivo:** `app/config.py:69-87`
- **Descrição:** `ProductionConfig` não define `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`. Cookies trafegam via HTTP, acessíveis por JavaScript.
- **Impacto:** Session hijacking via sniffing em redes abertas; roubo de cookie via XSS.
- **CVSS estimado:** 7.3 (High)

#### HIGH-02 — Ausência de Cabeçalhos de Segurança HTTP
- **Arquivo:** `app/__init__.py` (sem `after_request`)
- **Descrição:** Nenhum header de segurança configurado.
- **Headers ausentes e impactos:**
  | Header | Risco |
  |--------|-------|
  | `X-Frame-Options` | Clickjacking |
  | `X-Content-Type-Options` | MIME sniffing — browser executa upload como script |
  | `Content-Security-Policy` | XSS sem restrição de fontes |
  | `Strict-Transport-Security` | Downgrade HTTP (SSL stripping) |
  | `Referrer-Policy` | Vazamento de URL para terceiros |
  | `Permissions-Policy` | APIs do browser sem restrição |

#### HIGH-03 — Vazamento de Exceções Internas para o Usuário
- **Arquivos:** `app/routes/posts.py:190`, `app/routes/adoption.py:126`
- **Descrição:** `flash(f'Erro ao salvar foto: {str(e)}')` expõe paths do servidor, mensagens de erro do Pillow e outros detalhes internos para o usuário final.
- **Impacto:** Information disclosure — facilita reconhecimento para ataques direcionados.

#### HIGH-04 — Upload sem Validação de MIME Type
- **Arquivos:** `app/routes/posts.py:25-73`, `app/routes/adoption.py:19-43`
- **Descrição:** Validação apenas por extensão. Sem verificação do tipo real do arquivo. Sem proteção explícita contra decompression bomb (imagem 1KB comprimida → 1GB em memória).
- **Impacto:** Upload de arquivos maliciosos; DoS por memória via imagem malformada.

#### HIGH-05 — Logout via GET (CSRF de Logout)
- **Arquivo:** `app/routes/auth.py:90-96`
- **Descrição:** Logout é um GET request. Qualquer site pode forçar logout via `<img src="https://petpost.com/auth/logout">`.
- **Impacto:** Logout forçado de usuários; base para ataques de session fixation.

---

### MÉDIO (Fase 3 — Sprint pós-launch)

#### MED-01 — Enumeração de Usuários no Registro
- **Arquivo:** `app/forms/auth_forms.py:96`
- **Descrição:** Mensagem "Este email já está cadastrado" confirma existência de usuário para atacante.

#### MED-02 — Queries Admin sem Paginação (DoS por Memória)
- **Arquivo:** `app/routes/admin.py:90, 119`
- **Descrição:** `.all()` carrega toda a tabela `users` e `pet_posts` em memória por request.

#### MED-03 — `debug=True` Hardcoded em run.py
- **Arquivo:** `run.py:137`
- **Descrição:** `app.run(debug=True)` fixo. Se executado em produção acidentalmente, habilita o debugger Werkzeug (execução remota de código via browser).

#### MED-04 — Política de Senha Fraca (mínimo 8 caracteres)
- **Arquivo:** `app/forms/auth_forms.py:70-73`
- **Descrição:** Aceita senhas como `password1` ou `12345678`.

#### MED-05 — Geolocalização Automática sem Consentimento
- **Arquivo:** `app/templates/map/index.html:207`
- **Descrição:** `locateUser()` é chamado automaticamente ao abrir o mapa, disparando prompt de geolocalização sem ação do usuário. Violação de boas práticas LGPD.

---

### BAIXO (Fase 4)

#### LOW-01 — Email de Contato Exposto no User-Agent
- **Arquivo:** `app/services/geocoding.py:24`
- **Descrição:** `_USER_AGENT = 'PetPost/1.0 (projeto-academico; contato: admin@petpost.com)'` — email admin visível nos logs do servidor Nominatim (serviço externo).

#### LOW-02 — Ausência de Logging de Segurança
- **Arquivos:** `app/routes/auth.py`
- **Descrição:** Logins, falhas de autenticação e ações admin não são registrados. Impossibilita detecção de ataques.

#### LOW-03 — Sem Auditoria de Dependências (CVE scan)
- **Arquivo:** `requirements.txt`
- **Descrição:** Sem processo de verificação de CVEs nas dependências.

---

## O que Está Correto (Não Regredir)

- CSRF protection ativa em todos os formulários POST via Flask-WTF
- Senhas hasheadas com `werkzeug.security.generate_password_hash` (pbkdf2:sha256)
- Verificação de ownership em todas as rotas de edição/deleção (`current_user.id != post.user_id`)
- `@login_required` antes de `@admin_required` em todas as rotas admin
- Paginação nas listagens públicas (posts e adoção)
- Nomes de arquivo de upload gerados via UUID (sem path traversal)
- SRI (integrity hash) nos scripts Leaflet/CDN
- Parâmetros de query nos filtros de status/tipo validados contra whitelist explícita
- `autoescape=True` no Jinja2 (padrão) — protege contra XSS em templates

---

## Dependências Analisadas

| Pacote | Versão | Status |
|--------|--------|--------|
| Flask | 3.1.0 | OK |
| Flask-WTF | 1.2.2 | OK |
| Flask-Login | 0.6.3 | OK |
| Werkzeug | 3.1.3 | OK |
| Pillow | 11.1.0 | OK |
| PyMySQL | 1.1.1 | OK |
| cryptography | 44.0.2 | OK |

Recomendação: adicionar `pip-audit` ao CI para verificação contínua.
