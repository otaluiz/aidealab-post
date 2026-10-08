# Pauta da rotina diária — aidealab (@idea_lab7)

Fonte de verdade editorial da rotina "aidealab - carrossel diário 8h". Plano completo e
justificativas em `plano-instagram-2026-10.md` (mesma pasta). Revisar a cada 14 dias.

## Para quem
Dono(a) de pequeno negócio sem time de marketing (loja, clínica, serviço local, MEI) que
responde cliente no WhatsApp e quer vender mais sem virar técnico. Nunca falar com designer
ou com profissional de marketing.

## Promessa do perfil
IA e marketing que o pequeno negócio usa amanhã de manhã: WhatsApp, Google e Instagram,
passo a passo, sem hype.

## Pilares (rotação; nunca 2 iguais seguidos; oferta no máximo 1 a cada 5)
| Pilar | Peso | Formato preferido (ig-carousel-planner) | Objetivo |
|---|---|---|---|
| educacional | 40% | IG5 lista / IG8 framework "rouba esse método" | salvamento |
| tendência | 25% | notícia do dia traduzida: "o que muda pro seu negócio" | envio por DM |
| prova/bastidor | 20% | IG6 antes/depois, caso real, raio-x de perfil | seguir |
| oferta | 15% | dor + o que a aidealab faz + palavra na DM | lead |

## Séries (usar o nome da série no slide 1 ou no rodapé da legenda)
- **IA no balcão** — uma tarefa do dia a dia resolvida com IA.
- **Mito ou verdade** — crença comum sobre IA/marketing, corrigida (IG7).
- **Raio-X** — 3 ajustes num perfil/negócio (só com caso real).
- **Saiu hoje** — novidade da semana (Meta, Google, WhatsApp, Instagram, ChatGPT/Gemini/Claude) e o que fazer com ela.

## Banco de temas (usar quando a tendência do dia não servir; riscar ao usar)
- [x] WhatsApp Business com IA: 5 coisas para arrumar antes de ligar (whatsapp-ganhou-ia)
- [ ] Mito ou verdade: 5 frases sobre IA no pequeno negócio
- [ ] O Google agora responde por você: seu negócio aparece?
- [ ] A semana de conteúdo em 1 hora com IA (você reescreve a 1ª frase)
- [ ] Para quem é a aidealab (manifesto, para fixar)
- [ ] Catálogo do WhatsApp que vende sozinho
- [ ] Avaliação no Google: como pedir sem constranger
- [ ] Resposta pronta x resposta com IA: quando usar cada uma
- [ ] Legenda que aparece na busca do Instagram (palavra-chave na 1ª linha)
- [ ] O que o cliente pergunta antes de comprar (e o post que responde)

## Regras de copy
- Slide 1: promessa + loop aberto, até 10 palavras, com palavra que o cliente busca
  (ex.: "WhatsApp", "Google", "Instagram", "IA", "cliente", "venda").
- Valor mais forte nos slides 2–3. Um ponto por slide. Último slide = resumo salvável + 1 pedido.
- Nunca inventar número, cliente ou resultado. Dado de notícia só com a fonte na legenda
  ("segundo <veículo>").
- Legenda: gancho nos primeiros 125 caracteres, 1 pergunta concreta, CTA "Comenta PALAVRA".
  Alternar com "Manda pra quem ..." (envio por DM) em tendência e mito.
- Hashtags 3–5: 1 ampla + 2 de nicho + `#aidealab`. Base: `#iaparanegocios #pequenosnegocios
  #whatsappbusiness #marketinglocal #instagramparanegocios`.

## Como usar os dados diários
- `automation/cloud/estado-instagram.json`: `top5` mostra o tipo de gancho e o tema que
  mais gerou envio/salvamento/seguidor por alcance → repetir a forma, não o tema. Base 08/10: o que mais rendeu foi frase de contraste
  ("X não é só Y. É Z.") e entrega prática aberta ("Dois prompts. Abertos."); o pior foi abertura
  genérica de agência e tema de história do design.
  `piores5` → evitar a forma. Se tiver `erro`, ignore e siga a pauta.
- `automation/cloud/estado-tendencias.json`: notícias das últimas 48h do nicho. Escolha
  só o que muda algo prático para o pequeno negócio. Ignore política, esporte, crime,
  celebridade e notícia de empresa grande sem efeito para PME. `google_trends_br` é
  termômetro geral; só use se tiver ligação real com o nicho.
