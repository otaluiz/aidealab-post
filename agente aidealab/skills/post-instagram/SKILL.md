---
name: post-instagram
description: Publica no Instagram (@aidealab7) o próximo conteúdo aprovado da pasta `Clientes/aidealab/06-Aprovados-para-Postar` no Drive — imagem única ou carrossel, lendo legenda/hashtags/ordem do `metadata.json` de cada peça. Dispara com "postar próximo", "postar <nome-do-post>", ou sozinha via cron (rotina agendada). Respeita o portão humano da pasta — só publica o que já está aprovado ali, nunca gera conteúdo novo (isso é `criar-post`). Idempotente: pula qualquer peça com `postado:true`.
---

# Postar no Instagram

Publica de verdade, via Instagram Graph API, o próximo conteúdo aprovado em
`Clientes/aidealab/06-Aprovados-para-Postar` no Drive. Não gera arte nem copy
— isso é responsabilidade da `criar-post`. Esta skill só lê o que já foi
aprovado (pasta = portão humano) e publica.

Roda tanto por comando manual quanto sozinha via rotina agendada (cron) —
sem depender da máquina local ligada: toda leitura/escrita usa a API do
Drive (MCP), nunca o path local do disco, e a imagem sobe pra um bucket
público temporário antes de entrar na chamada da Graph API.

## Quando usar

"postar próximo", "postar <nome>", ou disparo automático via cron.

## Pré-requisito (verificar antes do primeiro post real)

O token do System User `aidealab_admin` precisa estar **atribuído como
ativo** à Page/conta @idea_lab7 no Meta Business Manager — não basta ter os
scopes no app. Teste rápido:

```bash
curl -s "https://graph.facebook.com/v22.0/me/accounts?access_token=$INSTAGRAM_ACCESS_TOKEN"
```

Se vier `{"data":[]}`, o acesso ainda não foi liberado — para e avisa o
usuário (Configurações do Negócio → Usuários do Sistema → `aidealab_admin` →
Atribuir ativos → Page, controle total). Não adianta repetir a chamada, é
ação manual no Business Manager.

## Credenciais

`INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`,
`SUPABASE_SERVICE_ROLE_KEY` vêm de variável de ambiente / secret da rotina
agendada — **nunca em texto puro no repo**. Se algum desses não estiver
setado, para e avisa; não hardcoda valor de teste.

## Arquitetura

- **Fonte de dados**: API do Drive (MCP), nunca o path local do disco —
  funciona igual rodando manual ou via cron sem a máquina ligada.
- **Fila**: qualquer subpasta de `01-Imagem` ou `02-carrossel` com
  `metadata.json`/`*.metadata.json` e `postado:false` é candidata. Ordena
  por `data_criacao` (mais antigo primeiro); usa o nome da pasta/arquivo
  como desempate. Ignora sempre `desktop.ini`.
- **Hospedagem temporária de imagem**: bucket público `ig-publish` no
  projeto Supabase `aidealab` (`jrfjjpxjkpvuvvycyryj`) — mesmo projeto do
  bot de WhatsApp, bucket isolado, nenhuma tabela do bot é tocada. Sobe
  cada imagem só na hora de publicar, apaga o blob depois do
  `media_publish` confirmado.
- **Publish**: ver `references/graph-api-instagram.md` — fluxo de 2 passos
  (container → publish), host `graph.facebook.com`, carrossel com
  containers filhos.
- **Schema do conteúdo**: ver `references/metadata-schema.md`.

## Procedimento

1. **Ler a fila.** Via Drive API, lista `06-Aprovados-para-Postar/01-Imagem`
   e `06-Aprovados-para-Postar/02-carrossel` (recursivo), lê cada
   `metadata.json`/`*.metadata.json`, filtra `postado:false`, ordena por
   `data_criacao`. Se um nome específico foi pedido ("postar <nome>"),
   busca só aquele; se não existir ou já estiver postado, avisa e para.
2. **Confirmar antes de publicar de verdade** (disparo manual): mostra pro
   usuário qual peça vai publicar (tema, legenda, prévia do texto de cada
   slide) e só publica após confirmação explícita — a menos que o disparo
   seja via cron (rotina já aprovada previamente pelo usuário ao configurar
   o agendamento).
3. **Baixar as imagens** da peça via `download_file_content` (Drive API).
4. **Subir pro Supabase Storage** (`references/supabase-storage.md`) — uma
   URL pública por imagem/slide.
5. **Publicar** seguindo `references/graph-api-instagram.md`:
   - Imagem única → 1 container (`image_url`+`caption`) → `media_publish`.
   - Carrossel → N containers filhos (`is_carousel_item:true`) → container
     pai (`media_type:CAROUSEL`+`children`+`caption`, ordem = `slides[].ordem`
     do metadata, nunca sort de nome de arquivo) → `media_publish`.
6. **Apagar os blobs** do bucket `ig-publish` depois do publish confirmado.
7. **Gravar o resultado** de volta no `metadata.json` via Drive API
   (`update_file`): `postado:true`, `postado_em:<iso 8601>`,
   `post_id:<id retornado>`. Se a publicação falhar, **não** marca
   `postado:true` — deixa pra próxima tentativa e reporta o erro.
8. **Reportar**: o que foi publicado (link do post se disponível via
   `permalink`), e qual é o próximo item da fila.

## Agendamento (cron)

Configurado à parte, via rotina agendada (`schedule`/`CronCreate`), num
horário combinado com o usuário. Cada disparo do cron roda o procedimento
acima sem pedir confirmação passo 2 (a aprovação já foi dada ao configurar
o agendamento) — mas continua não publicando nada com `postado:true`, e
continua parando se a fila estiver vazia ou se faltar credencial.

## Limites e proteções

- **25 posts publicados / 24h** por conta — a skill não força lote; cada
  disparo publica só 1 peça (a próxima da fila).
- **Container expira em 24h** — por isso a imagem é enviada pro bucket e
  publicada na mesma execução, nunca pré-processada com antecedência.
- **Nunca republica** algo com `postado:true` — proteção contra duplicata
  em reexecução ou corrida entre disparo manual e cron.

## Fora de escopo

- Gerar arte, copy, legenda ou hashtag — isso é `criar-post`; esta skill só
  publica o que já está aprovado em `06-Aprovados-para-Postar`.
- Editar ou mover o conteúdo já publicado (fica no Drive como histórico,
  só com `postado:true` gravado).
- Postar Stories/Reels — cobre feed (imagem única e carrossel) por
  enquanto.
