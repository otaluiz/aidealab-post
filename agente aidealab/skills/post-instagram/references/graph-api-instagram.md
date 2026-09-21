# Instagram Graph API — mecânica de publish

Confirmado por chamada real nesta conta (2026-09-17): o host certo para um
token de System User é `graph.facebook.com` — **não** `graph.instagram.com`
(esse rejeita o token com "cannot parse access token"; é para token de
Instagram Login, não de Business/System User).

`INSTAGRAM_ACCESS_TOKEN` e `INSTAGRAM_BUSINESS_ACCOUNT_ID` vêm de variável
de ambiente — nunca hardcoded.

## Imagem única

```bash
# 1. cria o container
curl -s -X POST "https://graph.facebook.com/v22.0/${INSTAGRAM_BUSINESS_ACCOUNT_ID}/media" \
  --data-urlencode "image_url=${PUBLIC_IMAGE_URL}" \
  --data-urlencode "caption=${CAPTION}" \
  --data-urlencode "access_token=${INSTAGRAM_ACCESS_TOKEN}"
# -> {"id": "<container_id>"}

# 2. confere status antes de publicar (evita publicar container que ainda não processou)
curl -s "https://graph.facebook.com/v22.0/<container_id>?fields=status_code&access_token=${INSTAGRAM_ACCESS_TOKEN}"
# espera status_code == "FINISHED"

# 3. publica
curl -s -X POST "https://graph.facebook.com/v22.0/${INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish" \
  --data-urlencode "creation_id=<container_id>" \
  --data-urlencode "access_token=${INSTAGRAM_ACCESS_TOKEN}"
# -> {"id": "<post_id>"}
```

## Carrossel (até 10 slides)

```bash
# 1. um container por slide, NA ORDEM de slides[].ordem do metadata.json
#    (não é sort de nome de arquivo — a pasta mistura convenção "1-hook.png"
#    e "01_capa.png")
curl -s -X POST "https://graph.facebook.com/v22.0/${INSTAGRAM_BUSINESS_ACCOUNT_ID}/media" \
  --data-urlencode "image_url=${PUBLIC_IMAGE_URL_SLIDE_N}" \
  --data-urlencode "is_carousel_item=true" \
  --data-urlencode "access_token=${INSTAGRAM_ACCESS_TOKEN}"
# -> {"id": "<child_id_N>"}  — repete por slide, sem caption em cada filho

# 2. container pai — caption só aqui, children na ordem certa
curl -s -X POST "https://graph.facebook.com/v22.0/${INSTAGRAM_BUSINESS_ACCOUNT_ID}/media" \
  --data-urlencode "media_type=CAROUSEL" \
  --data-urlencode "children=<child_id_1>,<child_id_2>,...,<child_id_N>" \
  --data-urlencode "caption=${CAPTION}" \
  --data-urlencode "access_token=${INSTAGRAM_ACCESS_TOKEN}"
# -> {"id": "<parent_container_id>"}

# 3. confere status_code == "FINISHED" do parent, depois media_publish igual
#    ao fluxo de imagem única (creation_id = parent_container_id)
```

Limite: 10 itens por carrossel (nenhum post aprovado hoje passa disso).

## Erros e limites a tratar

- `image_url` **tem** que ser pública e acessível no momento da chamada —
  se vier erro de fetch, confere se o upload no Supabase terminou e se o
  bucket é público antes de tentar de novo.
- Container expira em 24h sem publish — por isso criar e publicar na mesma
  execução, nunca com antecedência.
- Rate limit: 25 posts publicados / 24h por conta. Cada disparo desta
  skill publica só 1 peça — não estourar lote.
- Erro de permissão (`code 100`/`error_subcode 33`, "object does not
  exist") geralmente significa o System User perdeu/nunca teve o asset
  atribuído no Business Manager — não é bug de código, é acesso. Ver
  pré-requisito no `SKILL.md`.

## Verificação de identidade/permissão (debug, não publica nada)

```bash
curl -s "https://graph.facebook.com/v22.0/me?access_token=${INSTAGRAM_ACCESS_TOKEN}"
curl -s "https://graph.facebook.com/v22.0/debug_token?input_token=${INSTAGRAM_ACCESS_TOKEN}&access_token=${INSTAGRAM_ACCESS_TOKEN}"
curl -s "https://graph.facebook.com/v22.0/me/accounts?access_token=${INSTAGRAM_ACCESS_TOKEN}"
```
