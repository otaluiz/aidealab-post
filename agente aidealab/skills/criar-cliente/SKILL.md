---
name: criar-cliente
description: Garante que a pasta de um cliente da aidealab existe no Google Drive com a estrutura padrão de subpastas, criando o que faltar sem duplicar o que já existe. Se o usuário informar site e/ou Instagram do cliente, analisa e gera `identidade-e-tom.md` em `00-Identidade-e-Tom` — o primeiro conhecimento de marca que as demais skills (criar-post, criar-site) leem. Dispara com "crie cliente <nome>" / "novo cliente <nome>". Idempotente — também serve para completar a estrutura de um cliente já existente.
---

# Criar cliente

Garante, no Google Drive, que a pasta de um cliente dentro de `Clientes`
(parentId `1xHuFxkYD0INTpdZbzBZLRBy-X3tVM-rv`) existe e contém a estrutura
padrão de subpastas — criando apenas o que faltar. É a base das demais skills
da agência (`criar-post`, `criar-site`, e a futura `post-instagram`): elas
localizam a pasta do cliente certo a partir da estrutura que esta skill
garante.

Quando o usuário fornece o site e/ou o Instagram do cliente, a skill também
gera `identidade-e-tom.md` dentro de `00-Identidade-e-Tom` — um documento
estruturado (frontmatter + seções) que é o **primeiro conhecimento de
marca/negócio** que as demais skills (`criar-post`, `criar-site`) leem antes
de qualquer outra coisa.

## Quando usar

Pedido do tipo "crie cliente X" ou "novo cliente X" — opcionalmente com link
de site e/ou Instagram do cliente (ex: "crie cliente X, site
https://... , instagram https://..."). Também serve para completar a
estrutura de um cliente que já existe mas está incompleto (ex: cliente com só
uma pasta de logo solta), ou para gerar/atualizar só o `identidade-e-tom.md`
de um cliente que já tem a estrutura de pastas mas não tem esse documento
ainda — não é exclusivo de cliente novo.

## Estrutura padrão

```
00-Identidade-e-Tom
01-Referencias/
  Instagram
  Site
  Video
02-Materiais-Brutos
03-Roteiros
04-Carrosseis
05-Campanhas
06-Aprovados-para-Postar
```

Lista hardcoded aqui — não é lida dinamicamente de nenhuma pasta modelo a cada
execução. Se o padrão mudar, editar esta lista.

## `identidade-e-tom.md` — formato fixo

Documento único por cliente, salvo em `00-Identidade-e-Tom/identidade-e-tom.md`
como arquivo Markdown real (não converter para Google Doc — usar
`disableConversionToGoogleType: true` no `create_file`, para que
`read_file_content` das demais skills leia texto puro de volta). Frontmatter
YAML com os fatos estruturados + seções em prosa com o contexto. Este formato é
fixo porque `criar-post` e `criar-site` dependem dele para achar rápido cor/
fonte/tom sem reprocessar o site inteiro a cada execução:

```
---
cliente: <nome>
site: <url ou "não informado">
instagram: <url ou "não informado">
tagline: <frase de marca, se houver>
tom_de_voz: <resumo curto>
publico_alvo: <resumo curto>
missao: <se houver>
cores:
  primaria: <hex + nome>
  background: <hex + nome>
  accent: <hex + nome>
tipografia:
  display: <nome da fonte>
  body: <nome da fonte>
fontes_da_analise: [site, instagram_bio, ...]
gerado_em: <data>
---

## Quem é
## Serviços / o que oferece
## Diferenciais
## Prova social (se houver)
## Direção visual
## Notas
```

Cores/tipografia vêm, sempre que possível, de leitura real dos tokens
CSS/design system do site (não estimativa visual) — ver "Procedimento", passo
6. `## Notas` registra o que ficou pendente (ex: referência visual que não pôde
ser lida, arquivo de logo ainda não enviado) sem bloquear o resto do documento.

## Ferramentas necessárias

MCP do Google Drive já conectado à conta. Usa:
- `search_files` — checar existência por `parentId` + `title`.
- `create_file` com `mimeType: application/vnd.google-apps.folder` — criar
  pasta (cliente, pasta de topo, subpasta de `01-Referencias`).
- `create_file` com `contentMimeType: text/markdown` e
  `disableConversionToGoogleType: true` — salvar `identidade-e-tom.md`.

Não há ferramenta de renomear/mover/deletar no Drive MCP conectado. Qualquer
correção desse tipo fica a cargo do usuário, manualmente.

Para ler site/Instagram (passo 6 do procedimento): a ferramenta de navegador
(preview/`get_page_text`) é preferida sobre WebFetch simples para o site,
porque sites construídos pela própria `criar-site` (React/Next.js) são
SPAs — o HTML estático não tem o conteúdo, só o DOM renderizado tem. Um
`javascript_tool` de leitura de `getComputedStyle`/CSS custom properties no
navegador é o caminho para pegar cores/fontes reais em vez de estimar
visualmente. Para o Instagram, WebFetch no link do perfil já traduz a bio; o
conteúdo visual de posts (ex: referências de paleta/fonte que o usuário
mandar) fica bloqueado por login do Instagram — nesse caso, pedir ao usuário
para enviar a imagem diretamente no chat em vez de insistir no link.

## Procedimento

1. **Receber o nome do cliente** do pedido do usuário — e, se fornecidos,
   os links de site e/ou Instagram.
2. **Normalizar para minúsculas** — padrão observado nas pastas existentes
   ("hora da chipa", "cantinho mineiro", "sieger"). Evita duplicar cliente por
   diferença de maiúscula/minúscula.
3. **Buscar dentro de `Clientes`** (parentId fixo acima) por pasta cujo título
   bata, case-insensitive, com o nome normalizado.
4. **Se não existir, criar a pasta do cliente** dentro de `Clientes`.
5. **Garantir as 7 pastas de topo** do template dentro da pasta do cliente,
   criando só as que faltarem, e as 3 subpastas de `01-Referencias`
   (`Instagram`, `Site`, `Video`) — criando `01-Referencias` primeiro se ela
   também faltar.
6. **Se houver site e/ou Instagram** (fornecido pelo usuário ou já achado em
   `identidade-e-tom.md` de uma execução anterior) **e `identidade-e-tom.md`
   ainda não existir** em `00-Identidade-e-Tom`: analisa as fontes
   disponíveis — site (conteúdo + cores/fontes reais via CSS, não estimativa)
   e/ou bio do Instagram — e gera o documento no formato fixo acima. Se
   `identidade-e-tom.md` já existir, **não sobrescreve automaticamente**; só
   regenera se o usuário pedir explicitamente (ex: "atualize a identidade do
   cliente X"). Se não houver nenhum link (nem fornecido, nem em execução
   anterior), pula este passo sem bloquear o resto — a estrutura de pastas se
   completa normalmente e o documento fica pendente para quando houver uma
   fonte.
7. **Reportar**: link da pasta do cliente no Drive, quais pastas foram
   criadas agora vs. já existiam antes, e se `identidade-e-tom.md` foi
   gerado, já existia, ou ficou pendente por falta de site/Instagram.

A skill é idempotente: rodar de novo sobre um cliente já completo não duplica
nada, só confirma que a estrutura está presente (e não regenera
`identidade-e-tom.md` sem pedido explícito).

## O que reportar sempre

- Link da pasta do cliente no Drive.
- Lista do que foi criado nesta execução vs. já existia.
- Se `identidade-e-tom.md` foi gerado, já existia, ou ficou pendente (e por
  quê — falta de site/Instagram informado).
- Se encontrar uma pasta de nome parecido mas não idêntico (ex: variação de
  grafia), avisar antes de criar uma pasta nova — pode ser o mesmo cliente.

## Fora de escopo

- Copiar arquivos/templates para dentro das subpastas — só a estrutura de
  pastas é replicada, não conteúdo (todas as subpastas do modelo estão vazias,
  exceto `identidade-e-tom.md` quando gerado).
- Renomear, mover ou deletar pastas de clientes existentes — inclusive a pasta
  antiga `01-Referencias-Instagram`, que deve ser removida manualmente pelo
  usuário quando encontrada.
- Sobrescrever `identidade-e-tom.md` existente sem pedido explícito do
  usuário.
- Baixar/subir a logo do cliente automaticamente — se o usuário mandar a
  imagem no chat, a skill pode subi-la para `00-Identidade-e-Tom`, mas não
  busca a logo sozinha (ex: raspando o site).
- Ler o conteúdo visual de posts de Instagram de terceiros usados como
  referência (ex: inspiração de paleta/fonte enviada pelo usuário) — bloqueado
  por login do Instagram; pedir print/imagem direto no chat quando precisar
  desse tipo de referência.
- As demais skills da agência (postar no Instagram) — spec própria, ainda não
  criada.
