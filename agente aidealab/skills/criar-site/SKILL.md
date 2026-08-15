---
name: criar-site
description: Gera um site novo (React + Next.js) para um cliente da aidealab a partir das referências e identidade de marca já organizadas no Drive pela criar-cliente. Usa impeccable como espinha dorsal de direção de design anti-slop, construção e QA final, consultando ui-ux-pro-max para dados concretos e os MCPs Shadcn_UI/21st.dev para componentes. Dispara com "criar site <cliente>" / "crie o site do cliente <cliente>" / "novo site <cliente>". Para em dois checkpoints de aprovação (direção de design, plano de conteúdo) antes de escrever qualquer código.
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

Lê, da pasta do cliente no Drive:
- `00-Identidade-e-Tom` — identidade de marca e tom de voz.
- `01-Referencias/Site` — referências específicas de site.
- `01-Referencias/Instagram` — usada como apoio só se `Site` estiver vazia
  (consistência visual com o que já existe da marca).

Se o material encontrado for insuficiente para definir uma direção de design
(pastas vazias ou quase vazias), a skill **pergunta diretamente ao usuário**
pelo contexto de marca/negócio em vez de travar ou inventar.

## Etapa 2 — Direção de design

1. Invoca a skill `impeccable` (via a ferramenta Skill/Agent — comando
   `shape`, ou o fluxo de novo trabalho quando for o primeiro site do
   cliente) com o material coletado na Etapa 1 como contexto. `impeccable`
   decide o modo (`Persuade` — site de cliente é página de
   marketing/vendas) e produz a direção de design anti-slop.
2. Quando `impeccable` precisar de um dado concreto rápido (ex: opções de
   paleta ou par tipográfico para a vibe identificada), consulta a skill
   `ui-ux-pro-max` (via a ferramenta Skill) como referência pontual — ela
   não é mais a dona da persistência do design system, só um banco de dados
   de apoio.
3. Apresenta ao usuário: modo escolhido, paleta/tipografia, direção visual
   geral.

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
   GitHub — fica fora de escopo por enquanto). Stack fixa para todo site:
   React + Next.js (Vercel-ready) — não é mais decidida caso a caso.
2. A skill `impeccable` (via a ferramenta Skill/Agent) constrói o site
   seguindo a direção aprovada no Checkpoint 1 e o plano de conteúdo
   aprovado no Checkpoint 2, persistindo o contexto do projeto em
   `PRODUCT.md`/`DESIGN.md`.
3. **Componentes**: busca primeiro no MCP `Shadcn_UI` (registry oficial —
   componentes, blocos pré-montados, temas) para primitivas e composições
   padrão. Quando precisar de algo mais específico que o registry oficial
   não cobre, busca ou gera no MCP `21st.dev` (catálogo comunitário mais
   amplo + geração de componente via IA).
4. **Animação**: usa a skill `gsap-framer-scroll-animation` (Framer Motion)
   como padrão para transições e microinterações de componente — mais
   idiomático em React. Usa as skills `gsap-skills:gsap-scrolltrigger` e
   `gsap-skills:gsap-react` (GSAP) especificamente para animação de scroll
   complexa (pin, scroll horizontal, coreografia), onde GSAP é claramente
   mais forte que Framer Motion — as duas famílias cobrem terrenos
   diferentes, não são redundantes entre si.
5. **QA final**: antes de ir para a Etapa 5, invoca `impeccable audit` +
   `impeccable polish` (ou o subagente `impeccable-finish-reviewer`, via a
   ferramenta Agent) sobre o site construído.

**Ponto de extensão**: é aqui — e na Etapa 2 — que futuras skills de
desenvolvimento de site (a serem adicionadas pelo usuário ao ambiente) podem
entrar sem reescrever o fluxo inteiro. Hoje, sem essas skills adicionais, a
construção segue o pipeline `impeccable` descrito acima.

## Etapa 5 — Preview

Sobe o servidor de dev local do Next.js e mostra o site rodando para o
usuário revisar antes de finalizar.

## Etapa 6 — Relatório final

Reporta: caminho do repositório local, direção de design escolhida
(paleta/tipografia/modo), resumo do que foi criado, e resultado do QA final
(`impeccable audit`/`polish`).

## Ferramentas necessárias

- MCP do Google Drive (`search_files`) — verificação do pré-requisito e
  Etapa 1.
- Skill `impeccable` (+ subagentes `impeccable-finish-reviewer` e
  `impeccable-asset-producer` quando aplicável, invocados via as
  ferramentas Skill/Agent, não chamando scripts internos diretamente) —
  Etapa 2 e Etapa 4 (direção, construção, QA final).
- Skill `ui-ux-pro-max` (via a ferramenta Skill) — consulta pontual de
  dados concretos (paletas, tipografia, guidelines por stack) nas Etapas 2
  e 4.
- Skill `ui-styling` — referência de implementação shadcn/ui + Tailwind na
  Etapa 4.
- MCP `Shadcn_UI` — registry oficial de componentes/blocos/temas shadcn —
  Etapa 4.
- MCP `21st.dev` — catálogo estendido de componentes + geração via IA —
  Etapa 4, quando o registry oficial não cobre o necessário.
- Skill `gsap-framer-scroll-animation` — Framer Motion, animação padrão de
  componente — Etapa 4.
- Skills `gsap-skills:gsap-scrolltrigger` e `gsap-skills:gsap-react` — GSAP
  para animação de scroll complexa — Etapa 4.
- `git` local — Etapa 4.
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
