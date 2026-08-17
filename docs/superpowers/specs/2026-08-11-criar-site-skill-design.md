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

**Revisão de arquitetura (terceira rodada):** mais um MCP de componentes
(`Originkit`) foi conectado, e o usuário pediu suporte a sites com animação
3D, vídeo scroll-driven e mouse-following. Ambos entram como extensões
condicionais — só ativam quando a direção aprovada na Etapa 2 pedir esse
tratamento, não em todo site:

- **Componentes viram hierarquia de 3 níveis**: `Originkit` primeiro (seções
  de marketing prontas — hero, navbar, pricing, cards, forms — já adaptadas
  para Next.js/Tailwind/TS, com código Framer Motion nativo); `Shadcn_UI`
  para primitivas que o Originkit não cobre (botões, dialogs, formulários
  avulsos, tabelas); `21st.dev` como fallback final (catálogo mais amplo +
  geração via IA) quando nenhum dos dois anteriores serve.
- **3D condicional**: quando a direção aprovada pedir elementos 3D, usa
  React Three Fiber + `@react-three/drei` + `@react-three/postprocessing`
  para renderização declarativa dentro do Next.js, `Lenis` para smooth
  scroll (necessário para o scroll nativo não "quebrar" com cenas 3D
  pesadas), e GSAP ScrollTrigger (já no fluxo) para sincronizar câmera/
  objetos 3D com o scroll. É procedural/gerado em código — não depende de
  modelos 3D customizados nem do MCP do Blender (avaliado e descartado: não
  é necessário para o padrão de sites da aidealab). `ui-ux-pro-max` tem
  `--stack threejs` no banco dele, usado como referência pontual do mesmo
  jeito que as outras stacks.
- **Vídeo condicional**: vídeo scroll-scrubbed (currentTime do `<video>`
  controlado pelo GSAP ScrollTrigger — técnica nativa do próprio GSAP, sem
  lib extra); vídeo como textura dentro de cena 3D via `useVideoTexture` do
  `@react-three/drei`; vídeo de fundo/hero comum via `<video>` nativo do
  Next.js seguindo as guidelines de performance que o `ui-ux-pro-max` já
  cobre (lazy load, evitar CLS). Hospedagem/CDN de vídeo (ex: Mux,
  Cloudinary) fica fora de escopo por padrão — mesma lógica do resto do
  projeto (hospedagem é decisão do usuário depois).
- **Mouse-following**: na camada 2D/DOM, via Framer Motion (já no fluxo).
  Dentro de uma cena 3D, via eventos de ponteiro nativos do R3F/Three.js —
  não precisa de ferramenta adicional.

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

Lê (não só lista) o conteúdo da pasta do cliente no Drive — busca os
arquivos com `search_files` e depois efetivamente lê o conteúdo deles
(`read_file_content` para texto; `download_file_content` seguido de leitura
visual para imagens de referência, que são o grosso do material em
`01-Referencias`):
- `00-Identidade-e-Tom` — identidade de marca e tom de voz.
- `01-Referencias/Site` — referências específicas de site.
- `01-Referencias/Instagram` — usada como apoio só se `Site` estiver vazia
  (consistência visual com o que já existe da marca).

Se o material encontrado for insuficiente para definir uma direção de design
(pastas vazias ou quase vazias), a skill **pergunta diretamente ao usuário**
pelo contexto de marca/negócio em vez de travar ou inventar.

### Etapa 2 — Direção de design

1. Normaliza o nome do cliente (minúsculas, espaços viram hífen — ex: "Hora
   da Chipa" → `hora-da-chipa`) e cria, desde já, um repositório git **vazio**
   em `D:\claude\sites\<cliente-normalizado>\` (`git init` local; nenhum
   arquivo de código ainda — só a pasta e o git). Isso existe para que
   `impeccable` já rode com o diretório de trabalho (`cwd`) correto desde o
   início, já que ele exige isso no próprio setup dele e persiste
   `PRODUCT.md`/`DESIGN.md` relativo a esse `cwd`. Criar uma pasta vazia não
   viola a garantia de "nenhum código antes dos dois checkpoints" — essa
   garantia é sobre o **site em si** (código de página, componentes),
   coberta abaixo.
2. Invoca `impeccable` (fluxo de novo trabalho — todo site desta skill é o
   primeiro do cliente, não há caso de re-uso de `impeccable` num projeto
   existente) com `cwd` no repositório criado no passo 1, e o material
   coletado na Etapa 1 como contexto. `impeccable` decide o modo (`Persuade`
   — site de cliente é página de marketing/vendas) e produz a direção de
   design anti-slop, persistindo `PRODUCT.md`/`DESIGN.md` no repositório.
3. Quando `impeccable` precisar de um dado concreto rápido (ex: opções de
   paleta ou par tipográfico para a vibe identificada), consulta
   `ui-ux-pro-max` como referência pontual — não é o dono da persistência.
4. Apresenta ao usuário: modo escolhido, paleta/tipografia, direção visual
   geral.

**Checkpoint 1**: aguarda aprovação explícita do usuário antes de seguir. Se
o usuário pedir ajustes, refina e apresenta de novo. Nenhum arquivo de
código do site é escrito antes desta aprovação — só a pasta/git vazios do
passo 1 e os arquivos de contexto do `impeccable` (`PRODUCT.md`/`DESIGN.md`,
que são o próprio produto desta etapa, não código do site).

### Etapa 3 — Plano de conteúdo e páginas

Propõe a estrutura de páginas/seções e, usando a skill `marketing:content-
creation`, um esboço de copy de conversão (headlines, CTAs, textos-chave)
com base na direção aprovada e no negócio do cliente — não texto placeholder
genérico. Apresenta ao usuário.

**Checkpoint 2**: aguarda aprovação explícita do usuário antes de construir.
Nenhum arquivo de código do site (componentes, páginas) é escrito antes
desta aprovação.

### Etapa 4 — Construção

1. No repositório já criado na Etapa 2 (passo 1), escolhe e roda o comando
   de scaffolding do Next.js apropriado antes de `impeccable` gerar
   qualquer página — ex: `create-next-app` apontando para o diretório já
   existente. Se `D:\claude\sites\<cliente-normalizado>\` já tiver um site
   de uma execução anterior (re-execução da skill para o mesmo cliente),
   avisa o usuário e pergunta se quer sobrescrever, ou trata como
   atualização incremental — não decide isso sozinha. Sem push para GitHub
   — fica fora de escopo por enquanto. Stack fixa: React + Next.js
   (Vercel-ready).
2. `impeccable` constrói o site seguindo a direção aprovada no Checkpoint 1 e
   o plano de conteúdo aprovado no Checkpoint 2, atualizando o contexto do
   projeto em `PRODUCT.md`/`DESIGN.md` já existentes desde a Etapa 2.
3. **Componentes** (hierarquia de 3 níveis): busca primeiro no `Originkit`
   (seções de marketing prontas — hero, navbar, pricing, cards, forms — já
   adaptadas para Next.js/Tailwind/TS, com Framer Motion nativo). Para
   primitivas que o Originkit não cobre (botões, dialogs, formulários
   avulsos, tabelas), usa `Shadcn_UI` (registry oficial). Só recorre ao
   `21st.dev` (catálogo mais amplo + geração via IA) quando nenhum dos dois
   anteriores serve.
4. **Animação e mouse-following**: Framer Motion como padrão (via
   `gsap-framer-scroll-animation`) para transições e microinterações de
   componente, incluindo mouse-following na camada 2D/DOM (cursor
   magnético, hover). GSAP + ScrollTrigger (via `gsap-skills:gsap-
   scrolltrigger` e `gsap-skills:gsap-react`) especificamente para animação
   de scroll complexa (pin, scroll horizontal, coreografia).
5. **3D e vídeo (condicional — só quando a direção aprovada pedir)**: React
   Three Fiber + `@react-three/drei` + `@react-three/postprocessing` para
   cenas 3D procedurais (sem modelos customizados nem MCP do Blender —
   avaliado e descartado), `Lenis` para smooth scroll compatível com GSAP
   ScrollTrigger. Mouse-following dentro de uma cena 3D usa eventos de
   ponteiro nativos do R3F/Three.js — não precisa de ferramenta adicional.
   Vídeo scroll-scrubbed via GSAP nativo (`currentTime` do `<video>`),
   vídeo-textura 3D via `useVideoTexture` do `drei`, vídeo de fundo comum
   via `<video>` do Next.js com boas práticas de performance — sem
   CDN/streaming de vídeo por padrão.
6. **QA final**: antes de ir para a Etapa 5, roda `impeccable audit` seguido
   de `impeccable polish` sobre o site construído — esse é o caminho padrão,
   sempre o mesmo, para garantir profundidade de QA consistente entre
   execuções. O subagente `impeccable-finish-reviewer` é usado só como
   escalonamento, quando `audit`/`polish` sinalizarem algo que exige uma
   segunda opinião mais profunda — não como alternativa intercambiável.
7. **Ponto de extensão**: é aqui (e na Etapa 2) que futuras skills de
   desenvolvimento de site (a serem adicionadas pelo usuário) entram — hoje,
   a construção segue o pipeline `impeccable` descrito acima.

### Etapa 5 — Preview

Sobe o servidor de dev local do Next.js. Antes de apresentar ao usuário,
testa o site rodando com a skill `agent-browser` (já conectada no
ambiente) — navega pelas páginas geradas, tira screenshots em pelo menos
dois viewports (desktop e mobile), confirma que não há erro no console, e
verifica que elementos interativos (animações, cena 3D quando presente)
carregam sem quebrar. Só depois mostra o resultado (screenshots e/ou o
servidor rodando) para o usuário revisar antes de finalizar. Se o teste
encontrar erro, corrige antes de apresentar — não entrega site quebrado
para revisão.

### Etapa 6 — Relatório final

Reporta: caminho do repositório local, direção de design escolhida
(paleta/tipografia/modo), resumo do que foi criado, e resultado do QA final
(`impeccable audit`/`polish`).

## Implementação

Nomes de skill abaixo são os nomes completos (`plugin:skill`) que a
ferramenta Skill do Claude Code realmente resolve — não os nomes curtos
usados em prosa nas seções acima.

Ferramentas usadas:
- MCP do Google Drive (`search_files` para localizar, `read_file_content`/
  `download_file_content` para efetivamente ler o conteúdo) — Etapa 1 e
  verificação de pré-requisito. Somente leitura — `criar-site` nunca
  cria/move/renomeia pasta de cliente no Drive; isso é responsabilidade
  exclusiva de `criar-cliente` (skill separada).
- Skill `impeccable:impeccable` (+ subagentes `impeccable:impeccable-
  finish-reviewer`, usado como escalonamento de QA, e `impeccable:
  impeccable-asset-producer` quando aplicável) — Etapa 2 e 4 (direção,
  construção, QA final).
- Skill `ui-ux-pro-max:ui-ux-pro-max` — consulta pontual de dados concretos
  (paletas, tipografia, guidelines por stack, incluindo `--stack threejs`
  quando aplicável) nas Etapas 2 e 4.
- Skill `marketing:content-creation` — copy de conversão (headlines, CTAs)
  na Etapa 3.
- Skill `ui-ux-pro-max:ui-styling` — referência de implementação shadcn/ui +
  Tailwind na Etapa 4 (parte do mesmo plugin do `ui-ux-pro-max`, não uma
  skill à parte).
- Comando de scaffolding do Next.js (ex: `create-next-app`) — Etapa 4,
  passo 1, para inicializar o projeto dentro do repositório já criado na
  Etapa 2.
- MCP `Originkit` — seções de marketing prontas (hero, navbar, pricing,
  cards, forms) — Etapa 4, primeira parada para componentes.
- MCP `Shadcn_UI` — registry oficial de componentes/blocos/temas shadcn —
  Etapa 4, para primitivas que o Originkit não cobre.
- MCP `21st.dev` — catálogo estendido de componentes + geração via IA —
  Etapa 4, fallback final quando nem Originkit nem Shadcn_UI cobrem.
- Skill `gsap-framer-scroll-animation` — Framer Motion (animação padrão de
  componente) — Etapa 4.
- Skills `gsap-skills:gsap-scrolltrigger` e `gsap-skills:gsap-react` — GSAP
  para animação de scroll complexa — Etapa 4.
- React Three Fiber, `@react-three/drei`, `@react-three/postprocessing`,
  `Lenis` — Etapa 4, só quando a direção aprovada pedir 3D/scroll cinemático
  (bibliotecas de código, não skills/MCPs do ambiente).
- `git` local — Etapa 2, passo 1 (`git init` do repositório vazio).
- Servidor de dev local do Next.js — Etapa 5.
- Skill `agent-browser` — Etapa 5, para testar o site rodando (navegação,
  screenshots desktop/mobile, checagem de erro de console) antes de
  apresentar ao usuário.

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
- Criar ou gerenciar pastas de cliente no Drive — isso é exclusivo da skill
  `criar-cliente`, separada; `criar-site` só lê a estrutura já existente.
- Modelos 3D customizados e o MCP do Blender — avaliado e descartado; 3D
  fica procedural/gerado em código (React Three Fiber).
- Hospedagem/CDN/streaming de vídeo (ex: Mux, Cloudinary) — vídeo fica
  self-hosted no repositório por padrão.
