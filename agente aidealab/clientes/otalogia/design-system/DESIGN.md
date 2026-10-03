# otalogia — design system de posts

Status: proposta (Checkpoint 1). Contexto de negócio da marca ainda pendente.

## Conceito
O nome pede vocabulário de estudo: "-logia". O sistema é **modular e de bancada**: grade visível, formas chapadas geométricas, rótulos em mono, painéis de cor sólida. Nada de cartão de vidro, blur ou gradiente de ambiente: a marca se reconhece pela grade e pelas formas, não por foto.

## Cor
Preto `#0B0B12` (base) · Violeta `#7C3AED` · Azul `#2563EB` · Laranja `#FF7A1A` (accent) · Papel `#F5F5FA`.
Cada slide é de UM tema: **Noite** (preto), **Violeta** (painel roxo), **Azul** (painel azul) ou **Papel** (claro, texto preto). Laranja aparece como marca-texto (bloco laranja com texto preto) e no slide de CTA. Contraste: texto papel sobre noite/violeta/azul; texto preto sobre laranja/papel.

## Tipografia
- Display: Syne 800, caixa mista, tracking -2%, entrelinha .95.
- Corpo: Inter 400/600.
- Rótulo: JetBrains Mono 500, caixa alta, +8% de tracking (contador, tags, legendas de figura).

## Linguagem visual
- Grade de 12 colunas, margem 64px, linhas finas `--ota-linha` visíveis na capa.
- Raio 0 em painéis e molduras; pílula só em botão/CTA.
- Formas chapadas (círculo, quarto de círculo, quadrado) em azul/violeta/laranja como ilustração base; foto/cena entra dentro de moldura de linha fina quando o tema pedir.
- Marca-texto: UMA palavra por título em bloco laranja, texto preto.

## Templates
- **T1 Capa** — tema Noite, grade visível, formas chapadas, título grande com marca-texto, tag mono, "deslize".
- **T2 Conteúdo** — tema Violeta/Azul/Papel alternados; rótulo mono, título, moldura de figura com legenda "FIG.", corpo curto.
- **T3 CTA** — painel laranja inteiro, texto preto, botão preto em pílula.
- **Flyer** — T1 em escala de peça única, 1080×1440.

## Ritmo do feed
Capas sempre Noite; conteúdo alterna Violeta → Papel → Azul; CTA sempre laranja.

## Regras
- Tipo grande só em capa e CTA; miolo usa título médio.
- Contador em mono ("03 — 06"), nunca numeral gigante.
- Um marca-texto laranja por slide, no máximo.
- Texto sempre em HTML, nunca gerado por IA de imagem.
