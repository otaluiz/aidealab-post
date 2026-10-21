---
name: criar-motion
description: Cria carrossel ANIMADO (motion suave) para a aidealab com HyperFrames — 6 slides de vídeo 1080×1440 × 6 s, a partir de um tema de carrossel da semana (campanha/semanas/<ano>-W<nn>.md). Capa e CTA sempre sobre imagem (personagem @luizota/@wel ou banco de imagens), miolo só tipografia + UI animada. Dispara com "carrossel animado", "carrossel com motion", "criar motion <tema>". Não publica.
---

# Criar motion (carrossel animado)

Projeto de referência (aprovado como teste em 20/10/2026):
`otaluiz/claude-motion` → `carrosseis/2026-W43-automatize-o-basico/`
(`index.html` = composição HyperFrames, `variaveis.json` = versões, `render.sh` = render + corte por slide).
Copie a pasta, troque o texto dos slides e as imagens; a estrutura de motion fica.

## Produção (fila e carrosséis novos)

**Carrossel novo → `motor/motion/fonte.py` (seção abaixo), usado pela rotina diária e pela `criar-post`.**
O `motion.py` fica só para carrossel antigo sem `carrossel.json` (fila já aprovada, só arte final):
`python motor/motion/motion.py <pasta>` converte qualquer carrossel do motor (pasta com `metadata.json` +
`slide-NN.png`) em vídeos `slide-NN.mp4` e grava `slides[].video`. Capa, slide 2, CTA e slides sem texto (T5)
usam a arte aprovada com efeito por cima; o miolo é refeito em tipografia animada a partir de `slides[].texto`.
O `post-instagram` publica os vídeos e cai para os PNGs se o Instagram recusar. O projeto de referência abaixo
é para peça feita à mão (texto da capa animado sobre foto limpa, recorte com título atrás da cabeça).

## Carrossel novo (fonte = carrossel.json) — formato validado em 21/10/2026

`python motor/motion/fonte.py <pasta do carrossel>` (piloto: `clientes/aidealab/carrosseis/follow-up-ninguem-faz`).
- Texto animado em todos os slides, montado do `carrossel.json` (display, emoção, lista, CTA).
- **Parallax só nos slides com imagem (capa, slide 2, CTA)**, com a imagem ESTÁTICA: recorte do elemento
  principal (o do motor ou rembg) + placa sem o elemento (OpenCV inpaint), camadas em velocidades diferentes;
  personagem só respira de leve. **Nunca gerar vídeo nem gastar crédito para animar personagem.**
- Slides de texto no formato anterior: tipografia animada, grade/LED respira no lugar, sem camadas andando.
- **Texto nunca em cima de rosto:** cada slide com foto leva as caixas de rosto (`sujeito` do motor ou detecção
  OpenCV) e o layout tira título/serifada/botão de cima delas antes de animar (margem que cobre o parallax).

## Formato

- Composição única 1080×1440, 30 fps, 6 slides × 6 s (`data-duration="36"`); o `render.sh` corta um MP4 por slide
  (`out/<versao>/slide-0N.mp4`) para subir como carrossel de vídeos.
- Tema visual = `clientes/aidealab/design-system/tema` (navy `#0A0E16`, ciano `#6EC9F7`, papel `#E9EEF4`, Inter 900 +
  Yellowtail + Manrope + Fira Code, fontes locais em `fonts/`). Alternar fundo ink/papel no miolo.
- Sequência: capa (foto) → tensão → lista/explicação → como fazer → conclusão (com fonte) → CTA (foto).

## Motion (suave)

- Tudo entra com `expo.out`/`power3.out` e assenta até ~3,5 s; depois só o ambiente respira (loop limpo no IG).
- Display: revela por máscara (linha com `overflow:hidden`, `yPercent 105 → 0`, stagger 0,12 s).
- Textos de apoio: sobem 30 px com blur 10 → 0.
- Foto (capa/CTA): começa escura e com zoom (scale 1.16, brightness .35) e assenta em 6 s; bloom (cópia borrada em
  `screen`) respira; poeira com PRNG semeado sobe na névoa. Nada de `Math.random()` puro nem relógio.
- Personagem: recorte (rembg `isnet-general-use`) por cima do display, com o MESMO tween da foto, para o título
  ficar atrás da cabeça (cabeça morde ~40–50 px da última linha, como no `personagens.md`).
- Validar com `npx hyperframes check` (0 erros) e conferir quadros do vídeo final antes de entregar.

## Imagens: duas versões

O projeto tem a variável `versao` (`personagens` | `banco` | `cena`), escolhida no `render.sh <versao>`.

1. **personagens** — capa e CTA com @luizota / @wel (alternar quem faz capa e CTA entre carrosséis). Gerar com
   `soul_2` + `soul_id` seguindo `clientes/aidealab/design-system/personagens.md`. **`soul_2` é só para os
   personagens.**
2. **banco** — capa e CTA do banco `Clientes/aidealab/02-Materiais-Brutos/img-ref` (Drive). Custo zero. Escolher
   imagem com céu/área vazia no terço de cima (título) e sujeito no meio/baixo. Depois de entregar, mover as usadas
   para `01-Referencias/Instagram/img-ref` (regra da `criar-post`).
3. **cena** — cena gerada sem personagem; só quando o banco não tiver nada que sirva.

## soul_2: zero texto na imagem

O `soul_2` desenha letras falsas em tudo que lembra texto (balões de conversa, telas, placas, cartazes, rótulos,
camisetas). Escrever "no text" no prompt não resolve. Portanto:

- **Não pedir nenhum objeto que carregue texto**: nada de balão de chat, tela de celular acesa, letreiro, placa,
  documento, cartaz, embalagem com rótulo. Celular só `plain dark smartphone with a blank dark screen`.
- O texto e a UI (chat, atalho, lista) são sempre feitos em HTML na composição, nunca na imagem.
- Terminar o prompt com `No text, no letters, no logos, no signs, no glasses, no hat, no jewelry`.
- Conferir a imagem ampliada antes de usar; se vier letra, regerar ou cortar abaixo dela. Não entregar com texto falso.
