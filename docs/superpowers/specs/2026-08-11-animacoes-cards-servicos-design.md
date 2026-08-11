# Animações dos cards de serviços — design

Data: 2026-08-11
Origem: artefato "Animações dos cards de serviços" (README do projeto), refinado em brainstorming.

## Objetivo

Doze animações em loop, sem texto, uma por serviço do site da agência. Feitas em
Remotion (React → vídeo), renderizadas em MP4 e exibidas dentro dos cards de
serviço com `mix-blend-mode: screen`.

## Decisões tomadas no brainstorming

| decisão | escolha | por quê |
| --- | --- | --- |
| Paleta | inventada aqui | não existe site nem repo de referência ainda |
| Linguagem visual | line-art + glow | lê bem em 320px e unifica 12 serviços muito diferentes |
| Formatos | só MP4 | pedido explícito do usuário; sem WebM alpha |
| Integração | fundo preto + `mix-blend-mode: screen` | dá alpha de graça num formato sem canal alpha |
| Escopo | projeto + render dos 12 MP4 | |

### Desvios em relação ao artefato original

Consequência direta de MP4 + `screen`:

1. `Stage.tsx` não tem gradientes. O fundo é `#000000` puro — qualquer cor no
   fundo sobrevive ao `screen` e vira um retângulo visível sobre o card.
2. O prop `transparent` não existe. Ele servia para remover o fundo nos WebM
   alpha, que saíram do escopo.
3. `npm run render` gera apenas `out/mp4/*.mp4`.

## Arquitetura

Projeto novo e isolado em `D:\claude\animacoes-cards\`, com seu próprio
`package.json`. Não se mistura com o repo de skills que ocupa `D:\claude`.

```
animacoes-cards/
  package.json
  remotion.config.ts
  src/
    index.ts           registerRoot
    Root.tsx           as 12 <Composition>, 640×640, 30fps, 120 frames
    theme.ts           paleta, famílias de cor, larguras de traço
    anim.ts            wave() bell() cycle() — helpers periódicos
    Stage.tsx          fundo preto puro + glow compartilhado
    parts/             primitivas de line-art
      Ring.tsx         anel/arco tracejado
      Dot.tsx          ponto com halo
      DrawPath.tsx     path SVG que se desenha via strokeDashoffset
      Bar.tsx          barra de traço
      Pulse.tsx        onda de impacto que expande e some
    scenes/            12 arquivos, um por serviço
  out/mp4/             saída do render
```

**Abordagem escolhida:** componentes independentes por cena **mais** uma
biblioteca de primitivas compartilhadas (`parts/`). A alternativa de 12 arquivos
totalmente livres faria cada um reimplementar "anel que pulsa" com resultados
divergentes; a alternativa de um motor declarativo único não comporta 12
conceitos genuinamente diferentes. Com primitivas, cada cena vira um arquivo de
40–70 linhas que compõe em vez de redesenhar.

### Regra do loop

Toda função de tempo é periódica no comprimento da composição (120 frames), então
o frame 119 encosta no frame 0 sem salto visível.

- `wave(p)` → 0→1→0 com derivada zero nas duas pontas (respiro, vaivém)
- `bell(p)` → envelope de entrada/saída (partículas, pulsos)
- `cycle(frame, D, offset)` → progresso com defasagem, para escalonar elementos
  sem quebrar o loop
- rotações usam voltas inteiras por ciclo

Proibido: `useState`, `useEffect`, `Math.random()` (usar `random()` do Remotion
com seed fixa), e `spring()` ou `interpolate` linear que não fechem o ciclo.
Tudo é função de `useCurrentFrame()`.

## Sistema visual

Luz aditiva sobre preto. Traço de 3–4px, sem preenchimentos opacos, glow via
`filter: blur()` em cópias do traço. Nada de cinza fosco: sob `screen` um cinza
médio vira véu sujo em cima do card.

A cor agrupa os doze serviços em três famílias de quatro. O olho lê a família
antes de ler o ícone.

| família | base | destaque | serviços |
| --- | --- | --- | --- |
| Aquisição | `#3B82F6` | `#7DD3FC` | TrafegoPago, RedesSociais, SEO, Sites |
| Criativo | `#FACC15` | `#FDE68A` | Audiovisual, DesignerGrafico, Branding, MotionGraphics |
| IA & Dados | `#A855F7` | `#D8B4FE` | Chatbot, Automacao, AnaliseDados, Dashboards |

O tom base desenha a estrutura; o tom de destaque marca o elemento que
"acontece" na cena — o impacto, o pulso, o ponto ativo.

## As 12 composições

Todas: 640×640, 30fps, 120 frames (loop de 4s).

### Aquisição — azul

| id | serviço | animação |
| --- | --- | --- |
| `TrafegoPago` | Tráfego Pago Estratégico | Três anéis concêntricos. Um cursor entra na diagonal, crava o centro e dispara ondas de impacto que se dissolvem. O cursor sai por onde entrou. |
| `RedesSociais` | Gestão de Redes Sociais | Nó central respirando, três balões orbitando em velocidades diferentes. Corações sobem e evanescem em cascata defasada. |
| `SEO` | SEO Avançado | Lupa varre uma pilha de barras da esquerda para a direita. A barra iluminada sobe para o topo e a pilha reacomoda. |
| `Sites` | Sites, E-commerce e LPs | Wireframe de página se monta linha a linha (header → hero → grid de 3). Cursor clica num card e tudo desmonta na ordem inversa. |

### Criativo — amarelo

| id | serviço | animação |
| --- | --- | --- |
| `Audiovisual` | Produção Audiovisual & Drone | Drone em X com 4 hélices girando em voltas inteiras, oscilando em voo pairado. Abaixo, um retículo de enquadramento respira. |
| `DesignerGrafico` | Designer Gráfico & Criação | Curva bezier se desenha ponto a ponto, handles aparecem e giram, a curva se apaga na mesma direção. |
| `Branding` | Branding & Identidade Visual | Quatro formas soltas convergem e travam num monograma losango, pulsam juntas uma vez, e se soltam de volta. |
| `MotionGraphics` | Motion Graphics & Animação | Timeline com keyframes. Uma curva de easing se desenha entre eles e uma forma percorre o path no timing exato da curva. |

### IA & Dados — roxo

| id | serviço | animação |
| --- | --- | --- |
| `Chatbot` | Chatbots com IA Avançada | Núcleo hexagonal com respiração. Balões entram alternados esquerda/direita, com três pontos de digitação pulsando antes de cada um. |
| `Automacao` | Automação de Processos & Leads | Fluxograma de 5 nós. Um pulso de luz percorre o caminho, ramifica em dois no nó do meio e reconverge no final. |
| `AnaliseDados` | Análise de Dados & Preditivos | Nuvem de pontos com seed fixa. Uma linha de regressão se ajusta até assentar, com faixa de previsão respirando ao redor. |
| `Dashboards` | Dashboards Interativos | Grade de 4 widgets (barras, donut, sparkline, contador em anel) animando com defasagem, como um painel ao vivo. |

## Render

```bash
npm install
npm run studio     # Remotion Studio com as 12 composições
npm run render     # gera out/mp4/*.mp4
```

Uma de cada vez:

```bash
npx remotion render Chatbot out/mp4/Chatbot.mp4 --codec=h264 --crf=20
```

Fundo `#000000`, h264, crf 20.

## Uso no site

```html
<video autoplay loop muted playsinline preload="none"
       style="mix-blend-mode: screen">
  <source src="/anim/Chatbot.mp4" type="video/mp4" />
</video>
```

O `mix-blend-mode: screen` zera o preto do vídeo, deixando só o traço e o glow
sobre o card — funciona sobre qualquer gradiente ou hover.

Notas de performance, já que o site carrega doze deles:

- `preload="none"` e só chamar `play()` quando o card entrar no viewport, via
  `IntersectionObserver`. Vídeo parado fora da tela custa quase nada.
- Renderizar a 320×320 se o card exibir pequeno — metade da resolução corta o
  peso em cerca de 4×.
- Respeitar `prefers-reduced-motion`: pausar o vídeo, que fica exibindo o
  primeiro frame.

## Critérios de sucesso

1. `npm run studio` abre com as 12 composições listadas.
2. Cada composição faz loop sem salto visível entre o frame 119 e o 0.
3. Nenhuma cena usa `useState`, `useEffect` ou `Math.random()`.
4. O fundo renderizado é `#000000` puro, verificável no MP4.
5. Os 12 MP4 existem em `out/mp4/`.
6. Sobre um card com gradiente, com `mix-blend-mode: screen`, nenhuma borda
   retangular do vídeo é visível.
