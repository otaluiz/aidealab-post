---
name: analise-causa-raiz
description: Investiga por que um resultado de processo saiu diferente do esperado — queda de Bloom, perda de rendimento, batelada fora de especificação. Contrasta bom versus ruim, detecta mudança de regime, e entrega hipóteses ranqueadas com o teste que confirmaria cada uma. Use quando a pergunta for "por quê" ou "o que causou", não para consulta de indicador.
---

# Análise de causa raiz

Esta skill responde **por quê**. Ela nunca afirma causa a partir de correlação
sozinha — toda hipótese é confrontada com o mecanismo em `contexto-processo` (se
disponível) e entregue com o teste que a confirmaria, não como veredito fechado.

## Quando usar

"Por que o Bloom caiu na campanha de junho?", "o que mudou entre a batelada boa
de terça e a ruim de quarta?", "essa queda de rendimento é sazonal ou é algo que
mudou no processo?". Se a pergunta for "quanto" em vez de "por quê", é
`consulta-dados`, não esta.

## Dados necessários

Tabela canônica de `dados-processo` cobrindo o período de interesse **e** um
período de referência para contraste (antes da mudança, ou bateladas "boas"
seguindo a mesma especificação). Sem período de contraste, a análise fica limitada
a descrever a distribuição, não a apontar causa candidata.

## Procedimento

1. **Definir o contraste**: bom vs. ruim, antes vs. depois, ou dentro da
   especificação vs. fora. Deixar explícito qual é o grupo de referência.

2. **Checar mudança de regime primeiro**, antes de procurar variável isolada:
   o efeito é um evento pontual, uma tendência gradual, ou um degrau associado a
   uma data específica (troca de fornecedor, manutenção, mudança de receita)?
   Cruzar com metadados de campanha/turno da tabela canônica.

3. **Comparar distribuições** de cada variável de processo entre os grupos —
   não só a média, também dispersão e outliers. Uma variável com média igual mas
   variância maior no grupo ruim já é pista.

4. **Ranquear hipóteses**, cada uma com:
   - a variável e a direção do efeito observado;
   - se há mecanismo conhecido em `contexto-processo`/mapa causal que sustente
     essa direção (se sim, hipótese sobe no ranking; se contradiz o mecanismo
     conhecido, desce e é sinalizada como possível confundidor);
   - **o teste que confirmaria** — ex: "se for isso, bateladas com temperatura
     de estágio 2 acima de X° deveriam mostrar o mesmo padrão em outras linhas
     também", ou "rodar uma batelada controlada variando só essa variável".

5. **Checar confundidores** da lista em `contexto-processo` (matéria-prima,
   estágio, linha/produto, campanha, blend) antes de declarar qualquer hipótese
   como líder.

Código de referência para os passos 2–3: [references/testes-contraste.md](references/testes-contraste.md).

## O que reportar sempre

- Qual foi o grupo de contraste usado e por quê.
- n de cada grupo — hipótese construída sobre poucas bateladas é dita como
  preliminar.
- Hipóteses em ordem de força, cada uma com o teste que a confirmaria — nunca
  uma única causa apresentada como fato.
- Qualquer contradição com o mapa causal conhecido, explicitada, não omitida.
- Confundidores não controlados no dado disponível.
