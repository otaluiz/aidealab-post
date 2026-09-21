# Hospedagem temporária de imagem — Supabase Storage

A Graph API só aceita `image_url` público (sem upload direto de arquivo).
Como a fonte é o Drive (via API, sem path local), cada imagem sobe pro
bucket `ig-publish` só na hora de publicar, e é apagada depois.

- **Projeto**: `aidealab` (`jrfjjpxjkpvuvvycyryj`, região `sa-east-1`) — o
  mesmo projeto do bot de WhatsApp do usuário. Bucket isolado, nenhuma
  tabela/schema do bot é tocada.
- **Bucket**: `ig-publish`, público (leitura pública, só a chave
  `service_role` escreve).
- **URL pública de um objeto**: `https://jrfjjpxjkpvuvvycyryj.supabase.co/storage/v1/object/public/ig-publish/<path>`.
- **Credencial**: `SUPABASE_SERVICE_ROLE_KEY` — variável de ambiente,
  nunca hardcoded. É a service_role key (não a publishable/anon), porque é
  upload/delete server-side de automação, não acesso de usuário final.

## Criar o bucket (uma vez, via SQL)

Sem tool dedicada de "criar bucket" no MCP do Supabase — usa `execute_sql`
contra `storage.buckets`:

```sql
insert into storage.buckets (id, name, public)
values ('ig-publish', 'ig-publish', true)
on conflict (id) do nothing;
```

E uma policy de leitura pública (upload/delete continuam restritos por
usar a `service_role` key, que ignora RLS):

```sql
create policy "ig-publish public read"
on storage.objects for select
using (bucket_id = 'ig-publish');
```

## Upload (por imagem, na hora de publicar)

```bash
curl -s -X POST \
  "https://jrfjjpxjkpvuvvycyryj.supabase.co/storage/v1/object/ig-publish/<post_id>/<slide>.png" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: image/png" \
  --data-binary "@<caminho_local_temp_do_arquivo_baixado_do_drive>"
```

URL pública resultante:
`https://jrfjjpxjkpvuvvycyryj.supabase.co/storage/v1/object/public/ig-publish/<post_id>/<slide>.png`

## Delete (depois do media_publish confirmado)

```bash
curl -s -X DELETE \
  "https://jrfjjpxjkpvuvvycyryj.supabase.co/storage/v1/object/ig-publish/<post_id>/<slide>.png" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}"
```

Apaga sempre — mesmo em caso de falha no publish, limpa o que já subiu
antes de reportar o erro (não deixa lixo acumulando no bucket).
