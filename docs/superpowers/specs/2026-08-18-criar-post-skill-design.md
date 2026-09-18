# Skill: criar-post

## Contexto

A aidealab (agência de conteúdo Instagram) organiza clientes no Google Drive
dentro de `Clientes` (ID `1xHuFxkYD0INTpdZbzBZLRBy-X3tVM-rv`), uma subpasta por
cliente, com a estrutura garantida pela skill `criar-cliente`. Já existe a skill
`criar-site` (gera o site do cliente via `impeccable`). O `README.md` de skills
planejava "criar carrossel" e "postar no Instagram" como skills futuras.

Esta é a spec da skill **`criar-post`**, que assume o papel de "criar carrossel"
(e imagem única). Ela gera posts de Instagram on-brand a partir da identidade e
das referências já organizadas no Drive, seguindo:

- As diretrizes do vídeo de referência ("You're Making Carousels Wrong (Fix in
  3 Easy Steps)"), sintetizadas como um **"post design system"** de 3
  estruturas: COR, TIPOGRAFIA e LAYOUT.
- Boas práticas de **copywriting/storytelling** (hook → problema → explicação →
  solução → CTA).

Convenções do projeto respeitadas: skill = só `SKILL.md` (instrução, sem código
externo); uma responsabilidade por skill; consome MCPs/skills já conectados.

### Diretriz-fonte — "Post design system" (3 estruturas)

1. **COR** → 3 cores: Primária, Background, Accent.
2. **TIPOGRAFIA** → 2 fontes: Display + Body. O par NÃO é fixo em serifada/sans
   — vem de referência do usuário + sugestão, por cliente.
3. **LAYOUT (template system)** → headline fixa, margem consistente, **construir
   2–3 templates reusáveis + thumb e reusar sempre**, mantendo o **grid do feed
   coerente** (zonas: headline / content / rodapé com @handle).

## Objetivo

Uma skill (`criar-post`) que, dado um cliente já existente no Drive, cria um
post de Instagram (carrossel ou imagem única) on-brand: define/reusa o design
system de post do cliente, escreve a copy com storytelling, compõe os slides
como arte estática nítida e entrega os PNGs no Drive — sem publicar.

## Decisões de arquitetura

- **Escopo**: carrossel-first; imagem única é variação do mesmo sistema (1 slide
  em vez de N). Uma skill cobre os dois; pergunta o formato no início. Vídeo/
  Reels fora.
- **Renderização híbrida**: tipografia e layout SEMPRE compostos como arte
  estática nítida (via `anthropic-skills:canvas-design` + design tokens, na
  fonte da marca) — nunca texto gerado por IA. O gerador de imagem (Comfy Cloud
  MCP; Gemini opcional) entra SÓ na camada de imagem (fundos/ilustrações).
- **Design system de post ≠ design system de site**: skills diferentes,
  sub-skills diferentes, repos separados. NÃO compartilham com `criar-site`.
- **Um design system de post por cliente**, em repo git local importável no
  Claude Designer (acompanhamento visual + reuso).
- **Publicar fica fora**: vira `post-instagram` (skill futura). `criar-post`
  entrega o post pronto/aprovado no Drive; um humano aprova antes de publicar
  (pasta `06-Aprovados-para-Postar`).
- **Stack de sub-skills próprio** (distinto do `impeccable` da `criar-site`):
  `anthropic-skills:canvas-design`, `marketing-skills:*` (Corey Haines),
  `ui-ux-pro-max`, Comfy Cloud MCP, `agent-browser`.

## Comportamento

Trigger: "criar post \<cliente\>" / "novo post \<cliente\>" / "criar carrossel
\<cliente\>".

Repo de design system do cliente: `D:\claude\posts\<cliente-normalizado>\`
- `design-system/` — tokens (3 cores, 2 fontes) + specs dos 2–3 templates de
  slide (headline / content zone / rodapé @handle) + `index.html` de preview
  importável no Claude Designer. `git init` local.
- `output/` — PNGs finais dos posts gerados.

Idempotente / dois modos (espelha `criar-cliente`):
- **Bootstrap** (primeiro post do cliente): define o design system → Checkpoint 1.
- **Reuso** (posts seguintes): carrega o design system existente, só produz o
  post novo. Não redecide o sistema.

### Etapas

0. **Pré-requisito + formato**: (a) pasta do cliente existe em `Clientes`
   (case-insensitive); se não, para e avisa para rodar `criar-cliente` (não
   auto-invoca). (b) Pergunta o formato: imagem única ou carrossel.
1. **Coleta**: lê de fato `00-Identidade-e-Tom` e `01-Referencias/Instagram`.
   Se insuficiente, pergunta ao usuário.
2. **Design system do post** (bootstrap; pulado se já existe): 3 cores + 2
   fontes; 2–3 templates reusáveis; autoridade `identidade-e-tom.md` do
   cliente + `references/principios-design.md` + `anthropic-skills:
   canvas-design`. Persiste o repo. **Checkpoint 1**.
3. **Conteúdo/copy**: arco hook → problema → explicação → solução → CTA nos
   slides. Skills `marketing-skills:social` (primária), `copywriting`,
   `marketing-psychology`, `copy-editing`, `content-strategy`. **Checkpoint 2**.
4. **Construção (render híbrido)**: `anthropic-skills:canvas-design` compõe cada
   slide (1080×1350 padrão; 1080×1080 opcional) → PNG; imagem via Comfy Cloud
   MCP guiada por `marketing-skills:image`, só fundo/ilustração — **com
   escolha e alternância de modelo por tipo de necessidade** (fundo abstrato/
   textura → `run_template`/`submit_workflow` OSS; foto realista →
   `partner_generate`; ilustração vetorial → `run_template` vocacionado;
   sempre confirmando o catálogo atual via `search_models`/
   `get_prompting_guide` antes de gerar, e trocando de modelo se o resultado
   não atender, em vez de fixar um único modelo para o post inteiro).
5. **Preview + QA**: `agent-browser` — legibilidade mobile, sem corte de texto,
   grid coerente. Corrige antes de apresentar.
6. **Entrega**: salva PNGs no Drive (`04-Carrosseis` e/ou
   `06-Aprovados-para-Postar`). Reporta. Sem publicar.

## Implementação

Skill é só instrução (`SKILL.md`), sem código externo. Usa diretamente:
- MCP do Google Drive (`search_files`, `read_file_content`,
  `download_file_content`; `create_file` para subir PNG) — leitura da identidade/
  referências e entrega. Nunca cria/renomeia/move pasta de cliente (isso é da
  `criar-cliente`).
- `anthropic-skills:canvas-design` — composição visual → PNG.
- `marketing-skills:*` (Corey Haines) — conteúdo/narrativa e guia de imagem.
- Comfy Cloud MCP (+ Gemini opcional) — imagem, com escolha/alternância de
  modelo por tipo de necessidade (ver Etapa 4).
- `agent-browser` — QA visual.
- `git` local — repo de design system do cliente.

## Aprendizados do dogfooding (aidealab, 2026-08-18)

- **`ui-ux-pro-max:banner-design` e `ui-ux-pro-max:design-system` não
  servem como consulta rápida de dado de design**, ao contrário do que o
  design original assumia. Testados na prática: ambos retornam instruções de
  um pipeline de produção completo e autônomo (scripts Python/Node, pesquisa
  de referência no Pinterest, geração de imagem via Gemini/`ai-multimodal`,
  export via `chrome-devtools`) — não uma resposta pontual. Esse toolchain
  diverge da arquitetura já aprovada desta skill (`canvas-design` + Comfy
  Cloud + `agent-browser`). Decisão: **removido** das ferramentas de Etapa 2;
  as decisões de cor/fonte/layout ficam com a skill mesmo, a partir da
  identidade real do cliente (`identidade-e-tom.md`) e de
  `references/principios-design.md`.
- A definição de design system funciona bem sem esses sub-skills quando o
  cliente já tem identidade real extraída (cores/fontes do próprio site via
  CSS, não estimativa) — caso da aidealab.
- Escolha de modelo de imagem no Comfy Cloud precisa ser uma decisão
  explícita por tipo de necessidade (fundo abstrato vs. foto realista vs.
  ilustração vetorial), não um modelo fixo — adicionado como lógica de
  decisão na Etapa 4.
- **Tipografia pode precisar de uma 3ª fonte** ("serifada de destaque") além
  do par Display+Body fixo — surgiu de uma referência real que o usuário
  trouxe ("best *font* pairings", @adarshxdesign): dupla sans+serif dramática
  na capa/CTA. Generalizado na diretriz de design como opcional, restrito a
  capa+CTA (nunca conteúdo, pra não competir por atenção).
- **Licença de fonte de referência**: a fonte que o usuário pediu inicialmente
  ("Tempting") era uma script comercial (RGB Studio, dafont/MyFonts) — grátis
  só para uso pessoal, precisaria de licença paga para uso comercial num
  cliente. Substituída por **Fraunces** (Google Fonts, licença livre,
  visualmente equivalente — serifada itálica bold dramática). Regra
  adicionada ao `SKILL.md`: checar licença antes de embutir fonte específica
  citada em referência de terceiro; preferir equivalente Google Fonts quando
  a licença não for clara para uso comercial.
- **Fontes embutidas via `@font-face` + `data:` URI (base64)**, não `<link>`
  para Google Fonts CDN — necessário porque tanto o Artifact quanto o preview
  local devem funcionar sem depender de rede em tempo de visualização (e o
  Artifact bloqueia CDN externo por CSP). Processo: buscar cada peso/família
  **separadamente** via `fonts.googleapis.com/css2` (uma request combinando
  múltiplos pesos pode retornar a mesma URL de arquivo para pesos diferentes
  — bug observado no proxy do Google Fonts, confirmado comparando hash MD5
  dos arquivos baixados), baixar o `.woff2`, converter para base64 com `awk`
  (não `python3`/`sed -i` com string grande — estouram limite de argumento;
  `awk` com `getline` de arquivo evita isso e preserva UTF-8 corretamente).
- **Artifact é a superfície de acompanhamento visual padrão desta skill, não
  o Claude Design** — testamos os dois; o usuário achou a interface do
  Claude Design mais lenta pro fluxo dele e preferiu iterar via Artifact
  direto na conversa. DesignSync fica como alternativa disponível, não
  proativa. Ver `SKILL.md`, Etapa 2 e "Ferramentas necessárias".

## Fora de escopo

- Publicar no Instagram (skill `post-instagram` futura).
- Compartilhar design system com `criar-site` (separado).
- Posts em vídeo / Reels (só imagem por ora).
- Criar/renomear/mover pastas de cliente no Drive (isso é da `criar-cliente`).
- Alterar `criar-site` (follow-up próprio).
