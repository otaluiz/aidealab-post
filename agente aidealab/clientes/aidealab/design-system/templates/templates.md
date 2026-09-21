# Templates — aidealab post design system

3 templates reusáveis (ver render real em `../index.html`). Cada um cobre um
papel no arco hook → problema → explicação → solução → CTA.

## 1. Capa (hook)

**Quando usar**: sempre o slide 1 do carrossel (ou o único slide, no formato
imagem única). É o hook — 2 segundos para parar o scroll.

- Kicker pequeno no topo (`AIDEA LAB · <categoria>`), cor primária.
- Headline grande (88–96px, **Inter 900**), uma frase curta.
- **Palavra de ênfase em `Fraunces` itálica 900** (não só cor) — ~1.15× maior
  que o resto da headline, cor accent (`#EB47B4`) com leve glow. Dupla
  sans+serif inspirada na referência "best *font* pairings" (@adarshxdesign) —
  ver `../../criar-post/references/principios-design.md`. Essa dupla é
  exclusiva da capa e do CTA; nunca aparece em slide de conteúdo.
- Subtexto de apoio (opcional), 1 linha, Manrope, cor muted.
- Fundo com glow radial sutil (primária + accent) atrás do texto — nunca
  imagem gerada por IA com texto embutido.
- Indicador "arraste para o lado" no rodapé, além do @handle.
- Regras aplicadas: texto grande e ousado, hook sobre resultado (não sobre
  tópico), alto contraste, limpo e focado.

## 2. Conteúdo

**Quando usar**: slides do meio — problema, explicação, solução. Repete o
quanto for preciso.

- Tag/pill no topo indicando a função do slide (`O problema`, `A solução`...).
- Headline média (56–64px), **só Inter 900 — sem Fraunces**, fixa na mesma
  posição em todo slide de conteúdo. A dupla sans+serif fica reservada pra
  capa e CTA, os dois momentos de maior carga; conteúdo não compete por
  atenção com eles.
- Corpo de texto (32–40px, Manrope) abaixo — parágrafo curto ou 2–3 pontos,
  nunca bloco longo (regra "limpo e focado").
- Rodapé com @handle + indicador de slide (`0X/0Y`).

## 3. CTA (fechamento)

**Quando usar**: sempre o último slide.

- Headline centralizada, tom de convite/ação (72–80px), **mesma dupla
  Inter 900 + Fraunces itálica accent da capa** na palavra de ênfase.
- Pill de CTA em Inter 900 sobre accent (`#EB47B4`) com glow, texto curto e
  imperativo — o botão em si fica em sans (não itálico), pra ficar legível
  como ação clicável.
- Subtexto de apoio (ex: oferta, prazo, forma de contato), Manrope.
- Rodapé com @handle (sem indicador de "próximo slide" — é o fim).

## Regra comum aos 3

- Margem lateral 80px, margem topo/base 96px — nunca variar entre slides do
  mesmo carrossel (grid do feed coerente).
- Rodapé fixo em altura (100–120px) e posição em todos os templates.
- Fundo sempre `#0D0D12` dominante — cor não vira decoração, vira hierarquia
  (primária = destaque neutro, accent = a única coisa que "grita").
