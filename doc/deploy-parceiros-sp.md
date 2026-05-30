# Deploy dos Parceiros SP — Guia

Arquivo de dados: `seeds_parceiros_sp.py`
Conteúdo: 30 entidades reais do estado de SP (10 petshops, 10 clínicas, 10 lares/ONGs) com coordenadas lat/lng hardcoded.

---

## 1. Copiar o arquivo para a VPS

```bash
scp seeds_parceiros_sp.py usuario@petspost.com.br:/caminho/para/petpost/
```

Ou, se usar deploy via git:

```bash
git add seeds_parceiros_sp.py
git commit -m "feat: seed de parceiros reais do estado de SP"
git push origin main
# Na VPS: git pull
```

---

## 2. Executar na VPS

```bash
# Acessar a VPS
ssh usuario@petspost.com.br

# Ir para o diretório do projeto
cd /caminho/para/petpost

# Ativar o virtualenv
source venv/bin/activate

# Executar o seed (lê FLASK_CONFIG do ambiente ou usa 'production' por padrão)
FLASK_CONFIG=production python seeds_parceiros_sp.py
```

**Saída esperada:**
```
  ✅  "Petz Vila Mariana" adicionado
  ✅  "Petz Mooca" adicionado
  ...
Concluído: 30 adicionados, 0 já existiam.
Total no arquivo: 30 entidades.
```

Se rodar novamente, os registros existentes são pulados (sem duplicatas):
```
  ⏭️  "Petz Vila Mariana" já existe, pulando...
  ...
Concluído: 0 adicionados, 30 já existiam.
```

---

## 3. Verificar no painel admin

Acesse `/admin` → seção Parceiros e confirme que os 30 registros aparecem.

---

## 4. Verificar no mapa público

Acesse `/mapa` no browser. Os marcadores devem aparecer imediatamente (as coordenadas já estão no banco — não depende de geocodificação).

---

## 5. Adicionar novos parceiros

Para adicionar mais entidades depois:

**Opção A — Via painel admin** (`/admin/parceiro/novo`):
- Preencha os dados e salve
- O sistema tentará geocodificar o endereço automaticamente via Nominatim

**Opção B — Via seed**:
- Adicione novas entradas na lista `PARCEIROS` em `seeds_parceiros_sp.py`
- Inclua `lat` e `lng` manualmente (mais confiável que geocodificação automática)
- Execute o script novamente — só os novos serão inseridos

---

## Estrutura dos dados

Cada parceiro suporta os seguintes campos:

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `name` | Sim | Nome do local (máx. 150 chars) |
| `partner_type` | Sim | `'petshop'`, `'vet_clinic'` ou `'foster_home'` |
| `address` | Sim | Endereço completo |
| `lat` | Não | Latitude (aparece no mapa imediatamente) |
| `lng` | Não | Longitude |
| `phone` | Não | Telefone formato `(XX) XXXX-XXXX` |
| `email` | Não | Email de contato |
| `website` | Não | URL completa com `https://` |
| `description` | Não | Texto descritivo |
| `is_active` | Não | `True` = visível no mapa (padrão) |
