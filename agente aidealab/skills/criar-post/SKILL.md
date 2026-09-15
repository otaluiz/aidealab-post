---
name: criar-post
description: Cria um post de Instagram (carrossel ou imagem única) on-brand para um cliente da aidealab, a partir da identidade e referências já organizadas no Drive pela criar-cliente. Segue um "post design system" de 3 estruturas (cor, tipografia, layout) e storytelling de copywriting (hook, problema, explicação, solução, CTA). Renderização híbrida — tipografia/layout como arte estática nítida via canvas-design, imagem via ComfyUI local (padrão, grátis) ou Higgsfield (fallback/foto realista/personagem). Dispara com "criar post <cliente>" / "novo post <cliente>" / "criar carrossel <cliente>". Para em dois checkpoints (design system, copy) antes de renderizar. Não publica no Instagram.
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
   (canvas-design + ComfyUI/Higgsfield + agent-browser) — não invocar esperando uma
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

## Onde o tipo grande entra — e onde não entra

**Caixa alta só no hook e no CTA.** Os slides de explicação não levam a palavra
grande de fundo: neles a cena fala sozinha e o content-card carrega a leitura.
Regra do cliente, depois de ver a série com palavra em todos os seis — o miolo
ficava barulhento e a espinha competia com o card.

Sem monumento, o recorte seria pixel idêntico à cena: **retira a camada
também**, em vez de deixá-la inerte.

**O personagem (@luizota / @wel) aparece só no hook OU só no CTA**, nunca no
miolo — é uma das variações de abertura, não o padrão da série. Os slides de
explicação levam cena com figura anônima e pequena, que é o registro do banco
`img-ref` e dos carrosséis aprovados.

**Toda peça tem imagem forte.** Fundo de gradiente sozinho no miolo foi
rejeitado — *"cadê as imagens que chamam atenção?"*. Gradiente é fundo de
apresentação; peça de feed pede cena.

**Numeral grande (`.numeral`) é a mesma peça que o monumento de palavra —
segue a regra idêntica, em QUALQUER slide, inclusive o de referência.**
`01`, `02`, `03` atrás do sujeito ou da moldura é o mesmo barulho que a
palavra gigante. GEO-Busca-com-IA e Estratégia-no-Marketing saíram com
numeral nos slides de explicação **e** no de referência — os três slides
voltaram pra correção. O slide de referência já tem "Passo 0X" escrito no
corpo do texto; não precisa do dígito gigante repetindo a mesma informação
por cima da cena.

**Moldura de referência: não force reposicionamento sem espaço livre real.**
Se a figura do slide de referência está confinada numa faixa estreita e o
topo da peça (regnum + assinatura) já ocupa a margem superior, mover a
moldura pra "abrir espaço" costuma esbarrar no cabeçalho antes de resolver o
problema. Prioridade: (1) mede se há espaço vertical livre de verdade acima
ou abaixo do sujeito respeitando as margens do cabeçalho e do rodapé; (2) se
houver, reposiciona a moldura; (3) se não houver, mantém a moldura na
posição padrão — não redimensiona nem recorta o conteúdo da moldura só pra
forçar caber.

### Onde o recorte é fraco, não se coloca tipo

Cabelo escuro contra fundo escuro derrota todos os modelos de recorte —
testados `u2net_human_seg`, `u2net`, `isnet-general-use` e alpha matting: o
topo do crânio some, a palavra passa por cima e o personagem fica **careca**.

A saída não é caçar um recorte melhor. É **ancorar a palavra onde a silhueta é
sólida** — no tronco, nunca na cabeça. Mede o perfil de largura por linha e
escolhe a faixa; o defeito do topo deixa de importar porque nada é desenhado
ali.

## Arquitetura de pastas do cliente (ler ANTES de gerar qualquer coisa)

Duas famílias de pasta, e elas NAO servem para a mesma coisa:

**`02-Materiais-Brutos` — entra direto na arte, custo zero.**

| pasta | o que e | como usar |
|---|---|---|
| `bg-ref` | gradientes e texturas abstratas | chao da peca, com moldura por cima |
| `img-ref` | cenas surreais prontas | imagem do miolo, uso direto |
| `hook-cta-ref` | personagens ja fotografados/gerados | hook e CTA, uso direto |

**`01-Referencias/Instagram` — nao entra na arte, e modelo para GERAR.**

| pasta | o que e | como usar |
|---|---|---|
| `hook-ref` | layout e design de capa | recriar o layout com o personagem |
| `soul-ref` | cena/pose de uma pessoa so | `soul_2` + `soul_id` + a referencia |
| `dupla-ref` | cena com duas pessoas | base para peca com os dois fundadores |

Consequencia pratica: **antes de gastar credito, olhe `02-Materiais-Brutos`.**
Um carrossel inteiro pode sair de la sem gerar nada. O cliente vai apagando da
pasta o que ja foi usado, entao o que estiver la e material livre -- e o que
sumiu ja saiu em peca e nao se repete.

## O sistema de carrossel: dois eixos

Sintese do que esta aprovado em `04-Carrosseis`. Sao **dois eixos independentes**:
o miolo (variacao de carrossel) e a capa (variacao de hook). Um carrossel escolhe
UMA de cada e combina livremente. Nao confunda os dois -- "ground de cor" e uma
capa, nao um sistema de miolo.

### Eixo 1 -- variacoes de carrossel (o miolo)

**1. Cartao de vidro sobre imagem** -- Branding, Consistencia, Design, Sites que
inspiram, Tarefas para a IA.
Fundo SEMPRE imagem (cena gerada ou textura do `bg-ref`); leitura num cartao
translucido com chip de etapa, titulo e uma linha em italico no acento. Aceita um
slide de referencia com print dentro de cartao claro.

**2. Cartao escuro sobre foto** -- Servicos (3), Estrategia, GEO, Jornada,
Parece Barato.
Foto sangrando na peca inteira, cartao escuro com blur no rodape. Palavra grande
atras do sujeito quando a silhueta e solida (mordida de 15-45% da largura).

**3. Moldura de papel** -- O Processo, O Que Postar.
Moldura creme com a foto dentro e etiqueta no rodape da moldura, cartao creme com
tipo escuro, sobre gradiente calmo da paleta -- o MESMO fundo em todos os slides.

### Eixo 2 -- variacoes de hook (so a capa)

**A. Ground de cor, sujeito na frente** -- Branding, Fontes, Consistencia, Design.
Chao de cor da familia, palavra TOM SOBRE TOM no lado claro (contraste medido,
2,8 a 3,2:1 -- escurecer contra ground escuro nao passa de 1,9:1 e some), sujeito
recortado NA FRENTE do tipo com a base dissolvida por `mask-image`, linha de apoio
em serifa script. Custo: 1 geracao + 1 recorte. O recorte funciona aqui porque o
sujeito esta na frente de tudo: erro de mascara some contra o ground liso.

**B. Cena gerada, sem personagem** -- Ferramenta vs Processo, GEO, Economia da
Atencao. Cena conceitual (objeto gigante, campo vazio, figura anonima pequena) com
a palavra por cima. De graca vindo de `img-ref`, ou 0,12 gerando.

**C. Personagem em foto sangrando** -- Servicos, Parece Barato, O Que Postar.
Foto do @luizota ou do @wel ocupando a peca, palavra atras dele quando a silhueta
e solida, embaixo do rosto quando nao e. `hook-cta-ref` de graca ou soul + `soul-ref`.

### Referencias: uma vez usada, nunca mais

Referencia da `soul-ref` / `dupla-ref` **se gasta**. Usou numa peca, nao usa de
novo -- senao a serie repete a mesma criacao com outro texto. Anote qual foi
usada em cada peca antes de subir a proxima.

**`dupla-ref` gera DUAS pessoas** mesmo com "alone" escrito no prompt: o soul
copia a composicao da referencia, e a segunda pessoa sai um desconhecido. Peca
de um personagem so exige referencia da `soul-ref`. Se ja gerou e veio a dupla,
da para salvar cortando so o fundador -- foi o que funcionou na capa do elevador.

### Nem todo carrossel precisa de personagem

Um bloco de tres pode ter um carrossel inteiro **so de cena cinematografica**,
sem rosto nenhum -- capa e CTA incluidos. Isso descansa o feed, sai mais barato
e ainda amarra pelo color grading.

### Color grading: so no prompt, NUNCA no pos

No prompt, fixo em toda geracao: *cold cinematic color grade, deep blue-black
shadows, desaturated cyan midtones, one warm amber rim light, soft haze, 35mm
film look* -- mais *anamorphic lens, fine film grain* quando o registro e
cinematografico. E aqui que a paleta se resolve.

**A curva de pos esta DESLIGADA** (decisao do cliente, 13/09/2026). A imagem
entra na peca nativa: so recorte 3:4, nada de curva de cor. "As imagens nao
precisam, manter aspecto da imagem."

Historico, para nao repetir o caminho: existiram duas curvas de pos e as duas
foram reprovadas. A primeira (sombra azul-petroleo + alta luz ambar, contraste
+6%, saturacao -6%) achatava foto que ja estava boa. A segunda, azul + fuchsia
neon por rampa de luminancia, foi pedida, testada em quatro origens e reprovada
na mesma sessao. Os dois scripts seguem em `carrossel-v3/grade.py` e
`carrossel-v3/grade2.py` **sem uso** -- nao reintroduza nenhum dos dois sem
pedido explicito.

Consequencia pratica: a harmonia da serie passa a depender inteiramente da
escolha das imagens. Antes de montar, ponha as 6 lado a lado num contact sheet;
se uma nao pertence a familia das outras, troque a imagem, nao a curva.

### Regras que nao mudam

- **Slide de explicacao NUNCA tem fundo de gradiente liso.** E imagem gerada,
  textura do `bg-ref` ou foto. Gradiente liso so como ground de capa.
- **Tres posts seguidos na mesma variacao de miolo** antes de trocar. Um carrossel
  isolado nao constroi identidade; o bloco de tres constroi.
- Quando o fundo vem do `bg-ref`, e o mesmo fundo em todos os slides.
- Uma variacao de miolo por carrossel. Moldura e para FOTO -- gradiente dentro de
  moldura nao vale.
- Caixa alta so na capa e no CTA. Personagem so na capa ou no CTA, nunca no miolo.

### Lettering: duas verificacoes obrigatorias

**1. Script x palavra grande nao podem se tocar.** Tempting tem descida longa e
com laco; Inter 900 com `line-height: .84` deixa o acento subir ALEM da caixa do
texto. As duas tintas vazam para fora das suas caixas e se encontram -- foi o
que sujou "Mesmo com Instagram, / INVISIVEL" e "Bora ficar / VISIVEL".

Vao fixo nao resolve, porque cada palavra tem altura de tinta diferente (com
acento ou sem, com descida ou sem). `carrossel-v3/anticolisao.js` mede a tinta
real pelo `actualBoundingBoxAscent/Descent` do canvas e sobe a linha script ate
limpar, com 16px de folga. Roda DEPOIS do fit de largura -- e o tamanho final da
palavra que decide onde o acento chega. Inline o arquivo num `<script>` antes do
FIT e chame `window.__anticolisao(16)` no fim dele.

**1b. O toque certo é leve: a script DEITA no topo do bold, não invade.**
Baseline colada no `capTop` da palavra (o que a cola de baseline faz sozinha)
joga toda a descida da Tempting DENTRO das letras e cobre a metade de cima
delas — foi o que o cliente recusou em ESTRATÉGIA, FERRAMENTA, PROCESSO, BUSCA
e RESPOSTA. A referência da casa é `Concorrente-Comunica-Melhor` e
`Testa-uma-DUPLA`: só a ponta da descida encosta no topo do bold, as letras
seguem legíveis inteiras.

Como acertar: `data-lift` no elemento `.script`, ~0,3em do corpo da script
(82px → 78; 88px → 74; 96px → 30 quando a palavra é curta e a descida cai fora
dela; 104px → 30). Não existe número único — renderize e confira o crop 1:1 da
faixa do lockup, nunca o contact sheet: a diferença some em miniatura.

**Palavra-chave serifada: colore UMA palavra, não a linha toda.** A linha
script fica em `--paper`; só a palavra que carrega o sentido entra em
`--accent`, via `<span class="kw">`. Linha inteira colorida foi recusada.

**2. Na oclusao, a palavra tem que ser ~1,5x mais larga que o sujeito.** Medido
na faixa vertical onde ela cai, lendo o alpha do recorte. Abaixo disso a palavra
some inteira atras da pessoa: "COMPLETO?" desapareceu com 840px de palavra
contra 859px de sujeito. Sujeito que preenche o quadro (cobertura acima de ~70%
em todas as faixas) nao serve para oclusao -- troque a imagem ou baixe a palavra
para a faixa mais estreita.

### Tipografia da casa: INTER + TEMPTING
Duas familias, so -- equivalente moderno de **Helvetica + Shelley**; se trocar,
troca em par.
- **Inter** -- display (900), titulo de cartao, corpo e rotulos. NUNCA serifada.
- **Tempting** -- a linha de apoio acima da palavra grande. UNICO lugar com serifa.

Nao entra terceira familia. Manrope aparece nos carrosseis antigos por inercia;
em peca nova, corpo e Inter.

## Referências do cliente: hook-ref e carousel-design

Duas pastas mandam no visual, e são lidas do disco antes de desenhar:

```
C:\Users\luizr\Meu Drive (aidealabbr@gmail.com)\Clientes\<cliente>\01-Referencias\Instagram\hook-ref
```
mais a irmã `carousel-design`. (`flyer-desing` serve à `criar-flyer`.)

**Recriar uma referência COM o personagem (a via mais fiel).** O `soul_2`
aceita `soul_id` **e** uma imagem de referência ao mesmo tempo (`medias`, role
`image`, máximo 1). Então dá para pegar um pôster da `hook-ref`, mandá-lo como
media e gerar a mesma composição com o rosto do @luizota ou do @wel — em vez de
só descrever a cena por escrito e torcer. Custo igual ao de qualquer `soul_2`:
0,12.

Fluxo: `media_upload` (devolve a `upload_url` presignada) → PUT dos bytes →
`media_confirm` → `generate_image` com `soul_id` + `medias`. Nesta máquina o
PUT precisa forçar IPv4: o `fetch` do Node e o `curl` estouram timeout no
endpoint da AWS, e `urllib` com `getaddrinfo` fixado em `AF_INET` passa.

**O `soul_2` carimba tipografia falsa.** Pedir cena "editorial" ou "advertising
photography" faz o modelo desenhar um título de pôster inventado — saíram
`GOARANG`, `MDYSUNOROR`, legendas laterais. Repetir "no text, no letters" no
prompt **não resolve**: ele já está lá e o carimbo veio assim mesmo.

O que resolve é enquadramento: o carimbo cai quase sempre numa faixa alta e
isolada, então **corta abaixo dele** no preparo (`crop` antes do cover) em vez
de regerar às cegas. Confere sempre o render antes de fechar — em miniatura o
texto falso passa despercebido.

**A referência tem que ser FOTO PURA, nunca pôster.** É a causa raiz do carimbo.
Mandar como media uma peça já diagramada (título, legenda lateral, código no
canto) faz o `soul_2` reproduzir a diagramação junto com a composição: saíram
`VIRLIZZAR A QULQWEE`, balões de conversa em língua nenhuma e um cabeçalho de
crédito inteiro. A referência que funcionou de primeira era o único arquivo da
pasta que é fotografia crua. Então, antes do `media_upload`: **corta a faixa de
tipografia do pôster** e manda só a fotografia. Três gerações queimadas (~0,36)
até isolar isso.

**REGRA DO CLIENTE: geração com referência JAMAIS pode sair com texto.** Vale
para qualquer letra — título de pôster, legenda, código no canto e também
**escrita à mão**. Uma referência de post-its com recadinhos manuscritos faz o
modelo escrever rabisco ilegível em cada bloquinho, e isso reprova a peça do
mesmo jeito que um título falso.

A correção é **na referência, não na saída**. Limpar a arte final é caro e
estraga o rosto (mediana forte achata pele e terno; máscara apertada limpa só
metade dos bloquinhos). Limpar a REFERÊNCIA é barato porque ali qualidade não
importa — ela só guia composição:

```python
note = (s > 55) & (v > 60)                       # papel saturado
note = close(note, 21) ; note = open(note, 5)    # engole a escrita
saida = onde(note, medianBlur(img, 21), img)     # bloquinho vira chapado
```

Sobe a referência limpa, gera de novo, e o modelo copia bloquinho em branco.
Custou 0,24 aprender: o par gerado com a referência escrita foi inteiro para o
lixo.

**Fundo sujo? Troca o fundo inteiro, não remenda.** Quando sobra rabisco ou
tipo falso na parede da cena, apagar mancha por mancha (`inpaint`) come tempo e
deixa borrão — e ainda foi por ali que o rosto do personagem quase virou
mingau. O movimento certo é usar a máscara do recorte como alpha e **repintar
todo o fundo** com uma parede sintética (gradiente + vinheta + ruído) no tom da
série. Um passo só, e ele resolve DUAS coisas: mata o texto falso e conserta a
paleta — a referência vinha de estúdio claro e os outros slides do carrossel
são escuros, o que quebrava a harmonia do carrossel.

Dois cuidados: endurecer a alpha (`clip((a-0.22)/0.20)`) antes de compor, senão
objeto de borda clara — um celular na mão — fica fantasma; e, onde a máscara
não é confiável, forçar alpha 1 numa faixa (`maximum(alpha, guard)`) para
preservar o trecho original da foto.

**Quando a cena é cheia, o tipo vai NA FRENTE.** A oclusão é a assinatura, mas
não é obrigação: se o sujeito ocupa mais de ~60% da largura em toda a altura
(caso do rosto embalado na bandeja), a palavra atrás sobra só nas pontas e vira
ruído. Aí o caminho é **lettering aplicado por cima** — fill, contorno de tinta
e duas sombras duras deslocadas, a de cor antes da de tinta. Lê como rótulo
impresso e combina com cena de embalagem e vitrine.

**O que `hook-ref` ensina.** As capas ali NÃO são retrato de estúdio: são
**cena conceitual — a pessoa dentro de uma metáfora exagerada**. Alguém coberto
de post-its, cercado de celulares que mostram o próprio rosto, com o rosto
embalado numa bandeja de supermercado, num escritório com papéis voando. Por
cima, uma pergunta curta em duas alturas (linha pequena + palavra gigante
colorida) e uma trilha de rótulos no topo.

Então o hook se gera assim: **descreve a cena-metáfora, não a pose**. "Homem em
pé enquanto dezenas de panfletos voam ao redor" rende capa; "homem de braços
cruzados com luz de recorte" rende banco de imagem.

**O CTA nao precisa repetir sempre a mesma receita.** Script + monumento +
chip e UMA das formas, nao a forma. Regra do cliente: variar. Tres que ja
funcionaram:

- **tipo no chao** — o tipo desce para a faixa vazia embaixo do sujeito e o chip
  fecha (cena de imprensa fotografando o @wel sentado);
- **fechar o arco da capa** — o CTA usa OUTRO angulo da mesma serie de fotos do
  hook, mostrando o depois (na capa os dois estao cobertos de post-it; no CTA
  estao arrancando os bloquinhos);
- **monumento atras do sujeito**, que e o padrao antigo.

O que nao muda: chip de acao visivel, uma linha de tipo grande no maximo, e
caixa alta permitida (hook e CTA sao os dois unicos lugares).

**Dois fundadores na mesma capa.** Um `soul_id` por geração, então os dois nunca
saem juntos. A receita que funcionou:

1. gera **cada um no MESMO enquadramento** — mesmo prompt, mesma pose, fundo
   neutro, luz chapada ("de braços cruzados, fundo claro liso, luz suave, da
   cintura para cima"). Enquadramento igual é o que faz os dois parecerem da
   mesma foto;
2. gera o **fundo à parte**, sem personagem e sem texto (aqui: parede coberta de
   post-its em branco — a metáfora da `hook-ref` virou cenário em vez de pose);
3. recorta os dois com a máscara dupla, aplica a MESMA escala aos dois (não
   iguala a altura: quem é mais alto continua mais alto) e assenta no rodapé do
   quadro;
4. escurece os recortes ~12% e joga uma **sombra projetada borrada** atrás de
   cada um — sem isso os dois flutuam sobre a parede;
5. corta a faixa inferior da foto de origem antes de recortar: legenda falsa no
   pé da geração entra no recorte junto com o corpo.

Com os dois ocupando a metade de baixo não sobra faixa de mordida (a cobertura
passa de 80%), então o tipo aqui vai **na frente, acima das cabeças**.

## Etapa 3 — Conteúdo e copy

**A espinha de palavras.** Antes de escrever os cards, escolhe UMA palavra por
slide — a que vai atrás do sujeito. Lidas em sequência elas têm que formar a
narrativa do carrossel sozinhas, porque é isso que o leitor pega ao arrastar
rápido: `SOME · VISITA · VOLTA · DECIDE · CAMINHO`. Se a sequência não conta a
história sem os cards, a copy ainda não está pronta.

**Nunca use numeral 01/02/03 como o tipo grande.** Regra do cliente: os dots do
rodapé já numeram o slide, então o numeral gasta o lugar mais nobre da peça
repetindo o que o rodapé diz. Vale também para o chip do card — rótulo verbal
("A primeira vez", "O retorno", "A decisão"), nunca "Etapa 01".

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
   gera via **ComfyUI local ou Higgsfield**, guiada pela skill
   `marketing-skills:image` (prompt e otimização). A imagem entra na
   composição do `canvas-design` — nunca carrega o texto.

   **Escolha de motor — ComfyUI local × Higgsfield.**
   - **ComfyUI local (Desktop, MCP `comfyui`)** — zero custo, primeira escolha
     sempre. Checa com `get_system_stats` se o app **ComfyUI Desktop** está
     aberto; sem resposta, não sobe o app sozinho — avisa o usuário e cai pro
     Higgsfield. Confere `list_local_models` para saber o que está baixado
     antes de montar o workflow (`generate_image`/`enqueue_workflow`) — não
     assume nome de modelo fixo de execuções anteriores. Bom pra fundo
     abstrato/textura/glow e ilustração; mais lento numa GPU modesta, sem
     custo por imagem. Imagem sai em
     `D:\ComfyUI-Outputs\aidealab\<cliente>\` antes de entrar na composição —
     mesma função do `output/` do repo pras demais camadas, só que fora do
     versionamento (arquivo binário grande).
   - **Higgsfield** — quando o Desktop não está aberto, quando a peça precisa
     de foto realista com fidelidade que os modelos locais não cobrem, ou do
     personagem da casa (Soul treinado); mesma regra de custo e alternância
     de `criar-flyer` (ver aquela skill).
   - Se o resultado não atender (texto ilegível aparecendo na imagem, cor
     fora da paleta do cliente, artefato visual, composição errada) —
     **troca de modelo local antes de trocar de motor**; só sobe pro
     Higgsfield se o local não resolver ou não estiver disponível. Não
     insiste indefinidamente no mesmo modelo nem aceita resultado abaixo do
     padrão.

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
     Abaixo de 1080×1440, amplia **localmente e de graça** com Lanczos 2× +
     unsharp (Pillow). **Não gasta crédito com `upscale_image`** — regra
     fechada pelo cliente; ver a receita e o porquê na skill `criar-flyer`.
     Ampliar antes de recortar ainda melhora o `rembg`: mais pixel na borda,
     alpha menos serrilhado.
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
   `image_background_remover` = **1 crédito**. O upscale
   (`bytedance_image_upscale`, **2 créditos**, preço plano) está **fora do
   pipeline** — ampliação é local e grátis. Por peça:

   | Template | Operações | Crédito/peça | Par hook+CTA |
   |---|---|---|---|
   | A · Foto plena (já em 1080×1440) | nenhuma | 0 | 0 |
   | B · Ground + sujeito | 1 geração + 1 recorte | 1,12 | 2,24 |
   | C · Cenário + sujeito | 1 geração + 1 recorte | 1,12 | 2,24 |
   | D · Banco `img-ref` + Lanczos local | nenhuma paga | 0 | 0 |

   Três pontos contra a intuição, os três medidos e não estimados:
   - **B e C custam exatamente o mesmo.** A diferença entre os dois é só
     composição CSS (ground chapado vs. cena inteira atrás), não geração.
     Escolhe pelo resultado visual, nunca por orçamento.
   - **D é o template mais barato, não o mais caro.** Isso mudou: enquanto o
     upscale era pago, thumb de 736px custava 2 créditos e reaproveitar o
     banco saía mais caro que gerar do zero. Com Lanczos local o banco voltou
     a custar zero. Validado no carrossel GEO, feito inteiro de thumbs de
     736px e aprovado sem ressalva.
   - **Se um dia precisar mesmo de detalhe reconstruído, gera — não amplia.**
     0,12 de uma `soul_2` nova contra 2,00 de upscale: gerar do zero é 16×
     mais barato que ampliar.

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
postar). Junto, **todo post fecha com um `metadata.json` na própria pasta** —
é ele que a `post-instagram` futura vai ler, e sem ele o carrossel não passa de
uma pasta de imagens.

### `metadata.json` — o que tem que estar lá

```json
{
  "carousel_id": "<nome-da-pasta>",
  "cliente": "aidealab",
  "data_criacao": "AAAA-MM-DD",
  "status": "aprovado",
  "postado": false,
  "tema": "<uma linha>",
  "pilar": "educacional | oferta | bastidor | prova",
  "familia_cor": "azul | roxo | amber",
  "template": "<papéis dos slides em sequência>",
  "formato": "1080x1440",
  "geracao_imagem": "<engine, referência e custo em créditos>",
  "slides": [
    { "ordem": 1, "arquivo": "01_....png", "papel": "hook",
      "layout": "<variação de miolo/capa usada>",
      "texto": "<o que está escrito no slide>",
      "alt": "<descrição da imagem para leitor de tela>" }
  ],
  "legenda": "...",
  "primeiro_comentario": "...",
  "hashtags": ["#..."],
  "handle": "@aidealab7",
  "cta": { "tipo": "direct | salvar | palavra-chave",
           "palavra_chave": "PROMPT", "texto": "digite PROMPT na DM" },
  "publicacao": { "rede": "instagram", "formato": "carrossel",
                  "proporcao": "4:5", "slides_total": 6,
                  "ordem_arquivos": ["01_....png", "..."] }
}
```

Três campos existem por motivo prático e costumam ser esquecidos:

- **`alt`** por slide. Instagram aceita texto alternativo e quase ninguém
  preenche. Descreva a cena, não o conceito.
- **`ordem_arquivos`**. O upload automático publica na ordem que recebe; nome de
  arquivo com prefixo numérico (`01_`, `02_`) é o que garante a sequência.
- **`cta.palavra_chave`**. Uma palavra, sem acento e sem espaço. É ela que a
  automação de DM escuta, e acento quebra o filtro.

**Confira antes de fechar**: `ordem_arquivos` bate com os PNGs que existem na
pasta, e cada `slides[].arquivo` existe de fato. Metadado que aponta para
arquivo renomeado publica o carrossel fora de ordem.

### A legenda

Escrita com `humanizer` + `marketing-skills:copywriting` + `marketing-skills:social`.
O que isso significa na prática, para este cliente:

- **Primeira linha carrega o post sozinha.** É o único pedaço visível antes do
  "mais" e vale mais que o resto da legenda junto.
- **Sem travessão.** A casa usa vírgula, ponto e parênteses. Travessão em série
  é o tique de texto de robô mais fácil de reconhecer.
- **Sem "não é X, é Y"**, sem tríade decorativa, sem frase de efeito sozinha
  num parágrafo para dar peso.
- **CTA diferente em cada post.** Fechar todos com a mesma frase ("salva esse
  post e segue @aidealab7") transforma o perfil num carimbo. O convite muda com
  o assunto.
- **`primeiro_comentario` é pergunta ou link**, nunca repetição da legenda: é
  ele que abre conversa e tira link do corpo do post. Se o MCP do Drive conectado não
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
- MCP `comfyui` (ComfyUI Desktop local — `get_system_stats`,
  `list_local_models`, `generate_image`, `enqueue_workflow`, `get_history`,
  `get_image`) — geração local sem custo, requer o app **ComfyUI Desktop
  aberto**; motor padrão da camada de imagem (Etapa 4).
- Higgsfield (`generate_image`, `show_characters`) — fallback quando o
  Desktop local não está aberto, quando a peça precisa de foto realista com
  fidelidade que os modelos locais não cobrem, ou do personagem da casa
  (Soul treinado) (Etapa 4).
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
