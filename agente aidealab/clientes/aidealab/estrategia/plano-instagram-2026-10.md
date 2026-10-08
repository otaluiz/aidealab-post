# Plano Instagram @idea_lab7 — outubro 2026

Feito com a skill `instagram-skills` (`.claude/skills/instagram-skills`):
`ig-profile-optimizer`, `ig-audience-insights`, `ig-content-planner`,
`ig-carousel-planner`, `ig-hashtag-strategist`.

> **Limite desta análise:** o Instagram bloqueou a leitura pública do perfil
> (HTTP 401/429 sem login) e não há `APIFY_TOKEN` nem Insights no ambiente.
> O diagnóstico usa o que já foi publicado/agendado (fila em
> `skills/post-instagram/queue`, legendas em `clientes/aidealab/carrosseis`).
> Números de seguidores/alcance **não** foram inventados. Para fechar a leitura
> com dados reais, ver a seção 7.

---

## 1. Diagnóstico

**O que foi publicado (ordem aproximada):**

| Fase | Posts | Tema |
|---|---|---|
| Dias 1–14 | A ordem, O ornamento, A regra e a quebra, A tela, 3 sites que inspiram, Importância do branding/design, Três prompts na DM | design / branding / prompts |
| Dias 15–25 (fila) | Consistência, Estratégia, GEO busca com IA, Jornada do cliente, Serviços (3), Prova que vende, WhatsApp plantão, Clareza vende mais, Mitos de IA | marketing + IA para pequeno negócio |
| Rascunhos | Follow-up ninguém faz, Perfil Google parado, Pergunta do cliente vira post | IA aplicada ao dia a dia |

**Pontos fortes**
- Mudança certa de nicho: de "design bonito" para **IA aplicada a pequeno negócio**, que é específico e tem demanda (WhatsApp Business AI, Gemini no Perfil da Empresa, AI Mode).
- CTA por palavra-chave ("Comenta RETORNO / GOOGLE / PAUTA") gera comentário e conversa na DM, os dois sinais que mais pesam hoje.
- Legendas curtas, concretas, sem jargão. Hashtags em 5 (o tamanho certo para 2026).
- Sistema visual próprio (motor + design system) dá grid reconhecível.

**Problemas que travam crescimento**
1. **Grid com duas marcas.** Os 14 primeiros posts falam com designers; os novos falam com dono de negócio. Quem chega pelo post novo e rola o grid não entende para quem é o perfil.
2. **Só carrossel.** Carrossel ganha salvamento de quem já segue. Alcance de não-seguidor hoje vem de **Reels** (retenção) e de **envio por DM**. Sem Reels, o perfil depende de quem já está lá.
3. **@handle `idea_lab7` ≠ marca `aidealab`.** Número + underline dificultam busca e menção. O NAME (campo indexado) precisa carregar a palavra-chave.
4. **Posts de "serviços" seguidos (Dias 19–21)** = 3 posts de oferta em linha. Regra: no máximo 1 a cada 5.
5. **Sem série.** Cada post é avulso; série com nome cria hábito e motivo para seguir.

---

## 2. Perfil (ig-profile-optimizer)

Validar cada item no app; o que não deu para ver está marcado "conferir".

| Parte | Status | Ação |
|---|---|---|
| Foto | conferir | Logo legível em 110px ou rosto do Luiz com fundo liso. Alto contraste. |
| NAME (30) | provável falha | `aidealab · IA pro seu negócio` (29) |
| @handle | precisa melhorar | Se `@aidealab` estiver livre, migrar. Senão manter e reforçar no NAME. |
| Bio (150) | reescrever | ver abaixo |
| Link | conferir | Um link: diagnóstico grátis / WhatsApp. Não a home. |
| Categoria | conferir | "Agência de marketing" ou "Serviço de consultoria empresarial" |
| Destaques | criar | **Comece aqui · Antes/depois · IA no zap · Dúvidas · Fale com a gente** |
| Grid 9 | falha | Arquivar ou mover para baixo os posts de design puro; manter 9 do nicho novo no topo |
| Fixados (3) | definir | 1) "Mitos de IA no pequeno negócio" (alcance) 2) "WhatsApp plantão" (prova/útil) 3) post-manifesto "Para quem é a aidealab" (criar) |

**Bio proposta (escolher 1):**

A — 129 caracteres
```
IA que o pequeno negócio usa amanhã de manhã.
Atendimento, conteúdo e vendas no automático.
👇 Diagnóstico grátis do seu Instagram
```

B — 122 caracteres
```
Seu negócio vendendo mais com IA, sem virar técnico.
Posts toda semana com o passo a passo.
👇 Fale com a gente no WhatsApp
```

---

## 3. Plano para ganhar seguidores (90 dias)

**Meta de processo** (controlável): 5 posts/semana + stories diários + 30 min/dia de interação. Meta de resultado só depois de 2 semanas de Insights reais (seção 7).

### Mix semanal (ig-content-planner)
| Dia | Formato | Pilar | Objetivo |
|---|---|---|---|
| Seg | Carrossel | Educacional (lista/passo a passo) | salvamento |
| Ter | **Reel 20–40s** | Mito x verdade / tela gravada | alcance não-seguidor |
| Qua | Carrossel | Antes/depois ou bastidor de cliente | seguir |
| Qui | **Reel** | "Testei X no negócio do cliente" | alcance + envio |
| Sex | Carrossel | Oferta leve com palavra-chave na DM | lead |
| Diário | Stories 2–4 | enquete, bastidor, repost de post do dia | conversa |

### Alavancas de crescimento (em ordem de impacto)
1. **Reels 2x/semana.** Gancho falado nos 2 primeiros segundos, texto na tela, legenda com palavra-chave de busca. Repurpose: cada carrossel vira 1 Reel (tela gravada mostrando a mesma coisa).
2. **Conteúdo "manda pro sócio".** Pensar todo post para ser **enviado por DM**: dor específica + checklist. CTA alternado: "Manda pra quem ainda responde cliente à mão".
3. **Séries com nome fixo** (hábito = motivo para seguir):
   - *IA no balcão* — uma tarefa do dia a dia resolvida com IA
   - *Mito ou verdade* — Reels curtos
   - *Raio-X* — análise de um perfil/negócio (com autorização) mostrando 3 ajustes
4. **Collab posts** com 1 parceiro/mês (contador, nutricionista, loja local): coautoria aparece para as duas audiências.
5. **Interação diária (30 min):** comentar com substância em 10 posts de perfis do mesmo público (associações comerciais, Sebrae regional, perfis de dono de negócio local), responder todo comentário na primeira hora.
6. **SEO no Instagram:** palavra-chave na primeira linha da legenda e no texto do slide 1 (ex.: "atendimento no WhatsApp", "Google Meu Negócio", "IA para pequenas empresas"). Hashtag virou só classificação.
7. **Isca de DM** (skill `post-dm`): 1 por semana, entrega PDF. Comentário + DM = sinal forte e lead.
8. **Trial Reels** (testar para não-seguidores) nos Reels com gancho novo antes de mostrar a quem já segue.

### Regras de rotina
- Máx. 1 post de oferta a cada 5.
- Toda legenda: gancho nos primeiros 125 caracteres, uma pergunta concreta, uma palavra-chave de CTA.
- Hashtags: 3–5 (1 ampla, 2 de nicho, 1 de marca). Base: `#iaparanegocios #pequenosnegocios #whatsappbusiness #marketinglocal #aidealab`.

---

## 4. Temas em alta no nicho (pesquisa out/2026)

| Tema | Por que agora | Fonte |
|---|---|---|
| **IA dentro do WhatsApp Business** ("IA para Empresas" / Meta Business Agent) | Lançado no Brasil em fev/2026 para PMEs; exige catálogo com pelo menos 1 item; agente com venda dentro da conversa e passagem para humano | Forbes, Startups, Digisac |
| **Gemini no Perfil da Empresa (Google)** | Anunciado no Google for Brasil 2026: gerenciar perfil por voz/texto, ver ligações e rotas; mira ~13 mi de MEIs | Showmetech |
| **Modo IA do Google / GEO** | Busca responde em texto e cita marcas; perfil no Maps e conteúdo claro influenciam | Conversion |
| **Autenticidade x conteúdo de IA** | Saturação de post genérico; público valoriza bastidor e voz humana | Canaltech, Mundo do Marketing |
| **Busca dentro do Instagram** | Legenda, texto na imagem e palavra-chave pesam mais que hashtag | Metricool, Rafael Terra |
| **Envio por DM como sinal principal** | Compartilhamento e retenção acima de curtida | Metricool |

> Números de blogs de agência (ex.: "carrossel salvo 9x mais") não foram usados nos roteiros por falta de fonte oficial.

---

## 5. Roteiros de carrossel (ig-carousel-planner)

Formato 4:5, 1 ideia por slide, legível em 2 s. Passar pelo `criar-post` para render. Nenhum número inventado: onde há `[ ]`, preencher com dado real de cliente ou remover.

### C1 — "O WhatsApp agora tem IA. Antes de ligar, faça isto" · IG5 Listicle · salvamento
1. **O WhatsApp Business ganhou IA. Ligar sem preparar é pedir pra ela responder errado.**
2. Onde fica: Ferramentas → *IA para Empresas*. Precisa do app em português e pelo menos 1 item no catálogo.
3. **1. Catálogo completo.** A IA responde com o que está lá. Sem preço, ela não sabe o preço.
4. **2. Horário e endereço certos** no perfil comercial.
5. **3. As 10 perguntas que mais chegam** escritas com a resposta que você daria.
6. **4. Quando passar pra você:** reclamação, desconto, pedido grande.
7. **5. Teste você mesmo** de outro número antes de liberar.
8. Payoff: checklist dos 5 itens num slide só + "Salva e faz no domingo."

Legenda: `O WhatsApp Business agora responde cliente com IA. Mas ela só sabe o que você ensinou. Antes de ligar, arruma esses 5 pontos. Comenta ZAP que a aidealab te manda o modelo das 10 perguntas.`

### C2 — "Mito ou verdade: IA no pequeno negócio" · IG7 Myth-Buster · envio
1. **5 coisas que te falaram sobre IA no seu negócio. 3 são mentira.**
2. "É caro" → **Mito.** O que pesa é tempo de configurar, não assinatura.
3. "Vai parecer robô" → **Depende.** Com suas respostas reais, soa como você.
4. "Substitui o atendente" → **Mito.** Tira o repetitivo; o humano fica com o que vende.
5. "Precisa de site e sistema" → **Mito.** WhatsApp + Google + Instagram já dão conta.
6. "Quem começar antes leva vantagem" → **Verdade.**
7. Payoff: tabela mito/verdade + "Manda pra quem ainda acha que IA é coisa de empresa grande."

### C3 — "O Google agora responde por você. Seu negócio aparece?" · IG6 Antes/Depois · seguir
1. **Pergunta pro Google "onde tem X perto de mim". A resposta vem pronta. Seu nome está nela?**
2. Antes: busca mostrava 10 links. Agora: um texto que cita poucos nomes.
3. De onde a IA tira: Perfil da Empresa, avaliações, fotos, site claro.
4. Antes/depois de um perfil `[cliente real, com print]`.
5. **3 ajustes desta semana:** responder avaliações · categoria e serviços completos · 1 foto nova.
6. Novidade: dá pra gerenciar o perfil pelo Gemini por texto ou voz.
7. Payoff: "Comenta GOOGLE que a gente olha o seu."

### C4 — "Steal this: a semana de conteúdo em 1 hora com IA" · IG8 Framework · salvamento
1. **Como a gente monta 5 posts em 1 hora (o método inteiro).**
2. Passo 1 — junta 20 perguntas reais de clientes (WhatsApp, Direct, balcão).
3. Passo 2 — agrupa em 5 temas.
4. Passo 3 — IA faz o rascunho com o prompt `[prompt real da casa]`.
5. Passo 4 — **você reescreve a primeira frase com a sua voz.** É isso que separa de post genérico.
6. Passo 5 — agenda tudo de uma vez.
7. Payoff: as 5 etapas num slide + "Comenta PAUTA e recebe o prompt."
> Liga com o tema "autenticidade": IA faz a base, a voz é sua.

### C5 — "Raio-X: 3 ajustes no Instagram de [negócio local]" · série Raio-X · envio/collab
1. **Analisamos o Instagram de uma [padaria/clínica]. 3 ajustes simples mudam tudo.**
2. Bio: antes / depois.
3. Primeira linha da legenda com palavra que o cliente busca.
4. Destaques na ordem da dúvida do cliente.
5. Payoff + "Quer o raio-X do seu? Comenta RAIO-X." → publicar como **collab** com o negócio.

### C6 — "Para quem é a aidealab" · manifesto · fixado
1. **Se você responde cliente à mão às 23h, esse perfil é pra você.**
2. Quem a gente ajuda: dono de pequeno negócio sem time de marketing.
3. O que você vai ver aqui: IA no WhatsApp, Google e Instagram, passo a passo.
4. O que não vai ver: hype, ferramenta que você nunca vai usar.
5. Bastidor: foto real do Luiz/equipe.
6. Payoff: "Segue e ativa o sininho. Toda semana uma tarefa a menos."

---

## 6. Roteiros de Reels (repurpose dos carrosséis)

**R1 — Tela gravada (C1), 30s**
- 0–2s (falado + texto): "O WhatsApp Business ganhou IA. Olha onde fica."
- 2–20s: gravação do celular indo em Ferramentas → IA para Empresas, mostrando o catálogo.
- 20–28s: "Sem catálogo, ela não liga. Sem preço, ela inventa desculpa."
- 28–30s: "Comenta ZAP que eu te mando o checklist."

**R2 — Mito ou verdade (C2), 3 cortes de 8s** — cada mito com placa VERDADE/MITO, rosto do Luiz, fim com "manda pra quem precisa ouvir isso".

**R3 — "Perguntei pro Google" (C3), 25s** — tela do Modo IA buscando um serviço local; aponta quem apareceu e por quê; "comenta GOOGLE".

---

## 7. Fechar a análise com dados reais

1. **Apify (recomendado pela skill):** criar token grátis em console.apify.com, adicionar `APIFY_TOKEN` nas variáveis do ambiente e rodar `ig-audience-insights` para:
   - `fetch_profile("idea_lab7")` → seguidores, posts, bio atual;
   - `fetch_niche_posts` em `#iaparanegocios`, `#pequenosnegocios`, `#whatsappbusiness` → padrões que estão performando agora;
   - 3 concorrentes do nicho para benchmark.
2. **Insights do próprio perfil** (já existe token da Graph API na skill `post-instagram`): exportar alcance de não-seguidores, envios e salvamentos por post dos últimos 30 dias. Isso diz quais dos 25 posts repetir.
3. Revisar este plano em 14 dias com esses números.

---

### Fontes
- [Forbes — WhatsApp Business lança IA agêntica para PMEs](https://forbes.com.br/forbes-tech/2026/02/whatsapp-business-lanca-ia-agentica-para-pmes/)
- [Startups — Meta amplia IA para empresas com agentes no WhatsApp](https://startups.com.br/negocios/big-techs/meta-amplia-ia-para-empresas-com-agentes-integrados-ao-whatsapp/)
- [Digisac — Conversations 2026](https://www.digisac.com.br/blog/meta-conversations-2026)
- [Showmetech — Google for Brasil 2026](https://www.showmetech.com.br/google-for-brasil-2026/)
- [Conversion — AI Mode no Brasil](https://www.conversion.com.br/blog/ai-mode-brasil)
- [Metricool — Algoritmo do Instagram 2026](https://metricool.com/pt/algoritmo-instagram/)
- [Canaltech — 8 tendências para marcas no Instagram em 2026](https://canaltech.com.br/mercado/automacao-e-conteudo-autentico-8-tendencias-para-marcas-no-instagram-em-2026/)
- [Mundo do Marketing — 8 tendências](https://mundodomarketing.com.br/8-tendencias-que-devem-redefinir-conteudo-anuncios-e-vendas-no-instagram-em-2026)
- [Rafael Terra — 26 mudanças do algoritmo 2026](https://rafaelterra.com.br/?p=4736)
