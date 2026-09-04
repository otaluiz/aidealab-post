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

0. **Antes de desenhar um slide do zero, confere os dois templates editáveis
   do design system da aidealab** — canvas ao vivo, referência oficial pro
   lettering, cor e layout desta etapa, documentados também na página
   "Sistema de Carrosséis":
   - **Template Carrossel** (modo sem referência — hook/CTA/explicações
     padrão): https://claude.ai/code/artifact/ffa5c39a-725c-4cfa-8209-75c647d7b9b7
   - **Template Post com Referência** (modo com referência — troca uma
     explicação pela moldura de citação): https://claude.ai/code/artifact/e418a430-2922-407b-90c7-4a17a9660d63
   - **Sistema de Carrosséis** (doc de cor/tipografia/regras, linka os dois
     acima): https://claude.ai/code/artifact/5bc39ef8-aeaa-41c2-a674-2015ffc258f8

1. **Tipografia e layout** (texto sempre nítido, na fonte da marca):
   `anthropic-skills:canvas-design` (via a ferramenta Skill) compõe cada slide
   como arte estática seguindo o template escolhido e os tokens do design
   system, no tamanho exato do Instagram — **1080×1440** (retrato, 3:4) por
   padrão. O Instagram feed corta acima de 4:5 (1080×1350); 1080×1440 fica
   fora desse limite e é exibido cropado no feed — formato escolhido
   explicitamente pelo cliente mesmo assim, ciente do corte. Saída em PNG.
   O texto **nunca** é gerado por IA de imagem.
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
   regra de fundos acima), então a questão nem chega a se colocar.

   **Erro recorrente a evitar: reaproveitar o layout full-bleed do hook/CTA
   (texto solto + `scrim`, sem card) num slide de explicação com fundo
   `bg-gradient`.** Já aconteceu de montar um carrossel inteiro (todas as
   explicações) copiando o padrão do hook/CTA — texto direto sobre a
   textura, eyebrow-chip e bloco de texto como dois elementos `absolute`
   soltos e distantes um do outro. Resultado: fundo parece vazio/genérico
   (a textura sozinha não sustenta a composição como uma imagem-sujeito
   sustenta) e o eyebrow fica visualmente desconectado do texto, com um
   vão morto no meio do slide. **Sempre que o fundo for `bg-gradient`,
   agrupa eyebrow + heading + body dentro de UM único card** (mesmo
   tratamento visual do `.ref-frame`: fundo translúcido escuro
   `rgba(8,11,20,0.72)`, `backdrop-filter: blur(12–14px)`, borda
   `1px solid rgba(245,237,231,0.16)`, `border-radius: ~20–24px`,
   `box-shadow` suave) — nunca como blocos `absolute` separados flutuando
   sobre a textura. Antes de gerar os PNGs finais, checa visualmente que
   nenhum slide de explicação ficou com esse vão vazio; se ficou, é o
   sintoma de ter pulado o card.

   **Lettering do hook e do CTA: escala editorial grande, não texto
   pequeno espremido no rodapé.** No hook e no CTA — sempre sem moldura,
   texto direto sobre a imagem — a composição usa a MAIOR escala
   tipográfica do carrossel e fica posicionada com respiro (nem colada no
   topo/rodapé, nem espremida numa faixa fina): condensada (Anton) na
   casa de 200–230px pra linha principal do hook (130–140px no CTA).

   **Hook: template de oclusão (objeto na frente do texto) sempre que a
   imagem der um recorte limpo.** O hook padrão não é foto full-bleed com
   scrim — é o "poster editorial": ground de cor da marca em gradiente
   (`linear-gradient(180deg, <cor> 0%, #000 100%)`), monumento em Inter 900
   atrás (z-index 3), sujeito recortado com alpha real por cima (z-index 5,
   `bottom: 0`, centralizado) cobrindo só a **faixa inferior** do monumento, e
   a script Tempting acima (z-index 6). Header e rodapé sobem para z-index 10,
   senão o sujeito passa por cima deles.

   **Antes de aplicar, testa o recorte — nem toda imagem serve.** Roda o rembg
   e avalia: precisa ser figura única e coerente, com silhueta fechada. Se a
   imagem for cena abstrata (gradiente, onda, textura) o rembg não tem sujeito
   pra separar e o hook fica full-bleed mesmo; se o recorte sair parcial
   (membro cortado, borda esfarrapada, fragmento solto), também fica
   full-bleed. Vale medir: fração de foreground entre ~5% e ~65%, preenchimento
   da bounding box acima de ~35%, e no máximo 1–2 blobs grandes — mas a decisão
   final é olhar o PNG recortado, porque a métrica não vê borda feia.

   **Fundo em gradiente (ground) só entra quando o sujeito for GERADO com
   recorte nativo — nunca com rembg sobre foto de banco.** Já aconteceu de
   aplicar oclusão em fotos de banco (rembg): mesmo passando nos números da
   avaliação acima, saiu com borda visivelmente cortada/colada — reprovado
   pelo cliente em três hooks ao mesmo tempo. rembg sobre foto que não foi
   pensada pra virar cutout produz silhueta imprecisa; gerar direto com
   `background: transparent` (OpenAI) ou remover fundo com o
   background-remover nativo do próprio gerador (Higgsfield
   `remove_background`, não rembg) dá alpha limpo desde a origem. Regra
   prática: se o sujeito veio de `img-ref`/banco existente → hook fica
   **full-bleed** (foto inteira, sem recorte, `scrim` + `.lockup`); se o
   sujeito foi gerado agora com recorte nativo → hook pode usar o template de
   oclusão (`.hook-ground` + `.hook-mon` + `.hook-script` + `.hook-subject`).

   **Quatro famílias de hook/CTA — alterna entre elas de carrossel pra
   carrossel, nunca repete a mesma em dois carrosséis seguidos de uma
   série.** O lockup tipográfico (Inter 900 + Tempting, ver acima) é fixo
   nas quatro; o que muda é o que está atrás e na frente do texto:

   - **A · Foto plena** — `img-ref`/banco existente, inteira, sem recorte,
     `scrim` escuro na base + `.lockup` por cima. Zero geração, custo 0.
     Usa quando já existe uma foto forte na pasta de referências do cliente.
   - **B · Ground de cor + sujeito** — o template de oclusão documentado
     acima: ground liso em gradiente da família (`Shade → #000`), sujeito
     GERADO com recorte nativo, base dissolvida com `mask-image` (ver
     regra abaixo). Usa quando o carrossel pede um objeto/figura isolada,
     sem cenário.
   - **C · Cenário + texto + sujeito** — cinematográfico: a cena INTEIRA
     (ambiente, luz, profundidade) fica no fundo, não um gradiente chapado.
     Documentado dois blocos abaixo.
   - **D · Banco `img-ref` do cliente** — a opção mais barata: pega uma foto
     do banco do próprio cliente, sem gerar nada. Documentada no próximo
     bloco.

   **Template D — banco `img-ref` do cliente, com upscale.** A pasta é
   local, sincronizada pelo Google Drive desktop — lê direto do disco, não
   pelo MCP do Drive (baixar por MCP devolve base64 no resultado da
   ferramenta e queima contexto à toa):
   `C:\Users\luizr\Meu Drive (aidealabbr@gmail.com)\Clientes\<cliente>\02-Materiais-Brutos\img-ref`.
   Regras:
   - **Nunca reusa a mesma imagem** — nem entre carrosséis, nem entre hook e
     CTA. Antes de escolher, confere quais já foram publicadas (compara com
     os PNGs finais dos carrosséis anteriores; hash perceptual resolve).
   - **Monta um contact sheet antes de escolher** (grade de miniaturas num
     único JPEG) em vez de abrir 18 imagens uma a uma — uma leitura em vez
     de dezoito.
   - **Escolhe pela ÁREA VAZIA, não só pela beleza:** o template não tem
     recorte, então o texto precisa de um céu/campo escuro amplo onde pousar.
     Cena com sujeito pequeno e horizonte baixo é ideal; imagem-textura sem
     sujeito (gradiente, padrão, mancha) não serve pra hook.
   - **O banco costuma ser de thumbs de 736px — sempre confere a resolução.**
     Abaixo de 1080×1440 passa no `upscale_image` do Higgsfield
     (provider `bytedance`, `resolution: "2k"` já basta; 4k é desperdício).
     Fluxo: `media_upload` (pega a `upload_url` presignada) → PUT dos bytes →
     `media_confirm` → `upscale_image` com `width`/`height` da origem.
   - Depois do upscale, corta pra 3:4 escolhendo a âncora vertical com
     critério: imagem 9:16 ancorada no TOPO preserva céu e sujeito; cortar
     pelo centro decapita a composição.
   - `scrim` em DUAS peças (`.scrim-top` e `.scrim-bottom`), não um só: a
     foto de banco não foi feita pra carregar tipografia, e escurecer o
     quadro inteiro mata a imagem. Escurece só onde o texto pousa.

   **Template C — cenário completo, o recorte é a MESMA geração, não uma
   segunda camada.** Gera uma cena única no gerador de imagem (Higgsfield
   `soul_2`, 3:4, pessoa/objeto de costas ou à distância dentro de um
   ambiente amplo — deserto, cordilheira, campo, horizonte) e roda o
   `remove_background` nativo **sobre essa mesma imagem**. A página empilha
   três camadas com o MESMO `object-fit: cover` e o mesmo enquadramento nas
   duas imagens (cena inteira e recorte):
   ```
   .scene         { position:absolute; inset:0; object-fit:cover; z-index:0; }  /* cena completa */
   .monument/.script                                            z-index:3      /* texto */
   .subject-scene { position:absolute; inset:0; object-fit:cover; z-index:5; }  /* recorte da MESMA cena */
   ```
   Como as duas imagens são a mesma geração no mesmo frame, o recorte cai
   exatamente sobre si mesmo — nenhum reposicionamento manual, nenhuma
   máscara de dissolução de base (ela seria supérflua aqui: a base do
   recorte já encosta na própria cena de origem, então não existe corte
   reto contra fundo estranho; aplicar a máscara do template B por hábito
   só duplicaria o sujeito como um fantasma). O andaime do pôster
   (2026/AIDEA LAB/crosshairs/régua/rodapé/dots) e a cor do monumento e da
   script se adaptam ao tom do céu da cena: céu claro → `.on-light`
   (monumento em tinta escura, andaime em tinta); céu escuro → `.on-dark`
   (monumento em creme, andaime em creme); a script leva sempre
   `text-shadow` porque cruza os dois tons na mesma composição.
   Validado no carrossel "Estilos Gráficos" parte 2 (hook "O luxo do
   EXCESSO", CTA "Ainda faltam 5 ESTILOS").

   **Custo Higgsfield por hook/CTA — preços conferidos na conta.** Por
   operação: `soul_2` (2k, 3:4) = **0,12 crédito**;
   `image_background_remover` = **1 crédito**; `bytedance_image_upscale`
   (2k ou 4k, preço plano) = **2 créditos**. Por peça:

   | Template | Operações | Crédito/peça | Par hook+CTA |
   |---|---|---|---|
   | A · Foto plena (já em 1080×1440) | nenhuma | 0 | 0 |
   | B · Ground + sujeito | 1 geração + 1 recorte | 1,12 | 2,24 |
   | C · Cenário + sujeito | 1 geração + 1 recorte | 1,12 | 2,24 |
   | D · Banco `img-ref` + upscale | 1 upscale | 2,00 | 4,00 |

   Dois pontos contra a intuição, os dois medidos e não estimados:
   - **B e C custam exatamente o mesmo.** A diferença entre os dois é só
     composição CSS (ground chapado vs. cena inteira atrás), não geração.
     Escolhe pelo resultado visual, nunca por orçamento.
   - **D (banco) é o MAIS CARO quando a imagem precisa de upscale** — 2
     créditos contra 1,12 de gerar do zero, porque o upscale tem preço plano
     e alto. "Usar o banco pra economizar" só economiza de fato se a imagem
     já estiver em 1080×1440 ou mais (aí é template A, custo 0). Diz isso ao
     cliente antes de assumir que reaproveitar sai mais barato.

   Confirma o preço atual com `get_cost:true` antes de gerar em lote — o
   catálogo e os preços do Higgsfield mudam.

   **Recorte harmonizado com a família de cor do carrossel.** Ao gerar um
   sujeito pra oclusão, a paleta do próprio sujeito (tecido, reflexo, luz de
   contorno) deve casar com o `--g-base` do ground — nunca uma cor
   competindo com a outra. Pede geração minimalista: um único realce de cor
   (o tom do ground) sobre superfície neutra (cinza, prata, grafite), não um
   objeto multicolorido/iridescente aleatório — isso também evita o efeito
   "colado" que reflexos caóticos de várias cores produzem contra um
   gradiente de cor única.

   **Base do sujeito SEMPRE dissolvida no fundo.** Recorte que termina em
   corte reto contra o gradiente lê como adesivo colado — foi exatamente o que
   o cliente reprovou. Aplica
   `mask-image: linear-gradient(180deg,#000 0%,#000 72%,rgba(0,0,0,0) 100%)`
   no sujeito. Sujeito escuro sobre a parte preta do ground disfarça sozinho e
   engana na revisão; sujeito claro denuncia na hora — por isso a máscara é
   regra fixa, não caso a caso.

   **Escala do sujeito: topo em ~438px de 1440 (altura ≈ 1002px), preservando
   o aspect do recorte.** Menor que isso o sujeito não encosta no monumento e
   sobra vão morto até o rodapé; maior, ele tapa o miolo da palavra e o
   monumento deixa de ser legível.

   **Par tipográfico do hook e do CTA: Inter 900 (monumento) + Tempting
   (script).** O lockup é: palavra-script em Tempting por cima, monumento em
   Inter 900 logo abaixo, e uma linha de apoio menor embaixo. O monumento é
   uma palavra só, em caixa alta, e leva um auto-ajuste de corpo por
   largura-alvo (mede o `<span>` interno, não o bloco — o bloco é full-width e
   o laço encolheria a palavra até zero); sem isso, trocar a copy estoura ou
   afunda o corpo, porque a contagem de caracteres muda a largura.

   **Tempting não tem NENHUM glifo acentuado — verificado lendo o `cmap` da
   fonte: cobre A-Z, a-z e 0-9 e mais nada.** Logo a palavra-script é SEMPRE
   caixa mista e sem acento (nem `ç`, nem `ã`, nem `ê`); quem carrega acento é
   o monumento, em Inter 900, que tem acentuação completa. Frase-script
   acentuada não dá erro: o glifo cai silenciosamente na fonte de fallback e
   quebra o lockup sem avisar — então valida a string antes de usar.

   **O encaixe da script no monumento é CALCULADO em runtime, nunca por `top`
   ou `margin` fixos.** A regra visual é: a **baseline da script cai no topo
   das caixas altas do monumento** — os swashes da Tempting descem por cima
   das letras, sem respiro entre os dois blocos. Valor fixo não entrega isso
   porque o auto-ajuste muda o corpo do monumento conforme o número de
   caracteres (AUTOMAÇÃO cai pra ~147px, DESIGN sobe pra ~251px) e a distância
   entre o topo da caixa de linha e o topo das caixas altas é proporcional ao
   corpo — o mesmo `top` produz encaixe colado num slide e um vão de 30px no
   outro. Foi exatamente esse o defeito reprovado.

   Depois de ajustar a largura do monumento, mede e reposiciona:
   - baseline dentro da caixa = `(line-height − (ascent + descent)) / 2 + ascent`,
     com `ascent`/`descent` de `TextMetrics.fontBoundingBox*`;
   - altura de caixa alta = `actualBoundingBoxAscent` sondando **"H"** — nunca
     a palavra inteira, porque til e cedilha (AUTOMAÇÃO) inflam a medida e o
     encaixe sai diferente de uma palavra sem acento;
   - hook (script e monumento absolutos): `script.top = capTopDoMonumento −
     baselineDaScriptNaCaixa`;
   - CTA (os dois no fluxo): `script.marginBottom = baselineScript −
     lineHeightScript − baselineMonumento + capHeightMonumento`.

   Com o encaixe calculado, diacrítico maiúsculo deixa de ser caso especial —
   o `Ê` de CONSISTÊNCIA se acomoda sozinho, sem margem manual.

   **Linha 2 é texto corrido normal — só a palavra-chave dentro dela troca
   pra serifada + cor de destaque, nunca a linha inteira, nunca rotacionada.**
   (Regra do sistema antigo Anton + Playfair, mantida para slides de conteúdo;
   hook e CTA seguem o par Inter + Tempting acima.)
   O hook/CTA tem duas linhas: linha 1 é a condensada grande (Anton), a
   clause de abertura (ex.: "5 SITES", "Salva os 5."); linha 2, logo abaixo,
   é a clause de fecho como texto corrido comum — condensada, escala bem
   menor (texto, não display) — e dentro dela **só a(s) palavra(s)-chave**
   (ex.: "inspiram", "precisar") troca de fonte pra serifada (Playfair 900,
   ~1.3–1.4× o tamanho das palavras ao redor) e cor pro accent do carrossel;
   o resto da linha ("que", "de verdade.", "Vai") continua em condensada/
   cream, no mesmo fluxo de texto, mesma baseline. Nunca: (a) a clause de
   fecho inteira em serifada, (b) uma linha flex separada com escalas muito
   diferentes por palavra, (c) `transform: rotate(...)` em qualquer parte.
   No hook a palavra-chave fica sem itálico (`font-style: normal`), no CTA
   em itálico.

   **Linha 2 fica "tucked" por baixo da linha 1 — colada, sobrepondo
   levemente a cauda das letras, nunca com respiro/gap embaixo do headline.**
   `margin-top` da linha 2 é NEGATIVO (não positivo): ~-26px no hook
   (headline 210px), ~-18px no CTA (headline 130–140px) — a proporção é
   ~12–16% negativo do tamanho da linha 1. É esse encaixe apertado, quase
   um leve overlap, que dá o efeito "serifada por baixo do texto da
   frente" que o cliente aprovou — linha 2 solta com espaço embaixo do
   headline (gap positivo) já foi tentado e rejeitado.

   Este é o template oficial validado pelo cliente, replicado nos canvas
   editáveis "Template Carrossel" e "Template Post com Referência" (ver
   links abaixo) — sempre confira esses canvas antes de desenhar um
   hook/CTA novo, em vez de reinventar a composição. Esses dois canvas são
   editados diretamente pelo cliente na UI do Claude Design de tempos em
   tempos — se um deles mudar, refaça o fetch (`WebFetch` na URL) antes de
   assumir que a composição documentada aqui ainda é a mais recente.

   **Moldura de referência (janela de navegador) sempre que o post citar
   uma fonte/site externo — independe da regra de moldura acima.** Quando
   o conteúdo do slide referencia algo específico e nomeável (um site, uma
   ferramenta, uma fonte externa), mostra essa referência dentro de uma
   janela de navegador estilizada: barra superior com os 3 pontos
   (vermelho/amarelo/verde) + pill com a URL, e dentro dela o **print
   real da página inicial** do que está sendo citado — nunca só o nome em
   texto grande. Busca o print via a imagem oficial de preview (`og:image`
   da página, feita pra redistribuição externa — mais confiável que
   screenshot ao vivo) ou, se a fonte bloquear acesso automatizado, troca
   por outra referência equivalente em vez de forçar.

   CSS/HTML pronto pra colar: `templates/ref-frame.html` (nesta pasta da
   skill) — `.ref-frame`/`.ref-topbar`/`.ref-dots`/`.ref-url`/`.ref-shot`/
   `.ref-body`/`.ref-name`/`.ref-tagline` pra citação, `.content-card` pro
   slide de explicação padrão com fundo `bg-gradient`. Validado nos
   carrosséis "importância do branding" (ref: logodesignlove.com) e
   "importância do design" (ref: lawsofux.com).

   **O `.eyebrow-chip` desse slide sempre diz "Referência" — nunca "Pra
   estudar" nem variação.** Nomenclatura fixa, corrigida depois de sair
   errada em produção; reaplica em qualquer carrossel futuro que tenha slide
   de citação.

   Essa moldura de
   referência aparece em QUALQUER tipo de fundo (bg-gradient ou img-ref) —
   ela não segue a regra "moldura só com bg-gradient" acima, porque é uma
   peça de citação, não um card de legibilidade de texto.

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
   irregular/desbotada, principalmente em caixa alta. O sistema tem 3
   **famílias** de acento possíveis — cada uma com 3 tons (Tint/Base/Shade):
   - **Amber** — tint `#F6E3AE`, base `#E9BA4B`, shade `#B3833A`
   - **Magenta** — tint `#F7C1D9`, base `#E94B91`, shade `#A82F63`
   - **Azul** — tint `#B7CBFA`, base `#4C7EF0`, shade `#2E52B8`

   Cada carrossel escolhe **uma família** e usa a **Base** — sólida, nunca
   gradiente — em toda palavra-chave, chip e detalhe de cor do carrossel
   (capa, explicações, CTA). O **Tint** é só pra fundo suave/hover (ex.:
   fundo de um chip secundário); o **Shade**, só pra borda ou estado
   pressionado quando precisar de mais contraste — nenhum dos dois entra em
   texto corrido. Nunca mistura duas famílias no mesmo carrossel, nem cor
   sólida num slide e gradiente noutro. Gradiente de texto não é uma técnica
   do sistema por padrão — só reconsiderar se o cliente pedir explicitamente.

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

**Renderiza via CDP com métricas explícitas, nunca por `--window-size`.**
`--window-size=L,A` dimensiona a *janela*, não o viewport: a 1080×1440 o Chrome
diagramou a página em 1064×1345 e devolveu um PNG 1080×1440 com o resto
preenchido pelo fundo do próprio `.slide` — 16px de faixa à direita e 95px
embaixo, que na tela parecem "um fundo por cima do outro". `--hide-scrollbars`
e `--headless=old` não resolvem (o segundo nem existe mais). O caminho correto
é abrir o Chrome com `--remote-debugging-port`, chamar
`Emulation.setDeviceMetricsOverride` com a largura/altura exatas e capturar com
`Page.captureScreenshot` + `clip`. Antes de cada shot, espera
`document.fonts.ready` e confirma via `Runtime.evaluate` que `innerWidth`/
`innerHeight` e o `.slide` batem com o alvo — se não baterem, falha alto em vez
de gravar um PNG errado.

**Valida nos pixels entregues, não no DOM.** Medir o DOM dentro de um iframe
de 1080×1440 é inútil: o iframe força o tamanho, o slide sempre reporta certo e
o teste passa enquanto os PNGs saem cortados — foi exatamente assim que um lote
de 25 slides quebrados passou num QA "25/25 OK". Abre o PNG final e afirma
sobre os pixels.

**Faixa uniforme na borda direita é a assinatura do corte; faixa embaixo não
prova nada.** Muitos slides terminam num scrim escuro chapado mais a margem
inferior do rodapé (~130px), então procurar "linha uniforme embaixo" reprova
render bom. Já uma coluna uniforme na borda direita nunca é design — é déficit
de viewport. Usa a borda direita como porta de entrada, e o tamanho exato do
arquivo como segunda checagem.

**Mede a geometria, não confia no olho.** Sobreposição de texto com
header/rodapé é defeito bloqueante e passa despercebido numa revisão visual de
20+ slides. Afirma por código, pra cada slide, que nenhum bloco de conteúdo
(`.lockup`, `.ref-frame`, `.content-card`, `.eyebrow-chip`, `.cta-sub2`) passa
do topo do rodapé nem invade o header. Reporta a folga em px de cada slide —
folga negativa reprova o lote.

**Ancoragem: rodapé e blocos de base SEMPRE ancorados por `bottom`, nunca por
`top` em pixel absoluto.** Rodapé preso em `top: 1200px` funciona no formato em
que foi calibrado e quebra silenciosamente quando a altura da arte muda — o
rodapé fica parado enquanto todo o resto desce, e o conteúdo passa por cima
dele. Mesmo vale ao mudar de formato: bloco ancorado por `bottom` se reposiciona
sozinho; bloco ancorado por `top` com altura automática (a moldura de
referência é o caso clássico) mantém o topo e joga a diferença toda como vão
morto antes do rodapé — aí o ajuste é na altura do conteúdo interno
(`.ref-shot`), não na posição.

**Confere se a contagem que a copy promete bate com o número de slides.** Um
carrossel com 3 referências anunciava "5 SITES" no hook e no CTA. Antes de
renderizar, cruza todo número citado na copy (hook, CTA, legenda) com a
quantidade real de slides de conteúdo.

**Nenhuma imagem se repete entre carrosséis.** Antes de fechar a seleção,
compara o hash do conteúdo das imagens de todos os carrosséis do cliente, não
o nome do arquivo — cópias com nomes diferentes (`hook.b64` vs `hook_new.b64`)
escondem a repetição. Já aconteceu de um carrossel sair com hook e CTA
reciclados de dois outros posts do mesmo feed.

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
