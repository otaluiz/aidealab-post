# Personagens com referências criativas (@luizota e @wel)

Como gerar capa e CTA com os personagens da casa no motor (`motor/`). Aprovado pelo cliente em 08/10/2026
(carrosséis audio-longo-vira-texto, pedir-avaliacao-sem-vergonha, legenda-que-aparece-na-busca,
para-quem-e-a-aidealab, orcamento-em-5-minutos).

## Personagens

| Handle | soul_id | Descrição obrigatória no prompt |
|---|---|---|
| @luizota | `f752ac25-65a0-4930-a628-722af0508c5b` | `a young man with short dark textured hair` |
| @wel | `68f715ee-167c-4c8f-92eb-16bbd177f7d3` | `a young man with dark curly hair and a beard` |

Sempre `generate_image` com `model: soul_2`, `soul_id`, `aspect_ratio: 3:4`, `quality: 2k`. Alternar quem faz capa e
CTA entre carrosséis (campo `personagem` do `png/metadata.json`).

## Regras de direção

1. **Nunca sorrindo.** Expressão séria, intensa, cansada, decidida. Todo prompt leva `mouth closed, not smiling`.
2. **Pose editorial de moda**, nunca retrato de banco de imagem. Fonte: Drive
   `Clientes/aidealab/01-Referencias/Instagram/soul-ref` (fotos de moda masculina: câmera baixa, poses fora do eixo,
   cadeira/cubo/banquinho em estúdio, céu e concreto).
3. **Descreva a referência, não mande a foto.** Com a foto em `medias`, o `soul_2` copia roupa, óculos escuros,
   bandana, correntes, peito nu e paleta da referência, mesmo com o prompt proibindo (testado: 6 de 7 saíram assim).
   A exceção que funcionou foi uma referência sem acessórios (bloco de concreto contra o céu).
4. **Espaço para o título:** `the figure in the lower half of the frame, his head at the vertical middle of the
   picture, a large empty backdrop/sky fills the upper half`. Personagem grande com cabeça no topo não deixa o
   título entrar atrás dele.
5. **Paleta da marca:** `deep navy and cyan color grading`, estúdio `seamless deep navy backdrop` com `cyan rim light`.
6. **Sempre no fim:** `No text, no letters, no logos, no glasses, no hat, no jewelry`.
7. Reprovar e refazer se: sorrindo, óculos/acessório, sem camisa, moldura/borda preta, texto ou logo na roupa,
   rosto escondido. Uma referência de composição se gasta: não repetir a mesma pose em carrosséis seguidos.

## Biblioteca de poses (da soul-ref) — trocar o personagem e o figurino conforme o tema

| # | Pose | Bom para | Trecho de prompt |
|---|---|---|---|
| 02 | Salto contra o céu, câmera rente à grama | urgência, velocidade | `extreme low angle from the grass, leaping in mid-air, arms stretched out, vast deep blue sky above` |
| 10 | Sentado baixo contra a parede, sombra diagonal | manifesto, CTA sério | `sits low on a wooden crate leaning back against a plain wall, forearms on knees, hard side light, sharp diagonal shadow` |
| 16 | No alto de um bloco de concreto, céu nublado | dúvida, coragem | `extreme low angle, sits on top of a sharp concrete wedge against a dramatic cloudy sky, looking down` |
| 17 | Corredor estreito de paredes brancas | busca, caminho | `walks toward the camera through a narrow corridor of tall white walls opening to a deep blue sky` |
| 19 | Cadeira dobrável, curvado, exausto | cansaço, sobrecarga | `sits on a metal folding chair, leaning forward, elbows on knees, smartphone at his ear, tired heavy eyes` |
| 21 | Casaco longo em movimento | energia, apresentação | `dynamic off-balance pose, long plain navy overcoat flaring out in motion, fully buttoned white shirt` |
| 25 | Inclinado para trás num banquinho | CTA leve | `leans far back on a tall black stool, one hand gripping the seat, long legs stretched diagonally` |
| 32 | Mãos abertas contra a câmera | CTA "pare/olha" | `pushes both open hands toward the camera, fingers spread, forced perspective, face between the hands` |
| 37 | Sentado num cubo de metal, mão no queixo | CTA confiante | `sits on a brushed metal cube, legs wide apart, oversized black suit, one hand on his chin` |
| 42 | De perfil num banquinho alto | CTA calmo | `sits sideways on a tall black stool, one ankle on the other knee, calm profile` |

Modelo de prompt:
`Editorial fashion photograph, full body: <descrição do personagem> <pose da tabela>, <figurino liso sem estampa>,
<expressão séria>, mouth closed, not smiling. <cenário navy/cyan>. The figure in the lower half of the frame, his
head at the vertical middle, large empty <backdrop|sky> above his head. No text, no letters, no logos, no glasses,
no hat, no jewelry`

## Título grande atrás do sujeito (capa)

1. Hook em **2 linhas curtas** (até ~10 letras cada) + `emocao` curta; total até 10 palavras.
2. `python ../../../../../motor/compor.py carrossel.json --led slide2` (apague `carrossel.json.bak` antes: o compor
   relê o .bak e desfaz edições). Se o compor recusar o recorte ("recorte sujo"), gere com rembg
   (`isnet-general-use`) e escreva `recorte` + `sujeito.cabeca` à mão.
3. `python ../../../../../motor/capa_grande.py carrossel.json --tema ../../design-system/tema` — bloco central de
   1020u e cabeça mordendo ~50px da última linha.
4. Abra o `png/slide-01.png`: se a cabeça cobrir número ou letra-chave, rode com `--alinhar direita` ou
   `--alinhar esquerda` até ela cair num espaço entre palavras.
5. CTA (T4): mesmo efeito, `bloco` com `y = topo da cabeça + 50 − altura do display` (mínimo 150).

## Fila: intercalar personagem e banco

O publicador (`skills/post-instagram/scripts/publish_next.py`) alterna sozinho: depois de um post com `personagem`
no metadata vem um sem personagem (imagem de banco/cena), e vice-versa. Por isso todo carrossel com personagem precisa
de `personagem` = `luizota`, `wel` ou `ambos` no `png/metadata.json`, e todo carrossel de banco deixa o campo vazio.
