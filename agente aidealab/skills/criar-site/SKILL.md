---
name: criar-site
description: Gera um site novo (React + Next.js) para um cliente da aidealab a partir das referências e identidade de marca já organizadas no Drive pela criar-cliente. Usa impeccable como espinha dorsal de direção de design anti-slop, construção e QA final, consultando ui-ux-pro-max para dados concretos, os MCPs Originkit/Shadcn_UI/21st.dev para componentes, e opcionalmente React Three Fiber/GSAP/Lenis para 3D e vídeo scroll-driven quando a direção pedir. Dispara com "criar site <cliente>" / "crie o site do cliente <cliente>" / "novo site <cliente>". Para em dois checkpoints de aprovação (direção de design, plano de conteúdo) antes de escrever qualquer código.
---

# Criar site

Gera um site novo (código, React + Next.js) para um cliente da aidealab, a
partir das referências e da identidade de marca já organizadas no Drive pela
`criar-cliente`. O objetivo é evitar site genérico/AI slop: a direção de
design e a construção passam por `impeccable`, um pipeline completo de
design/build/QA (planejamento com `shape`, crítica, auditoria de
acessibilidade/performance/responsivo, polimento final, animação, e um
subagente dedicado de revisão — `impeccable-finish-reviewer`) que consulta a
skill `ui-ux-pro-max` pontualmente quando precisa de um dado concreto (ex:
opções de paleta ou par tipográfico para uma vibe específica).

A skill `taste-skill` saiu do fluxo — redundante frente ao `impeccable`, que
cobre o mesmo julgamento anti-slop com um pipeline mais completo por trás. A
skill `frontend-design` padrão do Claude Code também fica fora, pelo mesmo
motivo.

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

Lê (não só lista) o conteúdo da pasta do cliente no Drive: usa `search_files`
para localizar os arquivos e depois efetivamente lê o conteúdo deles —
`read_file_content` para texto, `download_file_content` seguido de leitura
visual para imagens de referência (que são o grosso do material em
`01-Referencias`):
- `00-Identidade-e-Tom` — identidade de marca e tom de voz.
- `01-Referencias/Site` — referências específicas de site.
- `01-Referencias/Instagram` — usada como apoio só se `Site` estiver vazia
  (consistência visual com o que já existe da marca).

Se o material encontrado for insuficiente para definir uma direção de design
(pastas vazias ou quase vazias), a skill **pergunta diretamente ao usuário**
pelo contexto de marca/negócio em vez de travar ou inventar.

## Etapa 2 — Direção de design

1. Normaliza o nome do cliente (minúsculas, espaços viram hífen — ex: "Hora
   da Chipa" → `hora-da-chipa`) e cria, desde já, um repositório git
   **vazio** em `D:\claude\sites\<cliente-normalizado>\` (`git init` local;
   nenhum arquivo de código ainda — só a pasta e o git). Isso é feito aqui,
   e não na Etapa 4, especificamente para que a skill `impeccable:impeccable`
   já rode com o diretório de trabalho (`cwd`) correto desde o início — ela
   exige isso no próprio setup e persiste `PRODUCT.md`/`DESIGN.md` relativo
   a esse `cwd`.
2. Invoca a skill `impeccable:impeccable` (via a ferramenta Skill — fluxo de
   novo trabalho; todo site gerado por esta skill é o primeiro do cliente,
   não há caso de reuso do `impeccable:impeccable` num projeto existente)
   com `cwd` no repositório criado no passo 1, e o material coletado na
   Etapa 1 como contexto. `impeccable:impeccable` decide o modo (`Persuade` — site de
   cliente é página de marketing/vendas) e produz a direção de design
   anti-slop, persistindo `PRODUCT.md`/`DESIGN.md` nesse repositório.
3. Quando `impeccable:impeccable` precisar de um dado concreto rápido (ex:
   opções de paleta ou par tipográfico para a vibe identificada), consulta a
   skill `ui-ux-pro-max:ui-ux-pro-max` (via a ferramenta Skill) como
   referência pontual — ela não é a dona da persistência do design system,
   só um banco de dados de apoio.
4. Apresenta ao usuário: modo escolhido, paleta/tipografia, direção visual
   geral.

**Checkpoint 1**: aguarda aprovação explícita do usuário antes de seguir. Se
o usuário pedir ajustes, refina e apresenta de novo. Nenhum arquivo de
código do site é escrito antes desta aprovação — só a pasta/git vazios do
passo 1 e os arquivos de contexto do `impeccable:impeccable`
(`PRODUCT.md`/`DESIGN.md`, que são o próprio produto desta etapa, não código
do site).

## Etapa 3 — Plano de conteúdo e páginas

Propõe a estrutura de páginas/seções e, usando a skill `marketing:content-
creation` (via a ferramenta Skill), um esboço de copy de conversão
(headlines, CTAs, textos-chave) com base na direção aprovada e no negócio do
cliente — não texto placeholder genérico. Apresenta ao usuário.

**Checkpoint 2**: aguarda aprovação explícita do usuário antes de construir.
Nenhum arquivo de código do site (componentes, páginas) é escrito antes
desta aprovação.

## Etapa 4 — Construção

1. No repositório já criado na Etapa 2 (passo 1), roda o comando de
   scaffolding do Next.js apropriado (ex: `create-next-app`, apontando para
   o diretório já existente) antes de `impeccable:impeccable` gerar qualquer
   página. Se `D:\claude\sites\<cliente-normalizado>\` já tiver um site de
   uma execução anterior (re-execução da skill para o mesmo cliente), avisa
   o usuário e pergunta se quer sobrescrever ou tratar como atualização
   incremental — não decide isso sozinha. Sem push para GitHub — fica fora
   de escopo por enquanto. Stack fixa para todo site: React + Next.js
   (Vercel-ready) — não é mais decidida caso a caso.
2. A skill `impeccable:impeccable` (via a ferramenta Skill) constrói o site
   seguindo a direção aprovada no Checkpoint 1 e o plano de conteúdo
   aprovado no Checkpoint 2, atualizando o contexto do projeto em
   `PRODUCT.md`/`DESIGN.md` já criados na Etapa 2.
3. **Componentes** (hierarquia de 3 níveis): busca primeiro no MCP
   `Originkit` (seções de marketing prontas — hero, navbar, pricing, cards,
   forms — já adaptadas para Next.js/Tailwind/TS, com Framer Motion nativo).
   Para primitivas que o Originkit não cobre (botões, dialogs, formulários
   avulsos, tabelas), usa o MCP `Shadcn_UI` (registry oficial). Só recorre
   ao MCP `21st.dev` (catálogo mais amplo + geração via IA) como fallback
   final, quando nenhum dos dois anteriores serve.
4. **Animação e mouse-following**: usa a skill `gsap-framer-scroll-
   animation` (Framer Motion, via a ferramenta Skill) como padrão para
   transições e microinterações de componente — mais idiomático em React —
   incluindo mouse-following na camada 2D/DOM (cursor magnético, hover; não
   precisa de ferramenta adicional além da própria skill). Usa as skills
   `gsap-skills:gsap-scrolltrigger` e `gsap-skills:gsap-react` (GSAP, via a
   ferramenta Skill) especificamente para animação de scroll complexa (pin,
   scroll horizontal, coreografia), onde GSAP é claramente mais forte que
   Framer Motion — as duas famílias cobrem terrenos diferentes, não são
   redundantes entre si.
5. **3D e vídeo (condicional — só quando a direção aprovada pedir)**: quando
   — e só quando — a direção aprovada no Checkpoint 1 pedir tratamento 3D ou
   vídeo scroll-driven, usa React Three Fiber + `@react-three/drei` +
   `@react-three/postprocessing` como bibliotecas de código para cenas 3D
   procedurais dentro do Next.js (sem modelos 3D customizados, sem MCP do
   Blender — avaliado e descartado), e `Lenis` como biblioteca de código
   para smooth scroll compatível com GSAP ScrollTrigger. Mouse-following
   dentro de uma cena 3D usa eventos de ponteiro nativos do R3F/Three.js —
   também não precisa de ferramenta adicional. Para vídeo: vídeo
   scroll-scrubbed via técnica nativa do GSAP (`currentTime` do `<video>`
   controlado pelo ScrollTrigger, sem lib extra); vídeo-textura dentro de
   cena 3D via `useVideoTexture` do `drei`; vídeo de fundo/hero comum via
   `<video>` nativo do Next.js seguindo boas práticas de performance — sem
   CDN/streaming de vídeo por padrão. Em nenhum outro site esse bloco entra
   em jogo.
6. **QA final**: antes de ir para a Etapa 5, roda `impeccable:impeccable`
   `audit` seguido de `impeccable:impeccable` `polish` sobre o site
   construído — esse é o caminho padrão, sempre o mesmo, para garantir
   profundidade de QA consistente entre execuções. O subagente
   `impeccable:impeccable-finish-reviewer` (via a ferramenta Agent) é usado
   só como escalonamento, quando `audit`/`polish` sinalizarem algo que exige
   uma segunda opinião mais profunda — nunca como alternativa
   intercambiável.

**Ponto de extensão**: é aqui — e na Etapa 2 — que futuras skills de
desenvolvimento de site (a serem adicionadas pelo usuário ao ambiente) podem
entrar sem reescrever o fluxo inteiro. Hoje, sem essas skills adicionais, a
construção segue o pipeline `impeccable:impeccable` descrito acima.

## Etapa 5 — Preview

Sobe o servidor de dev local do Next.js e mostra o site rodando para o
usuário revisar antes de finalizar.

## Etapa 6 — Relatório final

Reporta: caminho do repositório local, direção de design escolhida
(paleta/tipografia/modo), resumo do que foi criado, e resultado do QA final
(`impeccable audit`/`polish`).

## Ferramentas necessárias

Nomes de skill abaixo são os nomes completos (`plugin:skill`) que a
ferramenta Skill do Claude Code realmente resolve — não os nomes curtos
usados em prosa em outras seções deste documento.

- MCP do Google Drive (`search_files` para localizar; `read_file_content`/
  `download_file_content` para efetivamente ler o conteúdo) — verificação
  do pré-requisito e Etapa 1. **Somente leitura**: `criar-site` nunca cria,
  move ou renomeia pasta de cliente no Drive — isso é responsabilidade
  exclusiva da skill `criar-cliente`.
- Skill `impeccable:impeccable` (via a ferramenta Skill; + subagente
  `impeccable:impeccable-finish-reviewer`, usado como escalonamento de QA,
  e `impeccable:impeccable-asset-producer` quando aplicável, ambos via a
  ferramenta Agent — nunca chamando scripts internos diretamente) — Etapa 2
  e Etapa 4 (direção, construção, QA final).
- Skill `ui-ux-pro-max:ui-ux-pro-max` (via a ferramenta Skill) — consulta
  pontual de dados concretos (paletas, tipografia, guidelines por stack,
  incluindo `--stack threejs` quando aplicável) nas Etapas 2 e 4.
- Skill `marketing:content-creation` (via a ferramenta Skill) — copy de
  conversão (headlines, CTAs, textos-chave) na Etapa 3.
- Skill `ui-ux-pro-max:ui-styling` (via a ferramenta Skill; parte do mesmo
  plugin do `ui-ux-pro-max`, não uma skill à parte) — referência de
  implementação shadcn/ui + Tailwind na Etapa 4.
- Comando de scaffolding do Next.js (ex: `create-next-app`) — Etapa 4,
  passo 1, para inicializar o projeto dentro do repositório já criado na
  Etapa 2.
- MCP `Originkit` — seções de marketing prontas (hero, navbar, pricing,
  cards, forms) — Etapa 4, primeira parada para componentes.
- MCP `Shadcn_UI` — registry oficial de componentes/blocos/temas shadcn —
  Etapa 4, para primitivas que o Originkit não cobre.
- MCP `21st.dev` — catálogo estendido de componentes + geração via IA —
  Etapa 4, fallback final quando nem Originkit nem Shadcn_UI cobrem.
- Skill `gsap-framer-scroll-animation` (via a ferramenta Skill) — Framer
  Motion, animação padrão de componente e mouse-following 2D/DOM — Etapa 4.
- Skills `gsap-skills:gsap-scrolltrigger` e `gsap-skills:gsap-react` (via a
  ferramenta Skill) — GSAP para animação de scroll complexa — Etapa 4.
- React Three Fiber, `@react-three/drei`, `@react-three/postprocessing`,
  `Lenis` — bibliotecas de código (não skills/MCPs do ambiente, usadas
  diretamente na implementação) — Etapa 4, só quando a direção aprovada
  pedir 3D/vídeo scroll-driven.
- `git` local — Etapa 2, passo 1 (`git init` do repositório vazio).
- Servidor de dev local do Next.js — Etapa 5.

## O que reportar sempre

- Caminho do repositório local (`D:\claude\sites\<cliente-normalizado>\`).
- Direção de design escolhida: modo, paleta, tipografia.
- O que foi criado nesta execução (páginas, seções, principais decisões).
- Resultado do QA final (`impeccable audit`/`polish`).

## Fora de escopo

- Deploy, hospedagem, e compra de domínio — mesmo a stack sendo
  Vercel-ready, o deploy em si fica fora; o usuário decide quando publicar.
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
