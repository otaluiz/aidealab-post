---
name: criar-flyer
description: Cria um flyer/criativo de imagem única (1080×1440) para um cliente da aidealab, com a assinatura de TEXTO ATRÁS DO SUJEITO — foto do banco do cliente, recorte por rembg no mesmo enquadramento e tipografia grande ocluída pela figura. Dois modos de origem de imagem (banco criativo-ref, ou geração Higgsfield com soul-ref) e um catálogo de 11 estilos gráficos que se alternam de peça pra peça. Dispara com "criar flyer <cliente>" / "criativo <cliente>" / "flyer de serviço <cliente>". Não publica no Instagram.
---

# Criar flyer

Cria um **criativo de imagem única** — anúncio de serviço, peça de campanha,
pôster de marca — em 1080×1440, com a assinatura visual que a aidealab validou:
**o tipo grande fica ATRÁS do sujeito recortado**.

É skill separada da `criar-post` de propósito. `criar-post` é carrossel:
narrativa multi-slide, dois checkpoints, arco de copy. Flyer é peça única, com
pipeline próprio (recorte + oclusão) e um catálogo de estilos gráficos como
eixo de variação. Uma responsabilidade por skill é a convenção do repo.

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

Sujeito pequeno (menos de ~180px de largura) não sustenta uma palavra inteira:
nesse caso o texto que vai atrás é um **numeral grande** (01/02/03), que é
cortado de verdade e ainda numera algo real na peça.

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

**Modo 2 — geração Higgsfield com `soul-ref` + personagem.**
Quando o banco não tem a cena. `soul_2` com as imagens de `soul-ref` como
referência e o personagem do cliente; depois o mesmo pipeline de recorte.
Custo: 0,12 crédito por geração. Se precisar de recorte com alpha nativo em vez
de rembg, `remove_background` = 1 crédito.

**Upscale só quando a origem for pequena.** `bytedance_image_upscale` tem preço
plano de **2 créditos** — mais caro que gerar do zero. Só entra quando a foto
vem abaixo de 1080×1440 (é o caso do banco `img-ref`, que é de thumbs de 736px,
não do `criativo-ref`).

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

Par fixo da marca: **Inter 900** (monumento) + **Tempting** (script). O cliente
rejeitou explicitamente Bodoni Moda. A família de apoio pode mudar conforme o
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

Salva os PNGs em `04-Carrosseis/<nome-da-serie>/` na pasta do cliente no Drive
(pasta local sincronizada). Reporta: estilo usado por peça, imagem de origem,
créditos gastos. **Não publica no Instagram.**
