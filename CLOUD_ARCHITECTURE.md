# Cloud Architecture - Instagram Publishing

## Problem
Sistema de publicação no Instagram depende do PC estar ligado (Google Drive local) e requer execução manual ou GitHub Actions com horário fixo.

## Solution
Arquitetura cloud-nativa que funciona 100% sem depender do PC, com múltiplas camadas de redundância.

## Architecture

### 1. GitHub Actions Workflows

#### `post-instagram-cloud.yml` (NOVO - Principal)
- **Trigger**: A cada 30 minutos (sem PC ligado)
- **Job**: Executa `publish_next.py`
- **Fallback**: Se falhar, continua no próximo ciclo
- **Features**:
  - Roda a cada 30 min (não apenas 1x ao dia)
  - `workflow_dispatch` para publicação manual
  - `--force` flag para ignorar guarda de 1-post-per-dia
  - Notifica Supabase Edge Function como backup

#### `post-instagram-daily.yml` (Mantém compatibilidade)
- Original, roda 1x ao dia em horário fixo
- Útil como redundância

### 2. Supabase Edge Function (Serverless)

**Path**: `/supabase/functions/publish-instagram/index.ts`

Roda fora do ambiente cloud bloqueado, com acesso real à internet:

```
Client → GitHub Actions → Supabase Edge Function → Instagram Graph API
                                                  ↓
                                            Supabase Storage (upload)
```

**Features**:
- Lê fila do repo via GitHub Raw API (sem clone local)
- Download de imagens do Drive/GitHub
- Upload para Supabase Storage
- Publicação no Instagram
- Atualização da metadata (via commit webhook)

### 3. Queue System

**Localização**: `agente aidealab/skills/post-instagram/queue/FILA-SEMANA-1/02-carrossel/`

```
metadata.json:
{
  "carousel_id": "Dia11-importancia-do-design",
  "postado": false,          ← Script verifica isso
  "postado_em": null,
  "post_id": null,
  "slides": [
    {"arquivo": "1.png", "ordem": 1},
    {"arquivo": "2.png", "ordem": 2}
  ]
}
```

### 4. Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (a cada 30min)             │
│  - Executa publish_next.py                                  │
│  - Faz upload para Supabase Storage                         │
│  - Publica no Instagram                                     │
│  - Atualiza metadata.json                                   │
│  - Push para repo                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─→ Sucesso? Metadata marcada postado:true
                       │
                       └─→ Falha? Retry no próximo ciclo (30min)
                       
┌──────────────────────────────────────────────────────────────┐
│         Supabase Edge Function (backup serverless)           │
│  - Chamada opcional do GitHub Actions                        │
│  - Funciona fora do proxy bloqueado                          │
│  - API HTTP endpoint para disparo manual                     │
│  - Idempotente (seguro chamar múltiplas vezes)             │
└──────────────────────────────────────────────────────────────┘
```

## Deployment

### 1. Secrets no GitHub
Garantir que existem:
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_BUSINESS_ACCOUNT_ID`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_URL`

### 2. Supabase Edge Function
```bash
# Deploy local first:
supabase functions deploy publish-instagram

# Ou via Supabase CLI
supabase functions deploy publish-instagram --no-verify-jwt
```

### 3. Secrets no Supabase
```bash
supabase secrets set INSTAGRAM_ACCESS_TOKEN=xxx
supabase secrets set INSTAGRAM_BUSINESS_ACCOUNT_ID=xxx
```

## Usage

### Publicação Automática (Default)
- Roda a cada 30 minutos automaticamente
- Sem ação necessária

### Publicação Manual
**Via GitHub Actions UI**:
1. Actions → post-instagram-cloud
2. Run Workflow
3. Opcional: force_publish = true (ignora guarda de 1-post-per-dia)

**Via Curl** (se Edge Function estiver rodando):
```bash
curl -X POST \
  "https://[PROJECT].supabase.co/functions/v1/publish-instagram" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"repo":"otaluiz/aidealab-post","branch":"main"}'
```

## Fallback Chain

Se um falhar, o sistema tenta o próximo:

1. **GitHub Actions** (primary) - a cada 30min
   - ✓ Tem acesso à credenciais
   - ✓ Pode fazer commit no repo
   - ✗ Corre dentro do proxy bloqueado (Instagram falha)

2. **Supabase Edge Function** (secondary) - chamada do GA
   - ✓ Roda fora do proxy
   - ✓ Acesso direto a Instagram
   - ✗ Não pode fazer commit (precisaria de webhook)

3. **Manual Dispatch** (manual) - via UI ou webhook
   - ✓ Controle total
   - ✗ Requer intervenção manual

## Monitoring

### Log dos Commits
```bash
git log --grep="chore(post-instagram)" --oneline
```

### Verificar Fila
```bash
for dir in agente\ aidealab/skills/post-instagram/queue/FILA-SEMANA-1/02-carrossel/*/; do
  basename "$dir"
  jq '.postado, .postado_em' "$dir/metadata.json"
done
```

### GitHub Actions Runs
```bash
gh run list --workflow post-instagram-cloud.yml
```

## Troubleshooting

### Publish falha com "connect_rejected"
- Esperado em cloud sessions (proxy bloqueado)
- GitHub Actions roda fora do proxy - tenta novamente ali
- Edge Function é alternativa (requer Supabase deployment)

### Metadata não atualiza
- Check: `git push` no final do workflow
- Check: Permissions no GitHub Actions (contents:write)

### Mesmo item tenta publicar 2x
- Guarda de `already_posted_today()` previne
- Use `--force` se realmente precisar forçar

## Future Improvements

- [ ] Webhook do Supabase → Auto-commit updates
- [ ] Verificação de imagens antes de publicar
- [ ] Notificação por email/Slack
- [ ] Dashboard de status da fila
- [ ] Scheduling de publicações (pré-selecionar qual dia)
