---
name: criar-site
description: Gera um site novo para um cliente da aidealab a partir das referências e identidade de marca já organizadas no Drive pela criar-cliente. Usa taste-skill para direção de design anti-slop e ui-ux-pro-max para paleta/tipografia/stack concretos e consistência entre páginas via design system persistido. Dispara com "criar site <cliente>" / "crie o site do cliente <cliente>" / "novo site <cliente>". Para em dois checkpoints de aprovação (direção de design, plano de conteúdo) antes de escrever qualquer código.
---

# Criar site

Gera um site novo (código, não só estrutura de pastas) para um cliente da
aidealab, a partir das referências e da identidade de marca já organizadas no
Drive pela `criar-cliente`. O objetivo é evitar site genérico/AI slop: a
direção de design não vem de inferência solta, ela passa por duas skills já
instaladas no ambiente — `taste-skill`, que faz o julgamento estético
anti-slop (leitura de design + dials), e `ui-ux-pro-max`, que ancora esse
julgamento num banco de dados real de paletas/tipografia/stacks e persiste o
resultado num design system, garantindo consistência visual entre as páginas
do site conforme ele cresce.

A skill `frontend-design` padrão do Claude Code fica fora do fluxo — é
redundante frente a `taste-skill` + `ui-ux-pro-max`, que já cobrem tanto o
julgamento anti-slop quanto o dado concreto de implementação.

## Quando usar

Pedido do tipo "criar site \<cliente\>" / "crie o site do cliente \<cliente\>"
/ "novo site \<cliente\>".

### Pré-requisito

A skill busca a pasta do cliente dentro de `Clientes` (mesmo `parentId`
usado por `criar-cliente`: `1xHuFxkYD0INTpdZbzBZLRBy-X3tVM-rv`),
case-insensitive. Se a pasta não existir, a skill **para e avisa** o usuário
para rodar `criar-cliente` primeiro — **não** a invoca automaticamente. Uma
responsabilidade por skill é a convenção do projeto (ver
`agente aidealab/skills/README.md`); `criar-site` só consome a estrutura que
`criar-cliente` garante, nunca a cria por conta própria.

## Etapa 1 — Coleta de referências

Lê, da pasta do cliente no Drive:
- `00-Identidade-e-Tom` — identidade de marca e tom de voz.
- `01-Referencias/Site` — referências específicas de site.
- `01-Referencias/Instagram` — usada como apoio só se `Site` estiver vazia
  (consistência visual com o que já existe da marca).

Se o material encontrado for insuficiente para definir uma direção de design
(pastas vazias ou quase vazias), a skill **pergunta diretamente ao usuário**
pelo contexto de marca/negócio em vez de travar ou inventar.

## Etapa 2 — Direção de design

1. Invoca `taste-skill` com o material coletado na Etapa 1 como brief. A
   skill produz a "leitura de design" (tipo de página, vibe, público) e os
   três dials (`DESIGN_VARIANCE`, `MOTION_INTENSITY`, `VISUAL_DENSITY`).
2. Invoca `ui-ux-pro-max` (`search.py ... --design-system`), passando os
   dials da `taste-skill` via `--variance`/`--motion`/`--density`, para obter
   paleta, tipografia, stack recomendado e padrões de layout concretos —
   ancorados no banco de dados, não só na inferência do passo anterior.
3. Apresenta ao usuário: leitura de design, paleta/tipografia escolhidas,
   stack recomendado.

**Checkpoint 1**: aguarda aprovação explícita do usuário antes de seguir. Se
o usuário pedir ajustes, refina e apresenta de novo.

## Etapa 3 — Plano de conteúdo e páginas

Propõe a estrutura de páginas/seções e um esboço de conteúdo (textos-chave,
CTAs) com base na direção aprovada e no negócio do cliente. Apresenta ao
usuário.

**Checkpoint 2**: aguarda aprovação explícita do usuário antes de construir.

## Etapa 4 — Construção

1. Normaliza o nome do cliente (minúsculas, espaços viram hífen — ex: "Hora
   da Chipa" → `hora-da-chipa`) e cria um repositório git novo em
   `D:\claude\sites\<cliente-normalizado>\` (`git init` local; sem push para
   GitHub — fica fora de escopo por enquanto).
2. Roda `ui-ux-pro-max` de novo com `--design-system --persist --output-dir`
   apontando para a raiz do novo repositório, para gravar
   `design-system/<projeto>/MASTER.md` com a direção aprovada no Checkpoint
   1 — isso garante consistência entre páginas conforme o site cresce.
3. Implementa o site seguindo o `MASTER.md` e o plano de conteúdo aprovado,
   usando a stack escolhida na Etapa 2. Quando a stack for Tailwind-based,
   usa a `ui-styling` (shadcn/ui + Tailwind) como referência de
   implementação; para outras stacks, usa as buscas `--stack <nome>` da
   `ui-ux-pro-max` como guia.

**Ponto de extensão**: é aqui — e na Etapa 2 — que futuras skills de
desenvolvimento de site (a serem adicionadas pelo usuário ao ambiente) podem
entrar sem reescrever o fluxo inteiro. Hoje, sem essas skills adicionais, a
construção é feita seguindo diretamente `MASTER.md` + guidelines de stack da
`ui-ux-pro-max`/`ui-styling`.

## Etapa 5 — Preview

Sobe um servidor local (dev server da stack escolhida) e mostra o site
rodando para o usuário revisar antes de finalizar.

## Etapa 6 — Relatório final

Reporta: caminho do repositório local, stack e design system escolhidos
(paleta/tipografia), resumo do que foi criado.

## Ferramentas necessárias

- MCP do Google Drive (`search_files`) — verificação do pré-requisito e
  Etapa 1.
- Skill `taste-skill` e skill `ui-ux-pro-max` (invocadas via a ferramenta
  Skill, não chamando os scripts internos delas diretamente) — Etapa 2 e
  Etapa 4.
- Skill `ui-styling` — Etapa 4, quando a stack escolhida for Tailwind/shadcn.
- `git` local e ferramentas de scaffolding da stack escolhida (ex: Vite,
  Next.js CLI) — Etapa 4.
- Servidor de dev local da stack escolhida — Etapa 5.

## O que reportar sempre

- Caminho do repositório local (`D:\claude\sites\<cliente-normalizado>\`).
- Resumo do design system: paleta, tipografia, stack escolhidos.
- O que foi criado nesta execução (páginas, seções, principais decisões).

## Fora de escopo

- Deploy, hospedagem, e compra de domínio.
- Push para repositório remoto/GitHub — fica só local por enquanto.
- Gerar copy final sem aprovação do usuário — a skill propõe nos Checkpoints
  1 e 2, usuário aprova antes de construir.
- Rodar `criar-cliente` automaticamente quando a pasta do cliente não existe
  — a skill apenas avisa e para.
- Usar a skill `frontend-design` padrão do Claude Code — redundante frente a
  `taste-skill` + `ui-ux-pro-max` neste fluxo.
- Definir de antemão uma stack fixa para todo site — a Etapa 2 decide caso a
  caso, ancorada no `ui-ux-pro-max`.
