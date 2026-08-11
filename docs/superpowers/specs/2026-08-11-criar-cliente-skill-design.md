# Skill: criar-cliente

## Contexto

A aidealab (agência de conteúdo Instagram) organiza clientes no Google Drive dentro
da pasta `Clientes` (ID `1xHuFxkYD0INTpdZbzBZLRBy-X3tVM-rv`), uma subpasta por
cliente. Existe um padrão de estrutura de subpastas — atualmente presente por
completo apenas no cliente "hora da chipa" — que organiza o material de trabalho
do cliente (identidade, referências, materiais brutos, roteiros, carrosséis,
campanhas, aprovados para postar). Outros clientes (ex: "cantinho mineiro") foram
criados sem seguir essa estrutura, o que dificulta o uso consistente por outras
automações.

Esta é a primeira de quatro skills planejadas para a agência (criar cliente, criar
carrossel, postar no Instagram, criar site). As outras três serão desenhadas
separadamente, cada uma com sua própria spec. Esta skill é a base: as demais vão
localizar a pasta do cliente certo a partir da estrutura que ela garante.

## Objetivo

Uma skill (`criar-cliente`) que, dado um nome de cliente, garante que a pasta
desse cliente existe dentro de `Clientes` e contém as subpastas padrão —
criando o que estiver faltando, sem duplicar o que já existe.

## Estrutura padrão (template)

Aplicada em "hora da chipa" em 2026-08-11 (referência viva do template):

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

`01-Referencias` separa as referências por objetivo (posts de Instagram, site,
vídeo) em vez de ser só referências de Instagram como era antes
(`01-Referencias-Instagram`, hoje uma pasta antiga/vazia que deve ser removida
manualmente no Drive — a skill não precisa recriá-la nem migrá-la).

As outras 6 pastas de topo continuam planas, sem subníveis. A lista completa
(incluindo as 3 subpastas de `01-Referencias`) fica hardcoded no `SKILL.md`
— não é lida dinamicamente da pasta modelo a cada execução.

## Comportamento

Trigger: linguagem natural do tipo "crie cliente <nome>" / "novo cliente <nome>".

Passos:
1. Recebe o nome do cliente do pedido do usuário.
2. Normaliza o nome para minúsculas (padrão observado nas pastas existentes:
   "hora da chipa", "cantinho mineiro", "sieger"). Evita duplicar cliente por
   diferença de maiúscula/minúscula em usos futuros.
3. Busca dentro de `Clientes` (parentId fixo) por uma pasta cujo título bata
   (case-insensitive) com o nome normalizado.
4. Se não existir, cria a pasta do cliente dentro de `Clientes`.
5. Garante as 7 pastas de topo do template dentro da pasta do cliente,
   criando apenas as que faltarem.
6. Dentro de `01-Referencias` (criando-a primeiro se faltar), garante as 3
   subpastas (`Instagram`, `Site`, `Video`), criando apenas as que faltarem.
7. A skill é idempotente: serve tanto para criar cliente novo quanto para
   completar a estrutura de um cliente já existente (ex: "cantinho mineiro",
   que hoje só tem uma pasta de logo solta).
8. Reporta o link da pasta do cliente no Drive e quais pastas foram criadas
   (se algo já existia, apenas confirma que está presente).

## Implementação

A skill é só instrução (`SKILL.md`), sem código externo — usa diretamente as
ferramentas MCP do Google Drive já conectadas à conta:
- `search_files` (query por `parentId` e `title`) para checar existência
- `create_file` com `mimeType: application/vnd.google-apps.folder` para criar
  pastas (cliente, pastas de topo, subpastas de `01-Referencias`)

Não há ferramenta de renomear/mover/deletar disponível no Drive MCP conectado —
qualquer correção desse tipo (como remover a pasta antiga
`01-Referencias-Instagram`) fica a cargo do usuário, manualmente.

## Fora de escopo

- Copiar arquivos/templates para dentro das subpastas (hoje todas estão vazias
  na pasta modelo — só a estrutura de pastas é replicada, não conteúdo).
- Renomear, mover ou deletar pastas de clientes existentes.
- As outras 3 skills da agência (carrossel, postagem, site) — specs separadas.
