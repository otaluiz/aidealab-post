# Referências de imagem — aidealab (Materiais Brutos)

5 imagens deixadas pelo usuário em `02-Materiais-Brutos` no Drive, pra guiar a
**camada de imagem/background** gerada via Comfy Cloud MCP (Etapa 4 da
`criar-post`, ainda não executada — este documento é só a leitura de
layout/composição, feita antes de gerar qualquer coisa).

## Análise de composição (comum às referências)

1. **Duotone/gradient-map ousado** — 4 das 5 usam mapeamento de cor em 2–3
   tons (azul+vermelho, ciano+amarelo, magenta+ciano+dourado), não fotografia
   naturalista straight. Combina direto com a paleta neon da aidealab
   (`#6EC9F7`/`#0D0D12`/`#EB47B4`/`#FFD980`).
2. **Faixa de luz/energia cortando a composição** — banda de neon horizontal
   (`ref.png`, colagem de 8 cenas), anéis girando tipo Saturno
   (`Futuristic Call.png`), faixa de "scan/glitch" horizontal
   (`Surreal Portrait Art.png`). Recurso visual repetido entre as
   referências, não coincidência — vira candidato a elemento recorrente nos
   backgrounds gerados.
3. **Sujeito centralizado, fundo atmosférico simples** — silhueta/pessoa/
   objeto no centro, muito espaço negativo ao redor, fundo enevoado ou
   estúdio liso (nunca cena cheia de elementos concorrendo com o texto do
   slide — importante porque o texto do post entra por cima via
   `canvas-design`, o fundo não pode competir).
4. **Tema tech/futurista permeando** — computador retrô Y2K com tela "Y2K" +
   borboleta pixelada (`Retro Rainbow Computer.png`), "chamada futurista"
   com energia digital girando na cabeça (`Futuristic Call.png`). Bate
   direto com o posicionamento de IA/tecnologia da aidealab.

**Fora do padrão**: `still_life_640_N.webp` (streetwear + girassóis,
duotone ciano/amarelo, colagem de fita adesiva no fundo) é mais pop/editorial
— lida como referência de **ousadia de cor plana**, não de composição
atmosférica de fundo.

## Como isso deve informar a Etapa 4 (quando rodar)

- Fundos gerados via Comfy Cloud (pipeline OSS, "melhores modelos
  gratuitos") devem mirar: atmosfera/duotone na paleta da marca, espaço
  negativo generoso pra não brigar com o texto, e — quando fizer sentido pro
  tema do post — uma faixa de luz/energia horizontal ou diagonal como
  elemento de composição.
- Sujeito (se houver) sempre centralizado ou com respiro nas bordas — nunca
  preenchendo o frame, porque headline/kicker/rodapé do template
  (`templates/templates.md`) já ocupam margens fixas de 80–96px.
- Arquivos originais ficam em `02-Materiais-Brutos` no Drive (aidealab); não
  duplicados aqui — este documento é só a leitura, não os assets.
