# Skill: criar-site

## Contexto

A aidealab (agência de conteúdo Instagram) planeja quatro skills de automação:
`criar-cliente` (já implementada — garante a estrutura de pastas do cliente no
Google Drive), `criar carrossel`, `postar no Instagram`, e esta, `criar site`.
Todas as três últimas dependem de `criar-cliente` para localizar a pasta certa
do cliente.

`criar-site` é a mais ambiciosa das quatro: não mexe só em estrutura de
pastas, ela efetivamente gera um site (código) para o cliente, usando as
referências e a identidade de marca já organizadas no Drive pela
`criar-cliente`. O objetivo explícito é evitar "site genérico"/AI slop — para
isso, a skill se apoia em duas skills de design já instaladas no ambiente:

- **`taste-skill`** (`design-taste-frontend`) — skill de julgamento estético:
  lê o brief, declara uma "leitura de design" (tipo de página, vibe,
  público), define três dials (`DESIGN_VARIANCE`, `MOTION_INTENSITY`,
  `VISUAL_DENSITY`) e mapeia o brief para o design system/stack certo. É
  prosa/heurística — não tem banco de dados por trás, só o raciocínio do
  modelo em cima de um guia de ~1200 linhas.
- **`ui-ux-pro-max`** — skill orientada a dado: roda um script Python
  (`search.py`) sobre um banco local (~1.7MB de CSVs: 84 estilos, 192
  paletas, 74 pares tipográficos, guidelines de UX, regras por stack
  incluindo performance de React) para transformar uma leitura de design em
  paleta/tipografia/stack concretos, e **persiste** o resultado em
  `design-system/<projeto>/MASTER.md` (+ overrides por página) — o que
  garante consistência visual entre as páginas de um mesmo site.

A `frontend-design` (skill padrão do Claude Code) fica fora do fluxo — é
redundante frente às duas acima, que cobrem tanto o julgamento anti-slop
(`taste-skill`) quanto o dado concreto de implementação (`ui-ux-pro-max`).

O usuário sinalizou que vai continuar adicionando skills de criação de site ao
ambiente ao longo do tempo. Por isso este desenho evita virar um skill
monolítico: as etapas 2 (direção de design) e 4 (construção) são pontos de
extensão explícitos, documentados no `SKILL.md`, onde novas skills podem
entrar sem reescrever o fluxo inteiro.

## Objetivo

Uma skill (`criar-site`) que, dado um cliente já existente (estrutura criada
por `criar-cliente`), gera um site novo para ele: coleta as referências do
cliente no Drive, define uma direção de design não genérica, planeja a
estrutura de páginas/conteúdo, constrói o código do site num repositório git
próprio, e mostra o resultado rodando localmente antes de finalizar.

## Comportamento

Trigger: linguagem natural do tipo "criar site \<cliente\>" / "crie o site do
cliente \<cliente\>" / "novo site \<cliente\>".

### Pré-requisito

A skill busca a pasta do cliente dentro de `Clientes` (mesmo `parentId` usado
por `criar-cliente`: `1xHuFxkYD0INTpdZbzBZLRBy-X3tVM-rv`), case-insensitive.
Se não existir, a skill **para e avisa** o usuário para rodar `criar-cliente`
primeiro — não a invoca automaticamente (uma responsabilidade por skill,
mesma convenção do projeto).

### Etapa 1 — Coleta de referências

Lê, da pasta do cliente no Drive:
- `00-Identidade-e-Tom` — identidade de marca e tom de voz.
- `01-Referencias/Site` — referências específicas de site.
- `01-Referencias/Instagram` — usada como apoio só se `Site` estiver vazia
  (consistência visual com o que já existe da marca).

Se o material encontrado for insuficiente para definir uma direção de design
(pastas vazias ou quase vazias), a skill **pergunta diretamente ao usuário**
pelo contexto de marca/negócio em vez de travar ou inventar.

### Etapa 2 — Direção de design

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

### Etapa 3 — Plano de conteúdo e páginas

Propõe a estrutura de páginas/seções e um esboço de conteúdo (textos-chave,
CTAs) com base na direção aprovada e no negócio do cliente. Apresenta ao
usuário.

**Checkpoint 2**: aguarda aprovação explícita do usuário antes de construir.

### Etapa 4 — Construção

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
4. **Ponto de extensão**: é aqui que futuras skills de desenvolvimento de
   site (a serem adicionadas pelo usuário) entram — hoje, a construção é
   feita seguindo diretamente `MASTER.md` + guidelines de stack.

### Etapa 5 — Preview

Sobe um servidor local (dev server da stack escolhida) e mostra o site
rodando para o usuário revisar antes de finalizar.

### Etapa 6 — Relatório final

Reporta: caminho do repositório local, stack e design system escolhidos
(paleta/tipografia), resumo do que foi criado.

## Implementação

Ferramentas usadas:
- MCP do Google Drive (`search_files`) — Etapa 1 e verificação de
  pré-requisito.
- Skill `taste-skill` e skill `ui-ux-pro-max` (via `search.py`) — Etapa 2 e 4.
- Skill `ui-styling` — Etapa 4, quando a stack for Tailwind/shadcn.
- `git` local e ferramentas de scaffolding da stack escolhida (ex: Vite,
  Next.js CLI) — Etapa 4.
- Servidor de dev local da stack escolhida — Etapa 5.

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
