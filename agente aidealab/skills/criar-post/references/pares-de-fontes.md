# Pares de fontes validados — referência da `criar-post`

Conhecimento reusável para **qualquer cliente** (não é decisão de marca de
nenhum cliente específico). Curado de 3 bibliotecas de combinação de fontes
reconhecidas — consultar aqui antes de inventar um par do zero, na Etapa 2
(design system) quando a referência do cliente pedir um tratamento com 3
fontes (display + serifada de destaque, ver `principios-design.md`).

Fontes da pesquisa:
- [Figma — combinações de fontes](https://www.figma.com/pt-br/resource-library/combinacoes-de-fontes/) (39 pares)
- [fontpair.co](https://fontpair.co/)
- [Monotype — font pairing](https://www.monotype.com/font-pairing#/explore) (não retornou dados via fetch — é SPA; consultar manualmente se precisar)

## Pares fortes para dupla display+serifada dramática (capa/CTA editorial)

Selecionados por terem peso/itálico disponível no Google Fonts e lerem bem
em tamanho grande sobre imagem — o caso de uso mais comum da `criar-post`:

| Display | Serifada de destaque | Por que funciona |
|---|---|---|
| **Inter** | **Playfair Display** (itálica, peso 900) | Sans neutro deixa a serifada ser a "personalidade"; Didone dramático com traço mais legível que Bodoni em itálica grande. **Usado na aidealab.** |
| Epilogue | Baskervville | Sans moderno + serifada tradicional, registro editorial |
| Source Sans Pro | Alegreya | Sans limpo + serifada caligráfica, tom literário |
| Metal | EB Garamond | Display dramático + serifada clássica |
| Raleway | Merriweather | Sans elegante + serifada clássica, tom profissional |

## Pares fortes para display+body (sem serifada de destaque)

Quando a referência do cliente NÃO pede o efeito de dupla sans+serif — só
display + body, o padrão de 2 fontes:

| Display | Body | Registro |
|---|---|---|
| Montserrat | Karla | Corporativo contemporâneo |
| Oswald | Source Serif 4 | Sans condensada + serifada — títulos com autoridade |
| Instrument Sans | Geist | Duas sans modernas, contraste sutil — tech UI |
| Syne | Inter | Sans expansiva/bold + sans simplificada — tech/design moderno |
| Nunito | Lora | Formas arredondadas + serifada elegante — acessível |

## Regra de escolha

1. **Sempre checar licença** antes de usar um nome de fonte específico citado
   numa referência de terceiro (ex: Instagram) — preferir os pares acima
   (Google Fonts, licença livre) a menos que o cliente confirme ter licença
   comercial de algo diferente. Ver nota em `principios-design.md`.
2. Preferir um par onde **um lado é neutro/quieto e o outro tem
   personalidade** — dois rostos "characterful" ao mesmo tempo tendem a brigar
   em vez de complementar.
3. Testar peso e itálico grande de verdade (não só o nome da fonte) antes de
   aprovar — o mesmo par pode ler bem numa referência estática e mal quando
   renderizado em itálica 900 sobre uma foto de fundo real. Foi o caso da
   Bodoni Moda: nome forte, mas o traço fino da itálica em peso alto não
   segurou bem sobre imagem — trocada por Playfair Display no mesmo papel.
