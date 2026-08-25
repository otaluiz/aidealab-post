---
name: criar-post
description: Cria um post de Instagram (carrossel ou imagem única) on-brand para um cliente da aidealab, a partir da identidade e referências já organizadas no Drive pela criar-cliente. Segue um "post design system" de 3 estruturas (cor, tipografia, layout) e storytelling de copywriting (hook, problema, explicação, solução, CTA). Renderização híbrida — tipografia/layout como arte estática nítida via canvas-design, imagem só via Comfy Cloud MCP. Dispara com "criar post <cliente>" / "novo post <cliente>" / "criar carrossel <cliente>". Para em dois checkpoints (design system, copy) antes de renderizar. Não publica no Instagram.
---

# Criar post

Cria um post de Instagram para um cliente da aidealab — **carrossel** (padrão,
arquitetura completa) ou **imagem única** (variação simples do mesmo sistema) —
a partir da identidade de marca e das referências já organizadas no Drive pela
`criar-cliente`. O objetivo é post on-brand e profissional, não genérico: a
direção segue um **post design system** enxuto (3 cores, 2–3 fontes, 2–3 templates
reusáveis) e a copy segue storytelling de conversão.

A skill entrega o post pronto e o salva no Drive. **Não publica no Instagram** —
isso é responsabilidade de uma skill futura (`post-instagram`), respeitando o
portão humano da pasta `06-Aprovados-para-Postar`.

## Quando usar

Pedido do tipo "criar post \<cliente\>" / "novo post \<cliente\>" / "criar
carrossel \<cliente\>".

### Pré-requisito

A skill busca a pasta do cliente dentro de `Clientes` (mesmo `parentId` usado
por `criar-cliente`: `1xHuFxkYD0INTpdZbzBZLRBy-X3tVM-rv`), case-insensitive. Se
a pasta não existir, a skill **para e avisa** o usuário para rodar
`criar-cliente` primeiro — **não** a invoca automaticamente. Uma
responsabilidade por skill é a convenção do projeto (ver
`agente aidealab/skills/README.md`); `criar-post` só consome a estrutura que
`criar-cliente` garante, nunca a cria.

## Diretriz de design — "Post design system" (3 estruturas)

Síntese das boas práticas de carrossel adotadas pela agência:

1. **COR** → 3 cores: **Primária**, **Background**, **Accent**. A mesma
   paleta pode variar de contraste conforme o slide (ex: mais glow na capa,
   mais neutro no conteúdo) — a paleta em si não muda, só a aplicação.
2. **TIPOGRAFIA** → 2 fontes obrigatórias: **Display** (headline) + **Body**
   (texto), nenhuma fixa em serifada/sans — vem das referências do cliente +
   sugestão da skill. **+ 1 fonte opcional — "serifada de destaque"**: quando
   a referência do cliente pedir um efeito editorial tipo "dupla sans+serif"
   (ex: post de referência "best *font* pairings" — palavra de ênfase numa
   serifada/script elegante, dramática, cercada de texto em sans bold), usa
   uma terceira fonte **só na capa (hook) e no CTA**, nunca em slide de
   conteúdo — são os dois momentos de maior carga; conteúdo não compete por
   atenção com essa dupla. **Cuidado com licença**: fontes de referência
   vindas de post de terceiros (ex: Instagram de design) costumam ser
   comerciais e "grátis só para uso pessoal" (ex: fontes de script/
   calligraphy do dafont.com/MyFonts) — **checar a licença antes de embutir**
   num cliente de verdade; se não for clara pra uso comercial, substituir por
   equivalente do Google Fonts com o mesmo efeito visual (ex: Fraunces,
   Bodoni Moda, Instrument Serif no lugar de uma script comercial).
3. **LAYOUT (template system)** → **headline fixa** (mesma posição em todos os
   slides), **margem consistente**, **2–3 templates reusáveis + thumb** que se
   reusam sempre, mantendo o **grid do feed coerente**. Zonas de cada slide:
   headline / content zone / rodapé com @handle.

O conteúdo dos slides segue storytelling de copywriting, não só a estrutura
visual: **hook → problema → explicação → solução → CTA**. A capa é o hook que
para o scroll; cada slide puxa o swipe para o próximo; o último é o CTA.

## Repositório de design system do cliente

Por cliente, em `D:\claude\posts\<cliente-normalizado>\` (normalização: minúsculas,
espaços viram hífen — ex: "Hora da Chipa" → `hora-da-chipa`):

- `design-system/` — tokens (3 cores, 2–3 fontes) + specs dos 2–3 templates de
  slide + `index.html` de preview **importável no Claude Designer** (para
  acompanhamento visual e reuso).
- `output/` — PNGs finais dos posts gerados.

`git init` local no primeiro uso. Este é o design system **de post**, separado e
diferente do design system **de site** (skill `criar-site`) — não compartilham.

A skill é **idempotente, em dois modos**:
- **Bootstrap** (primeiro post do cliente): define o design system (Etapa 2) e
  para no Checkpoint 1.
- **Reuso** (posts seguintes): carrega o design system existente e pula direto a
  produção do post novo — não redecide cor/fonte/template.

## Etapa 0 — Pré-requisito e formato

1. Verifica o pré-requisito (pasta do cliente existe; senão para e avisa).
2. **Pergunta o formato logo no início: imagem única ou carrossel.** Carrossel é
   a arquitetura completa (capa + narrativa entre N slides); imagem única é o
   caso simples do mesmo sistema (1 slide). O resto do fluxo se adapta.

## Etapa 1 — Coleta de referências

Lê (não só lista) o conteúdo da pasta do cliente no Drive: usa `search_files`
para localizar e efetivamente lê — `read_file_content` para texto,
`download_file_content` seguido de leitura visual para imagens:
- `00-Identidade-e-Tom` — identidade de marca e tom de voz.
- `01-Referencias/Instagram` — referências específicas de post/carrossel.

Se o material for insuficiente para definir a direção (pastas vazias ou quase),
a skill **pergunta diretamente ao usuário** pelo contexto de marca/negócio em
vez de travar ou inventar.

## Etapa 2 — Design system do post (bootstrap; pulado no modo reuso)

Só roda se o cliente ainda não tem `D:\claude\posts\<cliente-normalizado>\design-system\`.

1. Define as **3 cores** (Primária/Background/Accent) e as fontes
   (Display + Body obrigatórias; + Serifada de destaque opcional, só se a
   referência do cliente pedir o efeito editorial de dupla sans+serif — ver
   diretriz acima). O par/trio tipográfico vem das referências que o usuário
   mandar + sugestão da skill — não há default fixo serifada/sans, e sempre
   checando licença antes de embutir uma fonte específica de referência.
2. Define **2–3 templates de slide** reusáveis com headline fixa, margens
   consistentes e rodapé @handle, mantendo o grid do feed coerente.
3. **Autoridade de design**: fontes reais do cliente (`identidade-e-tom.md` —
   cores/fontes já em produção no site/marca, quando existir) +
   `references/principios-design.md` desta skill (regras de capa/carrossel) +
   `anthropic-skills:canvas-design` (via a ferramenta Skill) como filosofia de
   composição visual. **`ui-ux-pro-max:banner-design` e
   `ui-ux-pro-max:design-system` não são consulta rápida** — validado no
   dogfooding com a aidealab: são pipelines de produção completos próprios
   (scripts Python/Node, pesquisa no Pinterest, geração via Gemini,
   screenshot via chrome-devtools) que divergem da arquitetura desta skill
   (canvas-design + Comfy Cloud + agent-browser) — não invocar esperando uma
   resposta pontual; as decisões de cor/fonte/layout ficam com a skill
   mesmo, a partir das fontes acima.
4. Persiste tudo no repo do cliente (tokens + specs dos templates +
   `index.html` de preview) **e publica o mesmo preview como Artifact** (via
   a ferramenta Artifact) — essa é a superfície de acompanhamento visual
   padrão desta skill; republica no mesmo link a cada ajuste. Claude Design
   (via DesignSync) é uma alternativa disponível, mas não o padrão — só usar
   se o usuário pedir explicitamente.

**Checkpoint 1**: apresenta o design system (3 cores, fontes, 2–3 templates,
preview) e aguarda aprovação explícita antes de produzir qualquer post. Refina e
reapresenta se o usuário pedir ajustes.

## Etapa 3 — Conteúdo e copy

1. Recebe o tema/objetivo do post do usuário.
2. Escreve a copy com o arco **hook → problema → explicação → solução → CTA**
   distribuído nos slides (no formato imagem única, colapsa num único frame
   forte: hook + CTA).
3. **Skills de conteúdo** (Corey Haines, via a ferramenta Skill):
   `marketing-skills:social` como primária (carrossel, slide-by-slide, hooks),
   reforçada por `marketing-skills:copywriting` (headlines/CTA),
   `marketing-skills:marketing-psychology` (gatilhos de persuasão) e
   `marketing-skills:copy-editing` (polimento final). Usa
   `marketing-skills:content-strategy` para ideação de tema quando o usuário não
   trouxer um pronto.
4. **Legenda (caption) do post** — texto que acompanha o post no feed,
   **separado** do texto que já está nos slides (nunca repete a headline
   literalmente). Reforça o hook na primeira linha (o que aparece antes do
   corte "ver mais"), desenvolve o storytelling com quebras de linha pra
   leitura fácil, e fecha com um CTA em texto (complementa, não repete, o CTA
   visual do último slide). Skill: `marketing:content-creation` (via a
   ferramenta Skill) para a estrutura hook/corpo/CTA de legenda de Instagram.
5. **Hashtags** — 3 a 5, mix de branded (`#aidealab` ou equivalente do
   cliente) + nicho (tema do post) + alcance amplo (categoria/indústria). Vai
   no fim da legenda ou no primeiro comentário — perguntar preferência do
   cliente na primeira execução e reusar depois.

**Checkpoint 2**: apresenta a copy + a estrutura slide-a-slide **+ legenda e
hashtags** e aguarda aprovação explícita antes de renderizar. Nenhum PNG é
gerado antes disso.

## Etapa 4 — Construção (render híbrido)

1. **Tipografia e layout** (texto sempre nítido, na fonte da marca):
   `anthropic-skills:canvas-design` (via a ferramenta Skill) compõe cada slide
   como arte estática seguindo o template escolhido e os tokens do design
   system, no tamanho exato do Instagram — **1080×1350** (retrato) por padrão;
   1080×1080 (quadrado) como opção. Saída em PNG. O texto **nunca** é gerado por
   IA de imagem.
2. **Camada de imagem** (fundos/ilustrações on-brand, quando o template pedir):
   gera via **Comfy Cloud MCP**, guiada pela skill `marketing-skills:image`
   (prompt e otimização). A imagem entra na composição do `canvas-design` —
   nunca carrega o texto.

   **Escolha e alternância de modelo — não fixa um único modelo para todo o
   post.** Antes de gerar, classifica a necessidade daquela imagem específica
   e escolhe o caminho conforme o tipo:
   - **Fundo abstrato / textura / glow / padrão geométrico** (a maioria dos
     fundos de carrossel — ex: o design system da aidealab em
     `D:\claude\posts\aidealab\design-system\tokens.json`, estética "neon
     tech"): `run_template` ou `submit_workflow` no Comfy Cloud com pipeline
     OSS — "melhores modelos gratuitos", mais rápido e mais barato; primeira
     escolha por padrão.
   - **Foto realista** (produto, ambiente, pessoa, cena): `partner_generate`
     com provedor parceiro (Flux, Ideogram, ou `google/*` via Gemini como
     alternativa) — maior fidelidade fotográfica que os pipelines OSS
     cobrem.
   - **Ilustração estilizada/vetorial** (ícone, mascote, elemento gráfico):
     `run_template` com modelo vocacionado a vetor (ex: Recraft) quando o
     Comfy servir esse tipo; senão `partner_generate`.
   - Antes de cada geração, consulta `search_models` e/ou
     `get_prompting_guide` no Comfy Cloud para confirmar o que está
     disponível **agora** — o catálogo de modelos muda, não assume nome de
     modelo fixo de execuções anteriores.
   - Se o resultado não atender (texto ilegível aparecendo na imagem, cor
     fora da paleta do cliente, artefato visual, composição errada) —
     **alterna para outro modelo/provedor da mesma categoria** antes de
     aceitar; não insiste indefinidamente no mesmo modelo nem aceita
     resultado abaixo do padrão.
   - `wait_for_job`/`get_output` para colher o resultado, independente do
     caminho escolhido acima.

   **Harmonia de cor entre as imagens do carrossel:** todo o banco de imagens
   usado num mesmo carrossel — geradas ou de referência (`img-ref`) — precisa
   soar da mesma paleta (mesma família de cor do design system do cliente,
   ex.: azul+dourado). Antes de finalizar a seleção, descarta ou substitui
   qualquer imagem cuja cor dominante destoe das demais (ex.: uma imagem
   magenta/laranja quente isolada num set azul+dourado), mesmo que a imagem
   em si seja boa — a coerência do conjunto vem antes da imagem individual.

   **Fundos-textura (`bg-gradient`) só nas explicações, nunca no hook/CTA.**
   Texturas abstratas de gradiente (pasta `bg-gradient` do cliente) só entram
   nos slides de explicação/conteúdo do meio do carrossel — nunca na capa
   (hook) nem no slide de CTA, que sempre usam imagem de referência (`img-ref`)
   ou gerada com sujeito/composição mais forte. Dentro das explicações,
   alterna entre `bg-gradient` e outras imagens de referência — nunca usa
   `bg-gradient` em todos os slides de explicação do mesmo carrossel.

   **Moldura (card/frame com blur atrás do texto) só quando o fundo é
   `bg-gradient`.** Regra fechada, não uma preferência: moldura entra
   **somente** nos slides cujo fundo é uma textura `bg-gradient` (ela existe
   pra dar contraste contra a textura). Em qualquer slide com imagem de
   referência (`img-ref`) ou gerada, o texto vai direto sobre a imagem — com
   `scrim`/gradiente escuro por trás pra legibilidade, nunca dentro de um
   card. **Nunca usa moldura no hook (capa) nem no CTA**, mesmo que algum
   deles use `bg-gradient` — hook e CTA sempre usam `img-ref`/gerada (ver
   regra de fundos acima), então a questão nem chega a se colocar. No hook,
   o texto vai direto sobre a imagem, sem card — grande, com destaque forte
   (a maior escala tipográfica do carrossel, incluindo gradiente de cor na
   palavra-chave quando fizer sentido) e disposto pra parar o scroll.

   **Header/rodapé sempre em branco sólido com sombra, nunca some contra a
   imagem.** O lockup do topo (`AIDEA LAB` / categoria) e o rodapé (`@handle`
   + dots) usam branco puro com text-shadow forte (nunca a cor cream/dim do
   corpo de texto) — precisam ficar legíveis em qualquer ponto de qualquer
   imagem de fundo, clara ou escura, sem depender de moldura.

   **Nunca deixa texto encostar ou sobrepor o header/rodapé.** No hook e no
   CTA — onde o texto fica solto sobre a imagem, sem moldura — garante
   margem de respiro clara entre a última linha de texto e a faixa do
   rodapé (`@handle`/dots) antes de aceitar o slide; overlap de texto é
   defeito bloqueante, não detalhe estético.

   **Toda palavra-chave/serifada em destaque leva UMA cor sólida do design
   system — nunca gradiente de duas cores no texto.** Testado e revertido:
   gradiente (ex.: azul→magenta) na palavra em si deixa o texto com aparência
   irregular/desbotada, principalmente em caixa alta. Cada slide escolhe
   **uma** cor de acento (normalmente a cor de acento do design system, ex.:
   amber) e aplica ela consistente em toda palavra/linha de destaque daquele
   carrossel — capa, explicações e CTA. Nunca mistura cor sólida num slide e
   gradiente noutro do mesmo post. Gradiente de texto não é uma técnica do
   sistema por padrão — só reconsiderar se o cliente pedir explicitamente.

   **Cuidado com cascata CSS ao combinar `.amber` (ou similar) com outras
   classes de mesma especificidade.** Se a classe base (`.line`,
   `.headline-sans` etc.) e a classe de cor (`.amber`) têm a mesma
   especificidade, quem vem depois no stylesheet vence — não a ordem das
   classes no HTML. Isso já causou texto "amber" renderizando branco por
   engano. Pra eliminar a ambiguidade, aplica a cor de destaque via
   `style="color:var(--amber)"` inline no elemento, em vez de confiar só na
   ordem das classes.

   **Chip de destaque (fundo em cor sólida ou gradiente atrás de uma palavra
   curta) como técnica extra, usada em alguns momentos — não em todo
   slide.** Inspirado nas referências de design salvas em
   `01-Referencias/Instagram` do cliente (ex.: os posts estilo "Design
   Trends" com labels tipo `VISION 2030` e `key idea` em blocos de cor
   sólida): aplica um fundo (cor sólida do design system, ou gradiente se
   fizer sentido ali especificamente) com cantos arredondados e **texto
   branco por cima (nunca escuro)** — o contraste do texto branco chapado
   é maior que o de texto escuro sobre a cor de acento, mesmo em cores
   claras como amber/dourado; usa um `text-shadow` leve se precisar de
   reforço — atrás de uma palavra ou frase curta — normalmente o
   eyebrow/label de um slide com moldura, ou uma chamada de ação isolada
   (ex.: "Comenta 'PALAVRA'" no CTA). Não é pra virar padrão fixo repetido
   em todo slide — é uma variação pontual pra dar contraste extra e puxar o
   olho pra 1-2 pontos específicos do carrossel. Essa é uma técnica
   separada do destaque de palavra-chave em texto corrido (que usa cor
   sólida, não fundo).

   **Sempre revisita as referências de design do cliente antes de montar um
   carrossel novo.** A pasta `01-Referencias/Instagram` (Drive, estrutura da
   `criar-cliente`) guarda prints/posts que o cliente ou eu já separamos como
   inspiração de tratamento visual (tipografia, chips, composição) — consulta
   essa pasta como parte da Etapa 2/4, não só a paleta e os tokens já
   fixados; ela é onde novas técnicas de destaque (como o chip acima) devem
   ser garimpadas antes de inventar do zero.

## Etapa 5 — Preview e QA

Antes de apresentar, testa os slides renderizados com a skill `agent-browser`
(via a ferramenta Skill): confere legibilidade no mobile, que não há corte de
texto, que o grid do feed fica coerente entre os slides, e que nenhuma
composição quebrou. Se encontrar problema, corrige antes de apresentar — não
entrega post quebrado para revisão. Depois mostra os PNGs (screenshots) para o
usuário revisar.

## Etapa 6 — Entrega

Salva os PNGs finais no Drive via `create_file`: em `04-Carrosseis` (o material
de trabalho) e/ou `06-Aprovados-para-Postar` (quando o usuário aprovar para
postar). Junto, salva a **legenda + hashtags** (Etapa 3) como um arquivo de
texto na mesma pasta (ex: `legenda.txt`) — a `post-instagram` futura vai
precisar desse texto tanto quanto dos PNGs. Se o MCP do Drive conectado não
subir binário de imagem, salva os PNGs localmente no `output/` do repo e
reporta o caminho para o usuário subir. **Não publica no Instagram.**

Reporta: caminho do repo local, resumo do design system usado (3 cores,
fontes, template escolhido), arquivos gerados (PNGs + legenda/hashtags), e
onde foram salvos.

## Ferramentas necessárias

Nomes de skill abaixo são os nomes completos (`plugin:skill`) que a ferramenta
Skill do Claude Code resolve.

- MCP do Google Drive (`search_files` para localizar; `read_file_content`/
  `download_file_content` para ler; `create_file` para subir PNG de saída) —
  Etapas 0, 1 e 6. **Nunca** cria, move ou renomeia pasta de cliente — isso é
  exclusivo da `criar-cliente`.
- Skill `anthropic-skills:canvas-design` (via a ferramenta Skill) — composição
  visual dos slides → PNG; motor principal de render (Etapas 2 e 4).
- Skills `marketing-skills:social`, `marketing-skills:copywriting`,
  `marketing-skills:marketing-psychology`, `marketing-skills:copy-editing`,
  `marketing-skills:content-strategy`, `marketing-skills:image` (Corey Haines,
  via a ferramenta Skill) — conteúdo/narrativa (Etapa 3) e guia de imagem
  (Etapa 4). Plugin `marketing-skills@marketingskills`.
- Skill `marketing:content-creation` (via a ferramenta Skill) — estrutura de
  legenda de Instagram (hook/corpo/CTA) e boas práticas de hashtag na Etapa 3.
  Plugin `marketing` — distinto do `marketing-skills@marketingskills` (Corey
  Haines) usado acima; os dois coexistem, papéis diferentes.
- Comfy Cloud MCP (`partner_generate`, `run_template`, `submit_workflow`,
  `search_models`, `get_prompting_guide`, `wait_for_job`, `get_output`) —
  geração da camada de imagem com escolha/alternância de modelo conforme o
  tipo de necessidade (Etapa 4). Gemini via `gemini-api-dev` /
  `partner_generate google/*` como opção dentro dessa escolha.
- **Não usar** `ui-ux-pro-max:banner-design`/`design-system` como consulta de
  design — são pipelines de produção completos com toolchain própria
  (Python/Node/Pinterest/Gemini/chrome-devtools), divergentes desta skill;
  validado no dogfooding com a aidealab (ver spec, seção "Aprendizados").
- Skill `agent-browser` (via a ferramenta Skill) — QA visual dos PNGs e preview
  do design system (Etapa 5).
- Ferramenta **Artifact** — publica o preview do design system (`index.html`)
  como Artifact na conversa; superfície padrão de acompanhamento visual
  (Etapa 2). Republica no mesmo link a cada ajuste, em vez de criar um novo.
- Ferramenta **DesignSync** (Claude Design, `claude.ai/design`) — alternativa
  para acompanhamento visual, **não é o padrão desta skill**; usar só se o
  usuário pedir explicitamente (testado no dogfooding com a aidealab — o
  usuário preferiu iterar via Artifact, interface do Claude Design achada
  mais lenta pra esse fluxo).
- `git` local — repo de design system do cliente (Etapa 2).

## O que reportar sempre

- Caminho do repositório local (`D:\claude\posts\<cliente-normalizado>\`).
- Design system usado: 3 cores, fontes, template escolhido.
- O que foi gerado nesta execução (formato, número de slides) e onde foi salvo.
- Se foi modo bootstrap (definiu o design system) ou reuso (usou o existente).

## Fora de escopo

- Publicar/agendar no Instagram — skill `post-instagram` futura, separada.
- Compartilhar o design system com a `criar-site` — são design systems
  diferentes (post ≠ site), repos separados.
- Posts em vídeo / Reels — só imagem estática por enquanto.
- Criar, mover ou renomear pastas de cliente no Drive — exclusivo da
  `criar-cliente`; `criar-post` só lê a estrutura e salva a saída.
- Gerar o texto do post por IA de imagem — tipografia é sempre composta nítida
  via `canvas-design`; o gerador de imagem cobre só fundo/ilustração.
- Entregar sem aprovação — a skill para nos Checkpoints 1 e 2.
