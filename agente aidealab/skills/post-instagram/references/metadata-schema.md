# Schema do `metadata.json` em `06-Aprovados-para-Postar`

Congelado a partir do exemplo real já em produção
(`02-carrossel/2026-08-28_importancia-do-design/metadata.json`), estendido
com os campos de estado de postagem que esta skill grava de volta.

## Carrossel — um `metadata.json` por pasta em `02-carrossel/<post>/`

```json
{
  "carousel_id": "2026-08-28_importancia-do-design",
  "cliente": "aidealab",
  "data_criacao": "2026-08-28",
  "status": "aprovado",
  "postado": false,
  "postado_em": null,
  "post_id": null,
  "tema": "importancia do design para negocios",
  "familia_cor": "azul",
  "template": "hook-explicacao-referencia-cta",
  "formato": "1080x1440",
  "slides": [
    { "ordem": 1, "arquivo": "01_capa.png", "papel": "hook", "texto": "..." }
  ],
  "legenda": "texto da legenda, separado do texto dos slides",
  "hashtags": ["#tag1", "#tag2"],
  "handle": "@aidealab7"
}
```

- `slides[].ordem` manda na sequência do carrossel — **nunca** sort de
  nome de arquivo (a pasta tem tanto `1-hook.png` quanto `01_capa.png`).
- `postado_em` (ISO 8601) e `post_id` só existem depois do publish; antes
  disso ficam ausentes ou `null`.

## Imagem única — um arquivo `<nome-da-imagem>.metadata.json` por PNG em `01-Imagem/`

Mesma pasta que as imagens, nome espelhando o arquivo (ex:
`design.png` + `design.metadata.json`) — não há um `metadata.json` único
pra pasta inteira porque cada imagem é um post independente.

```json
{
  "post_id": "design",
  "cliente": "aidealab",
  "tipo": "imagem_unica",
  "arquivo": "design.png",
  "status": "aprovado",
  "postado": false,
  "postado_em": null,
  "tema": "...",
  "familia_cor": "...",
  "formato": "1080x1440",
  "texto": "texto visível na peça (referência, não vai pro Instagram)",
  "legenda": "legenda do post",
  "hashtags": ["#tag1", "#tag2"],
  "handle": "@aidealab7"
}
```

## Idempotência

Só `postado:false` entra na fila. Depois de publicar com sucesso, a skill
regrava `postado:true`, `postado_em:<iso>` e `post_id:<id retornado pela
Graph API>` no mesmo arquivo via Drive API — nunca deleta nem move o
`metadata.json`, o histórico fica no Drive.
