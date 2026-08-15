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
`criar-cliente`. O objetivo explícito é evitar "site genérico"/AI slop.

**Revisão de arquitetura (segunda rodada, após instalação de mais skills):**
o desenho original usava `taste-skill` (julgamento) + `ui-ux-pro-max` (dado)
para a direção de design. Depois da instalação de `impeccable` — um pipeline
completo de design/build/QA — e da confirmação de que a stack do cliente é
sempre React + Next.js (Vercel-ready), o desenho foi revisado:

- **`impeccable`** vira a espinha dorsal das Etapas 2 e 4. É mais completo
  que `taste-skill` sozinho: além de ler o brief e definir uma direção anti-
  slop, tem comandos de planejamento (`shape`), crítica (`critique`),
  auditoria de acessibilidade/performance/responsivo (`audit`), polimento
  final (`polish`), animação (`animate`), persiste contexto do projeto
  (`PRODUCT.md`/`DESIGN.md`), e tem um subagente dedicado
  (`impeccable-finish-reviewer`) para QA do resultado final. Cobre o que
  `taste-skill` cobria e mais.
- **`taste-skill` sai do fluxo** — redundante frente ao `impeccable`, que faz
  o mesmo julgamento anti-slop com um pipeline mais completo por trás.
- **`ui-ux-pro-max` muda de papel**: deixa de ser o dono da persistência do
  design system (isso agora é `DESIGN.md`/`PRODUCT.md` do `impeccable`) e
  passa a ser consultado pontualmente pelo `impeccable` quando este precisa
  de um dado concreto rápido (ex: opções de paleta ou par tipográfico para
  uma vibe específica) — o banco de dados dele (192 paletas, 74 pares
  tipográficos, guidelines por stack) continua útil como referência, só não
  é mais a fonte de verdade da consistência entre páginas.
- **Componentes**: dois MCPs de componentes React/shadcn foram conectados —
  `Shadcn_UI` (registry oficial: componentes, blocos pré-montados, temas) e
  `21st.dev` (catálogo comunitário mais amplo + geração de componente via IA
  quando nada no registry oficial serve). `Shadcn_UI` é a primeira parada
  (componentes/blocos oficiais, testados, acessíveis); `21st.dev` é o
  complemento quando se precisa de algo mais específico ou de geração.
- **Animação**: como a stack é sempre React/Next, duas famílias de skills
  cobrem terrenos diferentes, não redundantes — `gsap-framer-scroll-
  animation` é a única que cobre Framer Motion (padrão para transições e
  microinterações de componente, mais idiomático em React), e
  `gsap-skills` (em especial `gsap-skills:gsap-scrolltrigger` e
  `gsap-skills:gsap-react`) cobre GSAP com mais profundidade que a skill
  anterior, reservado para animação de scroll complexa (pin, scroll
  horizontal, coreografia) onde GSAP é claramente mais forte que Framer
  Motion.
- **`frontend-design`** (skill padrão do Claude Code) continua fora do
  fluxo — redundante frente ao `impeccable`.

O usuário sinalizou que vai continuar adicionando skills de criação de site ao
ambiente ao longo do tempo. Por isso este desenho evita virar um skill
monolítico: as etapas 2 (direção de design) e 4 (construção) são pontos de
extensão explícitos, documentados no `SKILL.md`, onde novas skills podem
entrar sem reescrever o fluxo inteiro.

## Objetivo

Uma skill (`criar-site`) que, dado um cliente já existente (estrutura criada
por `criar-cliente`), gera um site novo para ele: coleta as referências do
cliente no Drive, define uma direção de design não genérica, planeja a
estrutura de páginas/conteúdo, constrói o código do site (React + Next.js)
num repositório git próprio, e mostra o resultado rodando localmente antes de
finalizar.

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

1. Invoca `impeccable` (comando `shape`, ou o fluxo de novo trabalho quando
   for o primeiro site do cliente) com o material coletado na Etapa 1 como
   contexto. `impeccable` decide o modo (`Persuade` — site de cliente é
   página de marketing/vendas) e produz a direção de design anti-slop.
2. Quando `impeccable` precisar de um dado concreto rápido (ex: opções de
   paleta ou par tipográfico para a vibe identificada), consulta
   `ui-ux-pro-max` como referência pontual — não é o dono da persistência.
3. Apresenta ao usuário: modo escolhido, paleta/tipografia, direção visual
   geral.

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
   GitHub — fica fora de escopo por enquanto). Stack fixa: React + Next.js
   (Vercel-ready).
2. `impeccable` constrói o site seguindo a direção aprovada no Checkpoint 1 e
   o plano de conteúdo aprovado no Checkpoint 2, persistindo o contexto do
   projeto em `PRODUCT.md`/`DESIGN.md`.
3. **Componentes**: busca primeiro no `Shadcn_UI` (registry oficial —
   componentes, blocos, temas) para primitivas e composições padrão. Quando
   precisar de algo mais específico que o registry oficial não cobre, busca
   ou gera no `21st.dev` (catálogo mais amplo + geração via IA).
4. **Animação**: Framer Motion como padrão (via `gsap-framer-scroll-
   animation`) para transições e microinterações de componente. GSAP +
   ScrollTrigger (via `gsap-skills:gsap-scrolltrigger` e
   `gsap-skills:gsap-react`) especificamente para animação de scroll
   complexa (pin, scroll horizontal, coreografia).
5. **QA final**: antes de ir para a Etapa 5, roda `impeccable audit` +
   `impeccable polish` (ou o subagente `impeccable-finish-reviewer`) sobre o
   site construído.
6. **Ponto de extensão**: é aqui (e na Etapa 2) que futuras skills de
   desenvolvimento de site (a serem adicionadas pelo usuário) entram — hoje,
   a construção segue o pipeline `impeccable` descrito acima.

### Etapa 5 — Preview

Sobe o servidor de dev local do Next.js e mostra o site rodando para o
usuário revisar antes de finalizar.

### Etapa 6 — Relatório final

Reporta: caminho do repositório local, direção de design escolhida
(paleta/tipografia/modo), resumo do que foi criado, e resultado do QA final
(`impeccable audit`/`polish`).

## Implementação

Ferramentas usadas:
- MCP do Google Drive (`search_files`) — Etapa 1 e verificação de
  pré-requisito.
- Skill `impeccable` (+ subagentes `impeccable-finish-reviewer` e
  `impeccable-asset-producer` quando aplicável) — Etapa 2 e 4 (direção,
  construção, QA final).
- Skill `ui-ux-pro-max` — consulta pontual de dados concretos (paletas,
  tipografia, guidelines por stack) nas Etapas 2 e 4.
- Skill `ui-styling` — referência de implementação shadcn/ui + Tailwind na
  Etapa 4.
- MCP `Shadcn_UI` — registry oficial de componentes/blocos/temas shadcn —
  Etapa 4.
- MCP `21st.dev` — catálogo estendido de componentes + geração via IA —
  Etapa 4, quando o registry oficial não cobre o necessário.
- Skill `gsap-framer-scroll-animation` — Framer Motion (animação padrão de
  componente) — Etapa 4.
- Skills `gsap-skills:gsap-scrolltrigger` e `gsap-skills:gsap-react` — GSAP
  para animação de scroll complexa — Etapa 4.
- `git` local — Etapa 4.
- Servidor de dev local do Next.js — Etapa 5.

## Fora de escopo

- Deploy, hospedagem, e compra de domínio (mesmo a stack sendo Vercel-ready,
  o deploy em si fica fora — o usuário decide quando publicar).
- Push para repositório remoto/GitHub — fica só local por enquanto.
- Gerar copy final sem aprovação do usuário — a skill propõe nos Checkpoints
  1 e 2, usuário aprova antes de construir.
- Rodar `criar-cliente` automaticamente quando a pasta do cliente não existe
  — a skill apenas avisa e para.
- Usar `taste-skill` isolada ou a skill `frontend-design` padrão do Claude
  Code — ambas redundantes frente ao `impeccable` neste fluxo.
- Decidir a stack caso a caso — fixa em React + Next.js (Vercel-ready) para
  todo site, conforme confirmado pelo usuário.
