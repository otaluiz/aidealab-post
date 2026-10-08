# O que precisa melhorar — @idea_lab7 (08/10/2026)

Base: dados reais da Graph API (`automation/cloud/estado-instagram.json`) + revisão dos carrosséis.
Marcar `[x]` quando resolver.

## 1. Perfil (fazer esta semana, no app)
- [ ] **NAME:** trocar `AIdea Lab 🤖` por `aidealab · IA pro seu negócio` (29 caracteres, campo que a busca lê).
- [ ] **Bio:** hoje é lista de serviços com 5 emojis. Trocar por (129 car.):
      `IA que o pequeno negócio usa amanhã de manhã.` / `Atendimento, conteúdo e vendas no automático.` / `👇 Diagnóstico grátis do seu Instagram`
- [ ] **Link:** 3 cliques em 28 dias. Apontar direto para o WhatsApp com mensagem pronta ("Quero o diagnóstico grátis").
- [ ] **Destaques:** Comece aqui · Antes/depois · IA no zap · Dúvidas · Fale com a gente.
- [ ] **Grid:** arquivar os posts da série de história do design e os de 2025 fora do nicho (Ranch Sorting, "Da ideia à tela"), para os 9 de cima falarem só com dono de negócio.
- [ ] **Fixar 3:** whatsapp-ganhou-ia (útil), manifesto "Para quem é a aidealab" (criar) e o melhor Reel quando existir.
- [ ] Decidir o @: manter `@idea_lab7` ou migrar para `@aidealab` (se livre). Se migrar, trocar `handle` em `design-system/tema/tema.json` e re-renderizar.

## 2. Conteúdo
- [ ] **Sem Reels desde 2025.** Os Reels antigos alcançaram 254–493 contas; os carrosséis novos, 12–79. Sem Reels o perfil não chega a quem não segue. Meta: 3 Reels/semana (ver `campanha-seguidores.md`).
- [ ] **0 salvamentos e 1 envio em 15 posts.** Todo post precisa de um motivo para salvar (checklist, passo a passo) ou enviar ("manda pra quem...").
- [ ] **Nicho misturado.** Parar posts para designer (estilos, fontes, sites de referência). Público é dono de pequeno negócio.
- [ ] **Abertura genérica de agência** ("Entra: processo manual...", "Na aidealab, ...") foi o pior desempenho. Abrir sempre com a cena do cliente.
- [ ] **Oferta em sequência** (Dias 19–21, três posts de serviços seguidos). Máximo 1 oferta a cada 5 posts.
- [ ] Rotina gera só carrossel → criar rotina de Reels (roteiro + tela gravada ou personagem falando).

## 3. Carrosséis e engine
- [x] Handle errado no rodapé (`@aidealab7`) corrigido no tema para `@idea_lab7`; os 4 rascunhos do motor novo foram re-renderizados.
- [x] Palavras escondidas atrás do personagem/objeto corrigidas (perfil-google capa, slide 2 e CTA; pergunta-do-cliente capa; whatsapp-ganhou-ia capa).
- [x] `upload_carrosseis.py` agora atualiza no Drive os rascunhos já existentes em 04 quando o PNG muda (antes pulava a pasta).
- [ ] **Carrosséis já aprovados em `06-Aprovados-para-Postar/FILA` feitos pelo motor antes de 08/10 ainda têm `@aidealab7` no rodapé.** As imagens-fonte deles não estão no repositório, então não dá para re-renderizar daqui. Conferir no Drive antes de postar; se tiver o handle errado, mover de volta para 04 com as fotos originais para re-render.
- [ ] perfil-google-parado, slide 7: a linha "a aidealab revisa com você" cai sobre a camiseta clara e perde contraste. Melhorar na engine: fundo/halo automático no texto de apoio do CTA quando a área for clara.
- [ ] Capa: o título atrás da cabeça só funciona com folga acima do personagem. A rotina já pede "generous headroom"; quando o `compor.py` não achar espaço, refazer a foto (custou 1 regeração no whatsapp-ganhou-ia).
- [ ] Repetição visual: 3 carrosséis seguidos com a mesma estrutura (T1-T2-T3-T2-T3-T2c-T4). Variar a sequência e usar T5 (referência) e diagrama quando couber.

## 4. Medição
- [ ] Rever metas em 22/10 comparando `conta_28d` com a base: alcance 342, visitas 102, cliques 3, 443 seguidores.
- [ ] `ig_insights.py` não traz seguidores ganhos por dia (`follows_and_unfollows` veio vazio). Acompanhar `followers_count` diário pelo histórico do `estado-instagram.json` no git.
