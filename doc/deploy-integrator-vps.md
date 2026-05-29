# Guia de Deploy — PetPost na Integrator VPS

**Para quem é este guia:** alguém com conhecimento básico de terminal que nunca fez deploy de uma aplicação Flask em servidor real.

**O que você vai ter ao final:** PetPost rodando em `https://seudominio.com.br` com SSL, MySQL, Nginx e reinicialização automática.

**Tempo estimado:** 2 a 3 horas na primeira vez.

---

## Índice

1. [Pré-requisitos e custos](#1-pré-requisitos-e-custos)
2. [Auditoria pré-deploy — o que verificar antes de subir](#2-auditoria-pré-deploy--o-que-verificar-antes-de-subir)
3. [Contratar a VPS na Integrator](#3-contratar-a-vps-na-integrator)
4. [Registrar o domínio no Registro.br](#4-registrar-o-domínio-no-registrobr)
5. [Primeiro acesso via SSH](#5-primeiro-acesso-via-ssh)
6. [Configuração inicial do servidor](#6-configuração-inicial-do-servidor)
7. [Instalar Python, MySQL e Nginx](#7-instalar-python-mysql-e-nginx)
8. [Subir o código da aplicação](#8-subir-o-código-da-aplicação)
9. [Configurar o banco de dados](#9-configurar-o-banco-de-dados)
10. [Configurar variáveis de ambiente](#10-configurar-variáveis-de-ambiente)
11. [Configurar Gunicorn como serviço](#11-configurar-gunicorn-como-serviço)
12. [Configurar Nginx como proxy reverso](#12-configurar-nginx-como-proxy-reverso)
13. [Apontar o domínio para a VPS](#13-apontar-o-domínio-para-a-vps)
14. [SSL gratuito com Let's Encrypt](#14-ssl-gratuito-com-lets-encrypt)
15. [Checklist final, manutenção e backups](#15-checklist-final-manutenção-e-backups)

---

## 1. Pré-requisitos e custos

### O que você vai precisar

| Item | Onde | Custo estimado |
|------|------|---------------|
| VPS Linux na Integrator | [integrator.com.br/plano-vps-linux](https://www.integrator.com.br/plano-vps-linux) | ~R$ 60–90/mês |
| Domínio `.com.br` | [registro.br](https://registro.br) | ~R$ 40/ano |
| Terminal SSH | Já vem no macOS/Linux. No Windows 11: Terminal nativo. Windows 10: instale o [PuTTY](https://putty.org) | grátis |
| Código no GitHub | [github.com](https://github.com) | grátis |

**Total:** ~R$ 100–130 no primeiro mês, depois ~R$ 60–90/mês.

### Antes de começar, tenha em mãos

- CPF (para registrar o domínio)
- Cartão de crédito ou conta para Pix/boleto
- O repositório do PetPost no GitHub
- Cerca de **2 a 3 horas** disponíveis

---

## 2. Auditoria pré-deploy — o que verificar antes de subir

Antes de tocar no servidor, confirme esses pontos no seu projeto local. Um estagiário pularia essa etapa — não pule.

### 2.1 Verifique o que está (e o que não está) no Git

No terminal, dentro da pasta do projeto:

```bash
git status
git log --oneline -5
```

Confirme que **nenhum desses arquivos aparece no `git status`** como rastreado:

```
.env                 ← contém suas senhas reais
venv/                ← ambiente virtual, pesado e desnecessário no servidor
app/static/uploads/  ← fotos enviadas por usuários
*.pyc / __pycache__  ← bytecode gerado automaticamente
```

Se algum deles aparecer como "tracked", pare aqui e resolva antes de continuar. O `.gitignore` do projeto já os exclui corretamente — verifique se o arquivo está íntegro.

### 2.2 Confirme que o `.env.example` só tem placeholders

```bash
cat .env.example
```

O arquivo deve ter **apenas valores de exemplo** — nunca senhas reais:

```bash
SECRET_KEY=mude-essa-chave-em-producao-gere-uma-aleatoria
DATABASE_URL=mysql+pymysql://petpost_user:petpost123@localhost/petpost_dev
```

Se tiver uma senha real lá, troque por um placeholder antes de fazer `git push`.

### 2.3 Rode os testes

```bash
pytest -v
```

Os 25 testes devem passar. **Não suba código quebrado para produção.**

### 2.4 Certifique-se que o código está no GitHub

```bash
git push origin main
```

O servidor vai baixar o código diretamente do GitHub. O que não estiver lá, não vai para o servidor.

### ⚠️ Atenção: seeds.py em produção

O arquivo `seeds.py` cria um usuário admin com a senha `Admin@123` — uma senha que qualquer um que leu o repositório conhece. **Nunca rode `python seeds.py` em produção.** Você vai criar o banco e as tabelas manualmente, como mostrado no passo 9.

---

## 3. Contratar a VPS na Integrator

### Qual plano escolher

Acesse **[integrator.com.br/plano-vps-linux](https://www.integrator.com.br/plano-vps-linux)** e escolha um plano com:

- **Mínimo para o PetPost:** 1 vCPU / 1 GB RAM / 20 GB SSD
- **Recomendado:** 2 vCPU / 2 GB RAM / 40 GB SSD

O PetPost é uma aplicação leve. O plano mínimo aguenta bem em produção acadêmica.

### Passo a passo

1. Acesse o site, clique em **"VPS Linux"** e escolha o plano
2. Na tela de configuração, selecione:
   - **Sistema Operacional:** Ubuntu 22.04 LTS
   - **Localização:** São Paulo (menor latência para o Brasil)
3. Finalize o pagamento
4. Em 5 a 30 minutos você receberá um e-mail com:
   - O **IP da VPS** (ex: `200.100.50.10`)
   - A **senha root temporária**
   - Link para o painel ICP da Integrator

> **Guarde esse e-mail.** O IP e a senha estão nele.

---

## 4. Registrar o domínio no Registro.br

O [Registro.br](https://registro.br) é o órgão oficial para domínios `.com.br`. É mais barato e confiável do que comprar em revendedores.

### Passo a passo

**1. Crie uma conta**

Acesse [registro.br](https://registro.br) → **"Criar conta"** → preencha com seus dados pessoais e CPF.

**2. Pesquise o domínio**

Na barra de busca, digite o nome desejado, ex: `petpost.com.br`. Se aparecer **"disponível"**, pode seguir.

> **Dica:** escolha algo curto, sem hífen e fácil de falar. `petpost.com.br`, `encontrapets.com.br` ou `petpostbr.com.br` são boas opções.

**3. Finalize o pagamento**

- Preço: ~R$ 40/ano para `.com.br`
- Aceita Pix, boleto e cartão
- A ativação é imediata após a confirmação

**4. Confirme no painel**

Vá em **"Meus Domínios"** — o domínio deve aparecer como **"Ativo"**.

> O domínio está registrado mas ainda não aponta para nenhum servidor. Isso é normal — vamos configurar no passo 13, depois de subir o servidor.

---

## 5. Primeiro acesso via SSH

SSH é o protocolo que permite controlar o servidor remotamente pelo terminal.

### Conectar pela primeira vez

**macOS / Linux** — abra o Terminal e execute:

```bash
ssh root@SEU_IP_AQUI
```

Exemplo:
```bash
ssh root@200.100.50.10
```

Na primeira conexão aparece esta mensagem:
```
The authenticity of host '200.100.50.10' can't be established.
Are you sure you want to continue connecting (yes/no)?
```

Digite `yes` e pressione Enter. Em seguida, cole a senha do e-mail da Integrator.

> Ao digitar a senha no Linux/Mac, os caracteres não aparecem na tela — isso é normal e proposital. Digite e pressione Enter.

**Windows** — abra o **Terminal do Windows** e use o mesmo comando. No Windows 10 sem Terminal nativo, use o PuTTY: coloque o IP no campo "Host Name" e clique em "Open".

### Como saber que funcionou

Você verá algo assim:
```
Welcome to Ubuntu 22.04.4 LTS
root@vps-petpost:~#
```

O `#` no final indica que você está como root no servidor.

---

## 6. Configuração inicial do servidor

Nunca rode a aplicação como root. Vamos criar um usuário dedicado, atualizar o sistema e ativar o firewall.

### 6.1 Atualizar o sistema

```bash
apt update && apt upgrade -y
```

> `apt update` busca as atualizações disponíveis. `apt upgrade -y` instala todas. Isso pode demorar 3 a 5 minutos.

### 6.2 Criar o usuário da aplicação

```bash
adduser deploy
```

O terminal vai pedir uma senha. Crie uma senha forte e **anote ela** — você vai precisar para acessar o servidor sem root.

Nas perguntas seguintes (Full Name, Room Number etc.), pressione Enter para pular todas.

Dê poderes de administrador a esse usuário:
```bash
usermod -aG sudo deploy
```

### 6.3 Configurar o firewall

```bash
ufw allow OpenSSH        # porta 22 — acesso SSH
ufw allow 'Nginx Full'   # portas 80 (HTTP) e 443 (HTTPS)
ufw enable
```

Quando perguntar `Proceed with operation (y|n)?`, digite `y`.

Verifique que está ativo:
```bash
ufw status
```

Saída esperada:
```
Status: active
OpenSSH                    ALLOW
Nginx Full                 ALLOW
```

> **Nunca feche a porta SSH (22).** Se fechar por engano, você perde acesso ao servidor.

### 6.4 Trocar para o usuário deploy

```bash
su - deploy
```

O prompt muda de `root@...#` para `deploy@...$`. A partir daqui, **use sempre o usuário deploy**.

---

## 7. Instalar Python, MySQL e Nginx

```bash
sudo apt install -y \
  python3 python3-pip python3-venv \
  mysql-server \
  nginx \
  git \
  certbot python3-certbot-nginx
```

> Instala tudo de uma vez. Pode demorar ~3 minutos.

Confirme que o Python foi instalado:
```bash
python3 --version
# Python 3.10.x ou superior
```

### 7.1 Iniciar o MySQL

```bash
sudo systemctl start mysql
sudo systemctl enable mysql
```

> `enable` faz o MySQL iniciar automaticamente quando o servidor reiniciar.

### 7.2 Proteger o MySQL

```bash
sudo mysql_secure_installation
```

Responda as perguntas assim:

| Pergunta | Resposta |
|----------|----------|
| Setup VALIDATE PASSWORD? | `N` |
| Set password for root? | Digite uma senha forte — **anote ela** |
| Remove anonymous users? | `Y` |
| Disallow root login remotely? | `Y` |
| Remove test database? | `Y` |
| Reload privilege tables? | `Y` |

### 7.3 Verificar o Nginx

```bash
sudo systemctl status nginx
```

Se aparecer `active (running)`, está ok. Abra `http://SEU_IP` no navegador e veja a página padrão do Nginx — isso confirma que o servidor web está funcionando.

---

## 8. Subir o código da aplicação

### 8.1 Criar o diretório e dar permissão

```bash
sudo mkdir -p /var/www/petpost
sudo chown deploy:deploy /var/www/petpost
```

### 8.2 Clonar o repositório

```bash
cd /var/www/petpost
git clone https://github.com/SEU_USUARIO/petpost.git .
```

> O `.` no final clona **dentro** da pasta atual, sem criar uma subpasta.

**Se o repositório for privado**, use um token do GitHub:

```bash
git clone https://SEU_TOKEN@github.com/SEU_USUARIO/petpost.git .
```

Para gerar o token: GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic) → Generate new token → marque `repo` → copie.

### 8.3 Criar o ambiente virtual Python

```bash
python3 -m venv venv
source venv/bin/activate
```

O prompt muda para `(venv) deploy@...` — isso confirma que o ambiente está ativo.

### 8.4 Instalar as dependências

```bash
pip install -r requirements.txt
pip install gunicorn
```

> O `gunicorn` não está no `requirements.txt` porque em desenvolvimento usamos `flask run`. Em produção, o Gunicorn é o servidor de verdade.

---

## 9. Configurar o banco de dados

### 9.1 Criar o banco e o usuário

```bash
sudo mysql
```

Você verá o prompt `mysql>`. Execute cada bloco abaixo **um de cada vez**:

```sql
CREATE DATABASE petpost_prod
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

```sql
CREATE USER 'petpost_user'@'localhost'
  IDENTIFIED BY 'SUA_SENHA_FORTE_AQUI';
```

```sql
GRANT ALL PRIVILEGES ON petpost_prod.*
  TO 'petpost_user'@'localhost';
```

```sql
FLUSH PRIVILEGES;
EXIT;
```

> Substitua `SUA_SENHA_FORTE_AQUI` por uma senha real. Ex: `P3tP0$t_Pr0d_2024!`. **Anote ela** — vai no `.env` no próximo passo.

---

## 10. Configurar variáveis de ambiente

Dentro de `/var/www/petpost`, crie o arquivo `.env`:

```bash
nano .env
```

> O `nano` é um editor de texto simples. Para **salvar:** `Ctrl+O` → Enter. Para **sair:** `Ctrl+X`.

Cole e preencha o conteúdo abaixo:

```bash
FLASK_APP=run.py
FLASK_CONFIG=production

SECRET_KEY=COLE_AQUI_A_CHAVE_GERADA

DATABASE_URL=mysql+pymysql://petpost_user:SUA_SENHA_FORTE_AQUI@localhost/petpost_prod
```

**Como gerar a SECRET_KEY:** abra um terminal na sua **máquina local** (não no servidor) e execute:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado e cole no `.env` no servidor.

Salve o arquivo (`Ctrl+O` → Enter → `Ctrl+X`).

Proteja o arquivo para que só o dono possa lê-lo:

```bash
chmod 600 .env
```

### 10.1 Criar as tabelas no banco

```bash
source venv/bin/activate
flask db upgrade
```

Se der algum erro, use o comando alternativo:

```bash
flask create-db
```

Nenhuma mensagem de erro = tudo certo.

> **Lembrete:** não rode `python seeds.py` aqui. Isso criaria um admin com senha pública conhecida. Crie o admin manualmente conforme o passo 15.

---

## 11. Configurar Gunicorn como serviço

### 11.1 Criar o arquivo de serviço

```bash
sudo nano /etc/systemd/system/petpost.service
```

Cole exatamente o conteúdo abaixo:

```ini
[Unit]
Description=PetPost — Gunicorn WSGI server
After=network.target

[Service]
User=deploy
Group=www-data
WorkingDirectory=/var/www/petpost
EnvironmentFile=/var/www/petpost/.env
ExecStart=/var/www/petpost/venv/bin/gunicorn \
          --workers 2 \
          --bind unix:/var/www/petpost/petpost.sock \
          --timeout 30 \
          --max-requests 1000 \
          --max-requests-jitter 100 \
          run:app
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Salve (`Ctrl+O` → Enter → `Ctrl+X`).

> **O que cada opção significa:**
> - `--workers 2` → 2 processos paralelos (suficiente para uso acadêmico)
> - `--bind unix:...sock` → comunicação com Nginx por socket Unix (mais rápido que TCP)
> - `--timeout 30` → cancela requisições que demoram mais de 30 segundos
> - `--max-requests 1000` → reinicia o processo a cada 1000 requisições (evita acúmulo de memória)
> - `Restart=on-failure` → reinicia automaticamente se a aplicação travar

### 11.2 Ativar e iniciar

```bash
sudo systemctl daemon-reload
sudo systemctl enable petpost
sudo systemctl start petpost
```

Verifique se está rodando:

```bash
sudo systemctl status petpost
```

Saída esperada:
```
● petpost.service - PetPost — Gunicorn WSGI server
   Active: active (running) since ...
```

Se aparecer erro, veja os logs:
```bash
sudo journalctl -u petpost -n 50
```

---

## 12. Configurar Nginx como proxy reverso

### 12.1 Criar a configuração do site

```bash
sudo nano /etc/nginx/sites-available/petpost
```

Cole o conteúdo abaixo. **Substitua `seudominio.com.br` pelo seu domínio real:**

```nginx
server {
    listen 80;
    server_name seudominio.com.br www.seudominio.com.br;

    # Limite de tamanho de upload — deve bater com o Flask (8MB)
    client_max_body_size 10M;

    # Arquivos estáticos servidos diretamente pelo Nginx
    location /static/ {
        alias /var/www/petpost/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Pasta de uploads com proteção contra execução de scripts
    location /static/uploads/ {
        alias /var/www/petpost/app/static/uploads/;
        add_header X-Content-Type-Options nosniff;
        default_type application/octet-stream;
        expires 30d;
    }

    # Todo o resto vai para o Gunicorn
    location / {
        proxy_pass http://unix:/var/www/petpost/petpost.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30;
    }
}
```

### 12.2 Ativar o site e testar

```bash
sudo ln -s /etc/nginx/sites-available/petpost /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
```

Saída esperada:
```
nginx: the configuration file syntax is ok
nginx: configuration file test is successful
```

```bash
sudo systemctl reload nginx
```

**Teste rápido:** abra `http://SEU_IP` no navegador. Se aparecer a aplicação PetPost, o Nginx + Gunicorn estão funcionando.

---

## 13. Apontar o domínio para a VPS

### 13.1 No painel do Registro.br

1. Acesse [registro.br](https://registro.br) → **Entrar** → **"Meus Domínios"**
2. Clique no seu domínio → **"Editar zona DNS"**
3. Crie ou edite os registros do tipo **A**:

| Tipo | Nome | Valor | TTL |
|------|------|-------|-----|
| A | `@` | `200.100.50.10` ← IP da sua VPS | 3600 |
| A | `www` | `200.100.50.10` ← mesmo IP | 3600 |

Salve as alterações.

### 13.2 Aguardar a propagação

Mudanças de DNS levam de **5 minutos a 24 horas** para propagar. No Brasil, costuma ser 15 a 30 minutos.

Verifique pela sua máquina local:
```bash
nslookup petpost.com.br
# Deve retornar o IP da VPS
```

> **Não avance para o próximo passo** enquanto o domínio não estiver apontando para o IP correto. O certificado SSL vai falhar se o DNS ainda não propagou.

---

## 14. SSL gratuito com Let's Encrypt

### 14.1 Instalar o certificado

```bash
sudo certbot --nginx -d seudominio.com.br -d www.seudominio.com.br
```

Durante o processo:

| Pergunta | Resposta |
|----------|----------|
| Enter email address | `seu@email.com` |
| Agree to terms? | `A` |
| Share email with EFF? | `N` |

Ao terminar:
```
Successfully received certificate.
Congratulations! Your certificate and chain have been saved.
```

### 14.2 Verificar renovação automática

```bash
sudo systemctl status certbot.timer
# Deve aparecer: active

sudo certbot renew --dry-run
# Deve aparecer: all simulated renewals succeeded
```

### 14.3 Teste final

Abra `https://seudominio.com.br` no navegador. Você deve ver o **cadeado verde** e a aplicação funcionando. `http://` deve redirecionar automaticamente para `https://`.

---

## 15. Checklist final, manutenção e backups

### Checklist antes de divulgar o link

- [ ] `https://seudominio.com.br` abre a aplicação
- [ ] `http://seudominio.com.br` redireciona para HTTPS
- [ ] Cadastro de usuário funciona
- [ ] Login funciona
- [ ] Upload de foto funciona — crie um post de teste com foto
- [ ] Mapa de parceiros carrega
- [ ] API de CEP responde: `https://seudominio.com.br/api/cep/01310100`
- [ ] Acesse `/admin` sem estar logado — deve redirecionar para login
- [ ] Crie o primeiro admin manualmente (veja abaixo)

### Criar o primeiro admin manualmente

Como não rodamos `seeds.py`, crie o admin pelo console do Flask:

```bash
cd /var/www/petpost
source venv/bin/activate
flask shell
```

No prompt `>>>` que abre:

```python
from app.extensions import db
from app.models.user import User

admin = User(name='Admin', email='admin@seudominio.com.br', role='admin')
admin.set_password('SUA_SENHA_FORTE_AQUI')
db.session.add(admin)
db.session.commit()
print('Admin criado!')
exit()
```

### Comandos de manutenção do dia a dia

```bash
# Logs da aplicação em tempo real (Ctrl+C para parar)
sudo journalctl -u petpost -f

# Reiniciar após atualização de código
sudo systemctl restart petpost

# Erros do Nginx
sudo tail -f /var/log/nginx/error.log

# Acessos ao site
sudo tail -f /var/log/nginx/access.log

# Status de tudo de uma vez
sudo systemctl status petpost nginx mysql
```

### Atualizar o código em produção

```bash
cd /var/www/petpost
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart petpost
```

### Backup automático semanal do banco

```bash
sudo mkdir -p /home/deploy/backups
sudo nano /etc/cron.weekly/backup-petpost
```

Conteúdo:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
mysqldump -u petpost_user -p'SUA_SENHA' petpost_prod > /home/deploy/backups/petpost_$DATE.sql
ls -t /home/deploy/backups/petpost_*.sql | tail -n +5 | xargs rm -f
```

```bash
sudo chmod +x /etc/cron.weekly/backup-petpost
```

---

## Referência rápida de portas e serviços

| Serviço | Porta/Caminho | Quem acessa |
|---------|--------------|-------------|
| SSH | 22 | Só você (terminal) |
| HTTP | 80 | Público (redireciona para HTTPS) |
| HTTPS | 443 | Público |
| Gunicorn | `petpost.sock` | Só o Nginx (internamente) |
| MySQL | 3306 | Só o localhost (firewall bloqueia externo) |

---

## Problemas comuns e soluções

**"502 Bad Gateway"**
```bash
sudo systemctl status petpost
sudo journalctl -u petpost -n 30
sudo systemctl restart petpost
```

**"Permission denied" no socket**
```bash
sudo usermod -aG www-data deploy
sudo systemctl restart petpost nginx
```

**Certificado SSL não instalou**
- Confirme que o DNS propagou: `nslookup seudominio.com.br` deve retornar o IP da VPS
- Confirme que a porta 80 está aberta: `sudo ufw status`

**Aplicação sobe mas mostra erro 500**
```bash
sudo journalctl -u petpost -n 100
# Geralmente é variável de ambiente faltando no .env ou migration não rodada
```

**Atualizei o código mas o site não mudou**
```bash
sudo systemctl restart petpost
# Se ainda não mudou, force o cache do navegador com Ctrl+Shift+R
```
