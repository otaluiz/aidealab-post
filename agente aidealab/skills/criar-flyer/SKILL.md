---
name: criar-flyer
description: Cria um flyer/criativo de imagem única (1080×1440) para um cliente da aidealab, com a assinatura de TEXTO ATRÁS DO SUJEITO — foto do banco do cliente, recorte por rembg no mesmo enquadramento e tipografia grande ocluída pela figura. Três modos de origem de imagem (banco criativo-ref; geração Higgsfield com soul-ref; ou geração ComfyUI local sem custo) e um catálogo de 11 estilos gráficos que se alternam de peça pra peça. Dispara com "criar flyer <cliente>" / "criativo <cliente>" / "flyer de serviço <cliente>". Não publica no Instagram.
---

# Criar flyer

Cria um **criativo de imagem única** — anúncio de serviço, peça de campanha,
pôster de marca — em 1080×1440, com a assinatura visual que a aidealab validou:
**o tipo grande fica ATRÁS do sujeito recortado**.

É skill separada da `criar-post` de propósito. `criar-post` é carrossel:
narrativa multi-slide, dois checkpoints, arco de copy. Flyer é peça única, com
pipeline próprio (recorte + oclusão) e um catálogo de estilos gráficos como
eixo de variação. Uma responsabilidade por skill é a convenção do repo.

## Etapa 0 — a pasta de referências manda no design

**Antes de desenhar qualquer coisa, lê a pasta de referências do cliente.** É
lá que ele deposita os pôsteres que quer ver recriados:

```
C:\Users\luizr\Meu Drive (aidealabbr@gmail.com)\Clientes\<cliente>\01-Referencias\Instagram\flyer-desing
```

O nome da pasta tem um typo herdado (`flyer-desing`, não `flyer-design`) —
usa como está, não renomeia a pasta do cliente. A irmã `carousel-design` serve
à `criar-post`. Lê do disco, nunca pelo MCP do Drive.

**Como usar uma referência.** Não é para copiar: é para extrair a *gramática*
e reescrever com a marca. Antes de montar, escreve para si mesmo duas listas —
o que vem da referência (grade, camadas, ornamento, ritmo tipográfico, gesto de
colagem) e o que é inegociável da casa (1080×1440, Inter + Manrope, paleta,
rodapé `@aidealab7` + `aidealab.com.br`, grão, e a oclusão). Se a referência
tiver a cor de outra marca, traduz para o parente mais próximo dentro da
paleta — foi assim que o vermelho do pôster Project 34 virou Magenta.

Referência nova na pasta = peça nova. Se houver mais de uma, pergunta qual,
ou faz a mais recente e diz qual escolheu.

## Personagens da casa

O cliente pode pedir que a peça seja estrelada por uma pessoa real da agência —
ou não pedir, e aí a escolha é tua conforme a cena.

| Apelido | Soul | `soul_id` |
|---|---|---|
| **@luizota** | "Luiz ota" (`soul_2`, ready) | `f752ac25-65a0-4930-a628-722af0508c5b` |
| **@wel** | ainda **não treinado** | — |

Confere sempre com `show_characters(action='list')` antes de usar: um Soul pode
ter sido treinado ou removido desde a última peça. **Se o cliente pedir @wel,
para e avisa que falta treinar** (5–20 fotos, ~10 min) em vez de improvisar
outra pessoa — o rosto errado numa peça de marca é pior que peça atrasada.

Detalhes de geração com Soul estão no **Modo 3** dos modos de origem.

## A assinatura: texto atrás do sujeito

Duas camadas de imagem, **a mesma foto no mesmo enquadramento**:

```
.scene   { position:absolute; inset:0; object-fit:cover; z-index:0; }  /* foto inteira */
.mon     {                                               z-index:3; }  /* tipo grande */
.subject { position:absolute; inset:0; object-fit:cover; z-index:5; }  /* recorte da MESMA foto */
```

Como as duas são o mesmo arquivo com o mesmo `object-fit: cover`, o recorte cai
**exatamente sobre si mesmo**. Não há reposicionamento manual, não há borda de
adesivo e **não se aplica a máscara de dissolução da base** do template B da
`criar-post`: a base do recorte encosta na própria cena de origem, então não
existe corte reto contra fundo estranho. Aplicar a máscara por hábito duplica o
sujeito como um fantasma.

**Ordem de camadas — errar isso lava a arte inteira.** Já aconteceu duas vezes:
- `scrim` **abaixo** do tipo (z1 ou z2), nunca acima. Scrim em z6 escurece o
  monumento e o recorte junto, e a peça sai cinza e sem contraste.
- **script (Tempting) fica NA FRENTE do sujeito (z6)**, só o monumento vai
  atrás. Com a script atrás, a cabeça do sujeito come metade da palavra.
- Texto de leitura obrigatória (chip, card, moldura, rodapé) sempre em z10+.

## Escolha da faixa de mordida — medida, nunca no olho

Antes de posicionar o tipo, **mede o perfil de cobertura do alpha por linha**:

```python
a = np.array(Image.open(cut).convert('RGBA').getchannel('A')) > 10
for y0 in range(100, 1300, 100):
    cobertura = a[y0:y0+150].any(axis=0).mean()   # fração da largura ocupada
```

Escolhe a faixa onde o sujeito cobre **~20–45% da largura**. Abaixo disso ele
só arranha a palavra; acima, engole. Depois ancora o monumento pela **BASE**
(`data-bottom`) nessa altura — nunca por `top` fixo.

**O texto atrás do sujeito é SEMPRE uma palavra — nunca um numeral 01/02/03.**
Regra do cliente. Os dots do rodapé já dizem em que slide o leitor está, então
o numeral gigante só repete essa informação ocupando o lugar de nobre da peça.
Uma palavra por slide (SOME · VISITA · VOLTA · DECIDE · CAMINHO) faz a série
inteira ser lida como uma frase enquanto o leitor arrasta — coisa que 01/02/03
não faz. Pela mesma razão, o chip do card leva rótulo verbal ("A primeira vez",
"O retorno"), não "Etapa 01".

Sujeito pequeno (menos de ~180px de largura) não engole uma palavra inteira —
ele a **arranha**, e isso basta. Nesse caso escolhe uma palavra curta e larga
(4–6 letras com `data-fit` alto), pra que a mordida caia numa letra inteira em
vez de raspar o vão entre duas.

## Ajuste do corpo: largura-alvo, e só depois de `document.fonts.ready`

Fixar `font-size` na mão estoura o quadro assim que a copy muda de tamanho —
aconteceu com AUTOMAÇÃO/DESTAQUE/MARCA na primeira leva. O corpo é calculado
por largura-alvo, medindo o `<span>` interno (o bloco é full-width e o laço
encolheria a palavra até zero).

**O ajuste inteiro roda dentro de `document.fonts.ready.then(...)`.** Com fonte
vinda da rede (`@import` do Google Fonts), medir antes do swap mede a
*fallback*: o corpo calculado fica grande demais e a palavra estoura. Foi
exatamente o que aconteceu com CRIAÇÃO em Archivo Black.

```js
document.fonts.ready.then(function () {
  // 1. corpo pela largura-alvo (mede o .mw, não o bloco)
  // 2. ancora pela base:  el.style.top = data-bottom - alturaDoBloco
  // 3. cola a script: baseline dela no topo das caixas altas do monumento,
  //    com capHeight sondado em "H" (nunca na palavra inteira — til e cedilha
  //    inflam a medida)
});
```

## Colisão de diacrítico com a script

O acento agudo fica ACIMA da altura de caixa alta, que é justamente onde a
baseline da script pousa. Quando um traço pesado da script cai bem em cima do
acento, ele some — "SUA ESTRATÉGIA" virou "SUA ESTRATEGIA" porque o `t` de
"montar" pousou sobre o agudo do É.

Não é bug sistêmico, é colisão de par específico. Conferir sempre no render, e
resolver trocando a copy. **Cedilha é segura**: desce abaixo da linha de base e
nunca cruza a script.

## Modos de origem da imagem

**Modo 1 — banco `criativo-ref` do cliente (padrão, custo zero).**
Pasta local sincronizada pelo Google Drive desktop — lê direto do disco, não
pelo MCP do Drive (baixar por MCP devolve base64 no resultado da ferramenta e
queima contexto à toa):
`C:\Users\luizr\Meu Drive (aidealabbr@gmail.com)\Clientes\<cliente>\02-Materiais-Brutos\criativo-ref`

- As imagens dessa pasta já vêm em 3:4 e ≥1080px — **não precisam de upscale**.
- Recorte com `rembg` local (`new_session('u2net')`), grátis.
- **Nunca reusa a mesma imagem** entre peças. Antes de escolher, confere quais
  já foram publicadas.
- **Monta um contact sheet** (grade de miniaturas num único JPEG) pra escolher —
  uma leitura em vez de dezoito.

**Modo 3 — o personagem da casa (@luizota), via Soul treinado.**
Já existe um Soul V2 pronto na conta: nome **"Luiz ota"**,
`soul_id: f752ac25-65a0-4930-a628-722af0508c5b`. Confirma com
`show_characters(action='list', status='ready')` antes de usar — não treina um
novo. Gera com `model: 'soul_2'` + esse `soul_id`; custo igual ao de qualquer
`soul_2` (0,12).

Duas armadilhas medidas em produção:
- **Um `soul_id` por geração.** Cena com duas pessoas identificadas exige
  `show_reference_elements`. Mas quando a segunda figura é anônima (de costas,
  sem rosto, cabeça substituída por objeto), o `soul_2` resolve a cena inteira
  numa geração só — foi assim que saiu o flyer do quebra-cabeça.
- **Descreve o objeto pela geometria, não pela categoria.** Dois erros na
  mesma peça: "as if turning an invisible cube" devolveu uma placa de vidro
  literal, e "puzzle cube" devolveu um quebra-cabeça de peças de encaixe. O que
  funcionou foi soletrar a forma — *"a 3x3 twisty cube with nine flat square
  colour tiles per face, crisp straight edges"*. Nome de categoria o modelo
  interpreta; geometria ele desenha.

Peça em que ele aparece: *Você não precisa quebrar a cabeça* — ele em pé atrás,
girando o cubo que é a cabeça da figura sentada.

**Modo 2 — geração Higgsfield com `soul-ref` + personagem.**
Quando o banco não tem a cena. `soul_2` com as imagens de `soul-ref` como
referência e o personagem do cliente; depois o mesmo pipeline de recorte.
Custo: 0,12 crédito por geração. Se precisar de recorte com alpha nativo em vez
de rembg, `remove_background` = 1 crédito.

**Modo 2b — geração ComfyUI local, sem custo.** Alternativa ao Modo 2 quando
o **ComfyUI Desktop está aberto** (checa com `get_system_stats` no MCP
`comfyui`; sem resposta, não sobe o app sozinho — avisa o usuário e cai pro
Modo 2). Não serve para o personagem da casa (Soul treinado é exclusivo
Higgsfield) — só para cena/fundo/sujeito genérico sem `soul-ref`. Gera via
`generate_image`/`enqueue_workflow` com os modelos já baixados localmente
(`list_local_models`); salva o bruto em
`D:\ComfyUI-Outputs\aidealab\<cliente>\` antes do mesmo pipeline de recorte
(`rembg`) e upscale local. Escolha entre 2 e 2b: 2b primeiro quando o app já
está de pé e a cena não exige o personagem treinado; senão Modo 2.

### Upscale: sempre local, sempre grátis

**Nunca gaste crédito com upscale.** Regra fechada pelo cliente depois do
carrossel GEO, que saiu inteiro de thumbs de 736px ampliadas localmente e foi
aprovado sem ressalva. `bytedance_image_upscale` não entra mais no pipeline.

**Quando ampliar:** só se a origem for menor que 1080×1440. O `criativo-ref` já
vem em 1536×2048 ou 1080×1440 e nunca precisa. O `img-ref` é banco de thumbs de
736px e sempre precisa.

**Como ampliar:** Lanczos 2× + unsharp, Pillow puro, zero crédito.

```python
up = im.resize((w * 2, h * 2), Image.LANCZOS)
up = up.filter(ImageFilter.UnsharpMask(radius=1.4, percent=68, threshold=2))
up = ImageEnhance.Contrast(up).enhance(1.03)
```

**Por que basta.** Lanczos não inventa detalhe, mas nesta assinatura ninguém
olha o poro da pele: a foto entra como *cena*, leva scrim por cima, grão por
cima e o monumento na frente. O que precisa estar nítido é o tipo, e o tipo é
vetor. Um upscale generativo pagaria por detalhe que o scrim apaga.

Ampliar antes de recortar também melhora o `rembg`: mais pixel na borda, alpha
menos serrilhado.

**O corolário de custo.** Se um dia uma peça realmente exigir detalhe
reconstruído, o caminho não é upscale — `bytedance_image_upscale` tem preço
plano de 2 créditos, contra 0,12 de uma geração `soul_2` nova. **Gerar do zero
é 16× mais barato que ampliar.** Não há ESRGAN nem opencv nesta máquina.

## Os 11 estilos gráficos como eixo de variação

A marca não muda de peça pra peça — muda a **gramática do estilo**. O catálogo
vem do guia da Looka e está desenhado nos artboards da série "Estilos
Gráficos": Modernismo, Bauhaus, Minimalismo, Art Déco, Pop Art, Estilo Suíço,
Psicodélico, Pós-modernismo, Brutalismo, Flat, Contemporâneo.

O que o estilo governa: **grade, cor, ornamento e a família de apoio**.
O que o estilo NÃO governa: formato 1080×1440, a assinatura de oclusão, o
rodapé `@aidealab7` + `aidealab.com.br`, e o grão.

Validados em produção:
- **Estilo Suíço** — grade de 6 colunas visível, tudo alinhado à esquerda, uma
  família só (Inter), réguas grossas em cima e embaixo, zero ornamento, serviços
  numa fileira de 3 colunas com filete.
- **Pop Art** — retícula de meio-tom sobre a cena (`radial-gradient` 13px),
  blocos de cor chapada, Archivo Black, e a palavra repetida 3× em fantasma
  (serigrafia) com só a da frente sólida.
- **Brutalismo** — monocromático com um estouro magenta, Space Mono nos rótulos,
  bordas de 4px, zero raio e zero sombra, estrutura exposta.

**Alterna o estilo a cada peça** — nunca dois flyers seguidos no mesmo estilo.

## Tipografia

Par fixo da marca: **Inter 900** (monumento) + **Tempting** (script).

**Nada de serifada.** O cliente rejeitou explicitamente Bodoni Moda e, depois,
Playfair Display — a instrução foi *"fontes modernas e profissionais, não
serifadas"*. O par de leitura é **Inter** (display, rótulos, chips) +
**Manrope** (corpo). Serifada não entra nem em texto pequeno nem em itálico de
apoio, que é onde ela costuma se infiltrar sem ninguém decidir. A família de apoio pode mudar conforme o
estilo (Archivo Black no Pop Art, Space Mono no Brutalismo), mas o monumento
continua Inter 900.

**Tempting não tem nenhum glifo acentuado** — cobre A-Z, a-z e 0-9 e mais nada
(verificado lendo o `cmap` da fonte). A palavra-script é sempre caixa mista e
**sem acento**; quem carrega acento é o monumento, em Inter. String acentuada
não dá erro: cai silenciosamente na fallback e quebra o lockup sem avisar.

## Render e QA

Render por **CDP com métricas explícitas** (`Emulation.setDeviceMetricsOverride`
+ `Page.captureScreenshot` com `clip`), nunca `--window-size` — essa dimensiona
a janela, não a viewport, e o shot sai com faixa morta.

Gate de pixel antes de entregar: o PNG tem que ser exatamente 1080×1440 e a
**coluna uniforme na borda direita tem que ser 0px** — faixa uniforme ali é a
assinatura do render cortado.

Depois do gate, **olha a peça**. O gate prova dimensão, não composição: palavra
estourando o quadro, acento comido pela script e sujeito engolindo a palavra
passam pelo gate inteiros.

## Entrega

Salva os PNGs em **`07-Flyer/`** na pasta do cliente no Drive (pasta local
sincronizada). Flyer NÃO vai em `04-Carrosseis` — essa é da `criar-post`, e
misturar peça única com série de carrossel bagunça a revisão do cliente. Reporta: estilo usado por peça, imagem de origem,
créditos gastos. **Não publica no Instagram.**
