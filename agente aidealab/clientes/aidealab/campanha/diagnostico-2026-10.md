# Diagnóstico @idea_lab7 — outubro 2026

Feito com a `instagram-skills` (`ig-audience-insights`, `ig-profile-optimizer`). Dados reais da Graph API em
`automation/cloud/estado-instagram.json` (08/10/2026). Os dados do nicho via Apify (`automation/cloud/estado-nicho.json`)
entram na próxima coleta semanal, assim que o `APIFY_TOKEN` estiver cadastrado; até lá esta seção do nicho fica
vazia de propósito (nada inventado).

## Números do perfil (08/10)
| Métrica | Valor |
|---|---|
| Seguidores | **442** (443 em 07/10) |
| Seguindo / posts | 215 / 22 |
| Alcance da conta, 28 dias | **343 contas** (menor que a base de seguidores) |
| Visitas ao perfil, 28d | 102 |
| Cliques no link, 28d | 3 |
| Contas engajadas, 28d | 27 |

## Desempenho dos posts
- Últimos 6 carrosséis (03–08/10): alcance **8, 13, 13, 20, 71, 20**. Salvamentos e envios: **0** em todos.
- Desde 21/09: 0 seguidores ganhos por post, só 1 envio.
- Os únicos posts que passaram de 150 contas foram **Reels de 2025** (254–493 contas; um teve 7 envios).
- Melhor forma recente (alcance ≥ 30): frase de contraste ("Marketing não é só aparecer. É saber onde..."),
  entrega prática aberta ("Dois prompts. Abertos."), apresentação de serviço com prova.
- Pior forma: abertura genérica de agência, série de história do design (fala com designer, não com o cliente).

**Leitura (ig-audience-insights):** o conteúdo não sai da bolha. Sem salvamento e sem envio o algoritmo não
distribui; sem Reels não há alcance para quem não segue. O alcance caiu enquanto a fila publicava carrosséis de
design e serviços; os carrosséis do nicho novo (IA para pequeno negócio, com personagem) entram a partir de 10/10.

## Perfil — scorecard (ig-profile-optimizer)
| Parte | Status | Ação |
|---|---|---|
| Foto | conferir no app | logo legível pequeno ou rosto, alto contraste |
| NAME | falha (`AIdea Lab 🤖`) | `aidealab · IA pro seu negócio` (29) |
| @handle | ok (`idea_lab7`) | manter; rodapé dos carrosséis já corrigido |
| Bio | falha (lista de serviços, 5 emojis) | `IA que o pequeno negócio usa amanhã de manhã.` / `Atendimento, conteúdo e vendas no automático.` / `👇 Diagnóstico grátis do seu Instagram` |
| Link | falha (3 cliques/28d) | WhatsApp com mensagem pronta "Quero o diagnóstico grátis" |
| Categoria | conferir | "Serviço de consultoria empresarial" |
| Destaques | criar | Comece aqui · Antes/depois · IA no zap · Dúvidas · Fale com a gente |
| Grid 9 | falha (design + 2025 fora do nicho) | arquivar posts de história do design e eventos de 2025 |
| Fixados | definir | manifesto "Para quem é a aidealab" (Dia26 da fila), melhor Reel, 1 prova |

## Nicho (Apify) — preencher pela coleta semanal
`estado-nicho.json` → `top_normalizado` (posts que performam por tamanho de conta), `formatos_top20`,
`contas_sugeridas`. A pauta semanal (`semanas/`) usa esses dados para escolher forma de gancho e formato.

## Conclusões que guiam a campanha
1. Reels é obrigatório: é o único formato que já trouxe gente de fora.
2. Todo carrossel precisa de motivo para salvar (checklist, passo a passo) ou enviar ("manda pra quem...").
3. Falar só com dono de pequeno negócio; tirar design do grid.
4. Personagens sérios e pose editorial (aprovado em 08/10) dão identidade; intercalar com cena de banco.
5. Corrigir perfil antes de investir em alcance: hoje quem visita (102) quase não segue nem clica.
