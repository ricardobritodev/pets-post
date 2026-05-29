# Guia de Produção — PetPost

Tudo que um desenvolvedor sênior verifica, configura e documenta antes de subir uma aplicação Flask em VPS real. Este guia é específico para o estado atual do projeto PetPost.

---

## Índice

1. [O que foi corrigido no código antes deste guia](#1-o-que-foi-corrigido-no-código-antes-deste-guia)
2. [Checklist do repositório Git](#2-checklist-do-repositório-git)
3. [Hardening do servidor VPS](#3-hardening-do-servidor-vps)
4. [Configuração do MySQL em produção](#4-configuração-do-mysql-em-produção)
5. [Variáveis de ambiente de produção](#5-variáveis-de-ambiente-de-produção)
6. [Gunicorn — configuração para produção](#6-gunicorn--configuração-para-produção)
7. [Nginx — proxy reverso e arquivos estáticos](#7-nginx--proxy-reverso-e-arquivos-estáticos)
8. [SSL e domínio](#8-ssl-e-domínio)
9. [Primeiro boot da aplicação](#9-primeiro-boot-da-aplicação)
10. [Verificação pós-deploy](#10-verificação-pós-deploy)
11. [Monitoramento e logs](#11-monitoramento-e-logs)
12. [Backups](#12-backups)
13. [Como atualizar o código em produção](#13-como-atualizar-o-código-em-produção)
14. [O que NÃO fazer em produção](#14-o-que-não-fazer-em-produção)

---

## 1. O que foi corrigido no código antes deste guia

Estes problemas foram identificados na auditoria pré-deploy e já estão corrigidos no repositório. Documentados aqui para referência futura.

### 1.1 ProxyFix ausente (crítico)

**Problema:** sem o `ProxyFix`, quando a aplicação roda atrás do Nginx, `request.remote_addr` retorna sempre o IP do próprio Nginx (`127.0.0.1`). Consequências reais:

- O rate limiting do Flask-Limiter via aplicava o limite por worker, não por cliente real
- Logs de segurança registravam `127.0.0.1` em vez do IP real do atacante
- O Talisman não conseguia detectar corretamente se a requisição veio via HTTPS

**Correção aplicada** em `app/__init__.py`:

```python
from werkzeug.middleware.proxy_fix import ProxyFix

# Em create_app(), antes do Talisman:
if config_name == 'production':
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
```

`x_for=1` diz "confie em 1 nível de proxy para o header `X-Forwarded-For`" — o número certo quando há exatamente um Nginx na frente.

### 1.2 Gunicorn não estava no requirements.txt

Corrigido. `gunicorn==23.0.0` adicionado ao `requirements.txt`. Isso garante que a versão é reproduzível.

### 1.3 Flask-Limiter usava storage hardcoded

O `storage_uri='memory://'` estava fixo no código. Corrigido para ler `RATELIMIT_STORAGE_URI` do `.env`, com fallback para memória em desenvolvimento.

> **Nota sobre rate limiting com múltiplos workers:** com `--workers 2` no Gunicorn e storage em memória, cada worker tem seu próprio contador. O limite efetivo é `N_workers × limite_configurado`. Para rate limiting preciso em produção, configure Redis (ver seção 5).

---

## 2. Checklist do repositório Git

Execute isso na sua máquina local **antes** de fazer o deploy.

### 2.1 Nenhum segredo no repositório

```bash
# Verifique se .env está sendo ignorado corretamente
git status --short | grep "\.env"
# Não deve aparecer nada. Se aparecer "A" ou "M" antes de .env, PARE.

# Confirme que não há senhas hardcoded em arquivos rastreados
git grep -i "password\s*=\s*['\"]" -- "*.py" | grep -v "test\|seeds\|placeholder\|hash"
```

### 2.2 Testes passando

```bash
pytest -v
# Deve aparecer: 25 passed
```

Não suba código com testes quebrando. Um deploy com testes vermelhos é um deploy às cegas.

### 2.3 Código está no GitHub

```bash
git push origin main
# Verifique no GitHub que o último commit é o que você quer em produção
```

### 2.4 Migrations estão em ordem

```bash
# Lista todas as migrations
ls migrations/versions/

# Confirma que o histórico está linear (sem bifurcações)
flask db history
```

Se houver duas migrations com o mesmo `down_revision`, o `flask db upgrade` vai falhar no servidor.

### 2.5 O que NÃO deve estar no Git (verificação rápida)

```bash
git ls-files | grep -E "\.env$|\.env\.local|uploads/[^.]"
# Resultado esperado: apenas .env.example
```

---

## 3. Hardening do servidor VPS

Faça tudo isso **antes** de subir a aplicação. Um servidor sem hardening básico começa a receber ataques de força bruta em minutos após ser provisionado.

### 3.1 Acesso SSH com chave em vez de senha

Autenticação por chave é ordens de magnitude mais segura que senha. Gere o par de chaves na sua máquina local:

```bash
# Na sua máquina LOCAL (não no servidor)
ssh-keygen -t ed25519 -C "petpost-vps"
# Salva em ~/.ssh/id_ed25519 (privada) e ~/.ssh/id_ed25519.pub (pública)
```

Copie a chave pública para o servidor:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@SEU_IP
```

Teste que funciona:
```bash
ssh -i ~/.ssh/id_ed25519 root@SEU_IP
# Deve entrar sem pedir senha
```

### 3.2 Criar usuário não-root e desabilitar login root

```bash
# No servidor, como root:
adduser deploy
usermod -aG sudo deploy

# Copie as chaves SSH do root para o novo usuário
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

### 3.3 Desabilitar login por senha e acesso root via SSH

```bash
sudo nano /etc/ssh/sshd_config
```

Localize e altere (ou adicione) estas linhas:

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
```

Reinicie o SSH:
```bash
sudo systemctl restart sshd
```

> **Teste a conexão em outro terminal antes de fechar o atual.** Se fechar sem testar e algo estiver errado, você perde o acesso.

### 3.4 Firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp      # SSH — NUNCA feche isso
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
sudo ufw status verbose
```

### 3.5 Fail2Ban — proteção contra brute force

O Fail2Ban bane automaticamente IPs que tentam força bruta no SSH e na aplicação.

```bash
sudo apt install -y fail2ban

sudo nano /etc/fail2ban/jail.local
```

Cole o conteúdo:

```ini
[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port    = ssh
logpath = %(sshd_log)s

[nginx-http-auth]
enabled = true
```

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Verifique os jails ativos
sudo fail2ban-client status
```

### 3.6 Atualizações automáticas de segurança

```bash
sudo apt install -y unattended-upgrades

sudo dpkg-reconfigure --priority=low unattended-upgrades
# Selecione "Yes"
```

Isso instala automaticamente patches de segurança do Ubuntu sem precisar de intervenção manual.

---

## 4. Configuração do MySQL em produção

### 4.1 Segurança inicial

```bash
sudo mysql_secure_installation
```

| Pergunta | Resposta recomendada |
|----------|---------------------|
| Setup VALIDATE PASSWORD? | `Y` (ativa política de senhas) |
| Password strength | `1` (medium — exige letras + números + símbolos) |
| Set root password? | Use uma senha forte de 20+ caracteres |
| Remove anonymous users? | `Y` |
| Disallow root login remotely? | `Y` |
| Remove test database? | `Y` |
| Reload privilege tables? | `Y` |

### 4.2 Criar banco e usuário com privilégios mínimos

O usuário de produção deve ter acesso **somente ao banco da aplicação** — nada mais.

```bash
sudo mysql
```

```sql
CREATE DATABASE petpost_prod
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Crie o usuário com uma senha forte (20+ caracteres, símbolos, números)
CREATE USER 'petpost_user'@'localhost'
  IDENTIFIED BY 'SENHA_FORTE_AQUI';

-- Apenas este banco, apenas operações da aplicação
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER
  ON petpost_prod.*
  TO 'petpost_user'@'localhost';

FLUSH PRIVILEGES;
EXIT;
```

> Não dê `GRANT ALL` ao usuário da aplicação. Se a aplicação for comprometida, o atacante não vai conseguir acessar outros bancos nem exportar dados do sistema.

### 4.3 Confirmar que MySQL não escuta conexões externas

```bash
sudo ss -tlnp | grep mysql
# Deve mostrar: 127.0.0.1:3306
# Se mostrar 0.0.0.0:3306, o banco está exposto na internet — corrija em /etc/mysql/mysql.conf.d/mysqld.cnf
```

---

## 5. Variáveis de ambiente de produção

Crie o `.env` no servidor. **Este arquivo nunca vai para o Git.**

```bash
nano /var/www/petpost/.env
```

```bash
FLASK_APP=run.py
FLASK_CONFIG=production

# Gere com: python3 -c "import secrets; print(secrets.token_hex(32))"
# Nunca reutilize a chave do desenvolvimento
SECRET_KEY=GERE_UMA_CHAVE_NOVA_AQUI

# Use o usuário e senha criados no passo 4.2
DATABASE_URL=mysql+pymysql://petpost_user:SENHA_FORTE_AQUI@localhost/petpost_prod

# Opcional mas recomendado com múltiplos workers:
# RATELIMIT_STORAGE_URI=redis://localhost:6379
```

Proteja o arquivo:

```bash
chmod 600 /var/www/petpost/.env
chown deploy:deploy /var/www/petpost/.env
```

### Gerar a SECRET_KEY corretamente

Na sua máquina **local** (nunca no servidor — a entropia é melhor):

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado para o `.env` do servidor. Uma chave diferente da de desenvolvimento — as sessões de dev não vão funcionar em prod (isso é intencional).

### Sobre o RATELIMIT_STORAGE_URI

Com `--workers 2` no Gunicorn e storage em memória:
- Cada worker tem contador separado
- Limite de "10 por minuto" vira "20 por minuto" efetivo

Para rate limiting preciso, instale Redis e configure:

```bash
sudo apt install -y redis-server
sudo systemctl enable redis-server
```

```bash
# No .env
RATELIMIT_STORAGE_URI=redis://localhost:6379
```

---

## 6. Gunicorn — configuração para produção

Crie um arquivo de configuração dedicado:

```bash
nano /var/www/petpost/gunicorn.conf.py
```

```python
# Número de workers: (2 x núcleos_de_CPU) + 1
# Para VPS com 1 vCPU: workers = 3
# Para VPS com 2 vCPU: workers = 5
workers = 3

# Socket Unix — mais rápido que TCP para comunicação com Nginx
bind = "unix:/var/www/petpost/petpost.sock"

# Timeout: mata requisições que demoram mais de 30s (protege contra slowloris parcial)
timeout = 30

# Reinicia worker após N requests — evita acúmulo de memória (memory leaks)
max_requests = 1000
max_requests_jitter = 100

# Logs
accesslog = "/var/log/petpost/access.log"
errorlog  = "/var/log/petpost/error.log"
loglevel  = "warning"

# Segurança: limita tamanho do header de request
limit_request_line   = 4094
limit_request_fields = 100
```

Crie o diretório de logs:

```bash
sudo mkdir -p /var/log/petpost
sudo chown deploy:www-data /var/log/petpost
```

Crie o serviço systemd:

```bash
sudo nano /etc/systemd/system/petpost.service
```

```ini
[Unit]
Description=PetPost — Gunicorn WSGI server
After=network.target mysql.service
Requires=mysql.service

[Service]
User=deploy
Group=www-data
WorkingDirectory=/var/www/petpost
EnvironmentFile=/var/www/petpost/.env
ExecStart=/var/www/petpost/venv/bin/gunicorn \
          --config /var/www/petpost/gunicorn.conf.py \
          run:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5
# Limites de segurança do processo
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable petpost
sudo systemctl start petpost
sudo systemctl status petpost
```

---

## 7. Nginx — proxy reverso e arquivos estáticos

```bash
sudo nano /etc/nginx/sites-available/petpost
```

```nginx
# Redireciona HTTP → HTTPS (o Certbot vai complementar isso depois)
server {
    listen 80;
    server_name seudominio.com.br www.seudominio.com.br;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seudominio.com.br www.seudominio.com.br;

    # Certificados SSL — preenchidos pelo Certbot
    # ssl_certificate     /etc/letsencrypt/live/seudominio.com.br/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/seudominio.com.br/privkey.pem;
    # include /etc/letsencrypt/options-ssl-nginx.conf;
    # ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Limite de upload — deve ser >= MAX_CONTENT_LENGTH do Flask (8MB)
    client_max_body_size 10M;

    # Oculta versão do Nginx dos headers de resposta
    server_tokens off;

    # Arquivos estáticos com cache agressivo — Nginx serve direto, sem passar pelo Flask
    location /static/ {
        alias /var/www/petpost/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options nosniff;
    }

    # Uploads: serve como download, nunca executa
    location /static/uploads/ {
        alias /var/www/petpost/app/static/uploads/;
        add_header X-Content-Type-Options nosniff;
        add_header Content-Disposition "inline";
        default_type application/octet-stream;
        expires 30d;

        # Bloqueia acesso a qualquer arquivo que não seja imagem
        location ~* \.(php|py|sh|pl|cgi|rb)$ {
            deny all;
        }
    }

    # Todo o resto vai para o Gunicorn
    location / {
        proxy_pass http://unix:/var/www/petpost/petpost.sock;

        # Headers para o Flask enxergar o IP real (requer ProxyFix configurado)
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_read_timeout  30;
        proxy_send_timeout  30;
        proxy_connect_timeout 10;

        # Desativa buffers para respostas de streaming
        proxy_buffering off;
    }

    # Bloqueia acesso a arquivos sensíveis
    location ~ /\.(env|git|htaccess) { deny all; }
    location ~ /\.py$                { deny all; }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/petpost /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

---

## 8. SSL e domínio

### 8.1 Apontar o domínio (Registro.br)

No painel do Registro.br, edite a zona DNS:

| Tipo | Nome | Valor |
|------|------|-------|
| A | `@` | IP da VPS |
| A | `www` | IP da VPS |

Aguarde a propagação (15–60 min). Confirme:

```bash
nslookup seudominio.com.br
# Deve retornar o IP da VPS
```

### 8.2 Instalar o certificado SSL

```bash
sudo certbot --nginx -d seudominio.com.br -d www.seudominio.com.br
```

O Certbot modifica automaticamente a configuração do Nginx para ativar HTTPS.

### 8.3 Verificar renovação automática

```bash
sudo systemctl status certbot.timer
sudo certbot renew --dry-run
```

---

## 9. Primeiro boot da aplicação

### 9.1 Instalar dependências

```bash
cd /var/www/petpost
source venv/bin/activate
pip install -r requirements.txt
```

### 9.2 Criar as tabelas

```bash
flask db upgrade
```

Se houver erro de conexão, confirme que o `.env` tem as credenciais corretas e que o MySQL está rodando:
```bash
sudo systemctl status mysql
```

### 9.3 Criar o primeiro admin manualmente

**Nunca rode `seeds.py` em produção** — ele cria o usuário admin com a senha `Admin@123`, que é pública no repositório.

Crie o admin pelo shell do Flask:

```bash
flask shell
```

```python
from app.extensions import db
from app.models.user import User

admin = User(
    name='Admin',
    email='admin@seudominio.com.br',
    role='admin'
)
admin.set_password('SUA_SENHA_FORTE_E_UNICA')
db.session.add(admin)
db.session.commit()
print(f'Admin criado: {admin.email}')
exit()
```

### 9.4 Permissões da pasta de uploads

```bash
# O Gunicorn roda como 'deploy' no grupo 'www-data'
chmod 750 /var/www/petpost/app/static/uploads/
chown deploy:www-data /var/www/petpost/app/static/uploads/
```

---

## 10. Verificação pós-deploy

Antes de divulgar o link, percorra este checklist manualmente:

### Funcionalidade básica
- [ ] `https://seudominio.com.br` carrega sem erro
- [ ] `http://seudominio.com.br` redireciona para HTTPS
- [ ] Cadeado SSL verde na barra do navegador
- [ ] Cadastro de novo usuário funciona
- [ ] Login funciona com o usuário criado
- [ ] Logout funciona (botão no navbar)
- [ ] Upload de foto em um post funciona
- [ ] A foto aparece corretamente após o upload
- [ ] Mapa de parceiros carrega (`/mapa`)
- [ ] API de CEP responde: `https://seudominio.com.br/api/cep/01310100`

### Segurança
- [ ] Acessar `/admin` sem estar logado → redireciona para login (não mostra o painel)
- [ ] Tentar editar o post de outro usuário → retorna 403
- [ ] Verificar headers de segurança com [securityheaders.com](https://securityheaders.com)
- [ ] Verificar SSL com [ssllabs.com/ssltest](https://www.ssllabs.com/ssltest/) — deve ser A ou A+

### Logs limpos
```bash
sudo journalctl -u petpost --since "10 minutes ago" | grep -i "error\|exception\|critical"
# Não deve aparecer nada
```

---

## 11. Monitoramento e logs

### Ver logs em tempo real

```bash
# Logs da aplicação (Gunicorn + Flask)
sudo journalctl -u petpost -f

# Logs de acesso HTTP
sudo tail -f /var/log/petpost/access.log

# Erros da aplicação
sudo tail -f /var/log/petpost/error.log

# Logs do Nginx
sudo tail -f /var/log/nginx/error.log

# Eventos de segurança (login, brute force, etc.)
sudo journalctl -u petpost -f | grep "petpost.security"
```

### Verificar se todos os serviços estão rodando

```bash
sudo systemctl status petpost nginx mysql fail2ban
```

### Cron simples de monitoramento

Crie um script que envia e-mail se a aplicação cair:

```bash
sudo nano /etc/cron.d/petpost-monitor
```

```
*/5 * * * * deploy curl -sf https://seudominio.com.br/posts > /dev/null || \
  echo "PetPost DOWN $(date)" | mail -s "ALERTA: PetPost fora do ar" seu@email.com
```

---

## 12. Backups

### Backup diário do banco de dados

```bash
sudo mkdir -p /home/deploy/backups
sudo chown deploy:deploy /home/deploy/backups
nano /home/deploy/backup-db.sh
```

```bash
#!/bin/bash
set -e

DATE=$(date +%Y%m%d_%H%M)
BACKUP_DIR=/home/deploy/backups
DB_USER=petpost_user
DB_PASS="$(grep DATABASE_URL /var/www/petpost/.env | grep -oP ':\K[^@]+')"
DB_NAME=petpost_prod

# Dump comprimido
mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" | gzip > "$BACKUP_DIR/petpost_$DATE.sql.gz"

# Mantém apenas os últimos 7 backups diários
ls -t "$BACKUP_DIR"/petpost_*.sql.gz | tail -n +8 | xargs -r rm

echo "Backup concluído: petpost_$DATE.sql.gz"
```

```bash
chmod 700 /home/deploy/backup-db.sh

# Agendar para rodar todo dia às 3h da manhã
crontab -e
# Adicione a linha:
0 3 * * * /home/deploy/backup-db.sh >> /home/deploy/backups/backup.log 2>&1
```

### Testar o backup

```bash
/home/deploy/backup-db.sh
ls -lh /home/deploy/backups/
```

### Testar a restauração (pelo menos uma vez)

```bash
# Crie um banco de teste
sudo mysql -e "CREATE DATABASE petpost_restore_test CHARACTER SET utf8mb4;"

# Restaure o backup
gunzip -c /home/deploy/backups/petpost_XXXXXXXX.sql.gz | \
  sudo mysql petpost_restore_test

# Verifique se as tabelas existem
sudo mysql petpost_restore_test -e "SHOW TABLES;"

# Limpe o banco de teste
sudo mysql -e "DROP DATABASE petpost_restore_test;"
```

Um backup que nunca foi testado não é um backup.

---

## 13. Como atualizar o código em produção

```bash
cd /var/www/petpost

# 1. Baixa as mudanças do GitHub
git pull origin main

# 2. Ativa o ambiente virtual
source venv/bin/activate

# 3. Atualiza dependências (se requirements.txt mudou)
pip install -r requirements.txt

# 4. Aplica migrations (se houver novas)
flask db upgrade

# 5. Reinicia a aplicação (zero-downtime com reload)
sudo systemctl reload petpost  # SIGHUP — recarrega workers sem derrubar o serviço
# ou, se precisar reinício completo:
sudo systemctl restart petpost
```

### Rollback em caso de problema

```bash
# Volta para o commit anterior
git log --oneline -5       # veja os commits recentes
git checkout HASH_DO_COMMIT_ANTERIOR

# Reinicia
sudo systemctl restart petpost
```

---

## 14. O que NÃO fazer em produção

| Ação | Por quê é perigoso |
|------|--------------------|
| `python seeds.py` | Cria admin com senha pública `Admin@123` |
| `flask run` em vez de Gunicorn | Servidor de desenvolvimento, 1 thread, debug possível |
| `DEBUG=True` em qualquer config de produção | Expõe traceback completo, variáveis locais e permite execução de código via Werkzeug debugger |
| Senha de banco no `.env.example` ou em código | Vaza para o repositório público |
| `GRANT ALL ON *.* TO 'petpost_user'` | Usuário da app com acesso a todos os bancos do servidor |
| Ignorar erros 500 nos logs | Podem indicar tentativas de exploração em andamento |
| Subir sem SSL ativo | Senhas e cookies trafegam em texto puro |
| Abrir porta 3306 (MySQL) no firewall | Banco de dados exposto na internet |

---

## Referência rápida

### Serviços e suas funções

```
Internet → Nginx (443/80) → Gunicorn (socket) → Flask app
                                                       ↕
                                                   MySQL (3306, local)
```

### Comandos essenciais

```bash
# Status de tudo
sudo systemctl status petpost nginx mysql fail2ban

# Logs em tempo real
sudo journalctl -u petpost -f

# Reiniciar aplicação
sudo systemctl restart petpost

# Testar configuração do Nginx sem reiniciar
sudo nginx -t && sudo systemctl reload nginx

# Backup manual
/home/deploy/backup-db.sh

# Ver quem o Fail2Ban baniu
sudo fail2ban-client status sshd

# Verificar uso de disco (uploads crescem com o tempo)
df -h
du -sh /var/www/petpost/app/static/uploads/
```
