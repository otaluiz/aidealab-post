---
name: modelo-preditivo
description: Constrói e valida modelo preditivo de um atributo de qualidade a partir da tabela analítica canônica — baseline, split temporal, métrica em unidade de engenharia, comparação com incerteza de medição. Invocada pelas skills de atributo (analise-bloom, analise-rendimento etc.), não dispara diretamente por pedido genérico do usuário.
---

# Modelo preditivo

Esta skill é o método. Ela não sabe o que é Bloom ou umidade — recebe de quem a
invocou o nome do alvo, a incerteza de medição do alvo, e a tabela canônica (via
`dados-processo`). O que ela garante é rigor: nenhum modelo passa por aqui sem
baseline, sem validação temporal e sem confronto com o ruído da própria medição.

> **Regra de aceite:** um modelo só é apresentado como útil se bate o baseline
> **e** seu erro é menor que a incerteza de medição do alvo. Se qualquer um dos
> dois falhar, o resultado é "não há sinal utilizável aqui" — não a melhor
> tentativa disponível.

## Quando usar

Invocada por uma skill de atributo (`analise-bloom`, `analise-rendimento`,
`analise-viscosidade`, `analise-umidade`) quando o pedido é prever, estimar ou
entender o que mais influencia o atributo.

## Dados necessários

- Tabela canônica de `dados-processo`, já validada.
- **n mínimo recomendado: 40 unidades de análise** para qualquer modelo além de
  correlação simples; abaixo disso, reportar como exploratório e dizer
  explicitamente que o n é insuficiente para validação robusta.
- Incerteza/repetibilidade de medição do alvo, vinda da skill de atributo que
  invocou. Sem esse número, a skill deve pedir antes de concluir sobre
  capacidade preditiva.

Se code interpreter não estiver disponível, produzir a especificação abaixo
(alvo, features, split, método) para rodar no SEEQ Data Lab, e pedir o resultado
de volta para interpretar.

## Procedimento

1. **Definir o alvo e confirmar o ponto de amostragem** — pré-blend ou produto
   final (ver `contexto-processo`, "Blend × atributos do produto final"). Alvo
   pós-blend é sinal mais fraco; declarar isso na apresentação do modelo.

2. **Feature engineering** a partir da tabela canônica: agregações por fase já
   existem; considerar também lag por tempo de residência entre etapas (ex: o
   efeito da extração na umidade final passa por várias horas de processo
   intermediário) e razões entre variáveis quando fizer sentido de processo
   (ex: razão água/sólido).

3. **Baseline obrigatório** antes de qualquer modelo: média do alvo (ou média
   por linha/produto, se estratificação for relevante). Todo modelo é comparado
   contra isso.

4. **Split temporal — nunca aleatório.** Ordenar por tempo, treinar no passado,
   validar no futuro (ex: 70/30 cronológico, ou validação em blocos). Split
   aleatório vaza informação de bateladas vizinhas (mesma campanha, mesmo
   fornecedor) e infla a métrica artificialmente.

5. **Modelar**, do mais simples ao mais complexo, só avançando se o anterior não
   for suficiente: regressão linear/regularizada → PLS (útil com muitas
   variáveis de processo correlacionadas entre si) → random forest / gradient
   boosting (se houver n suficiente e suspeita de não-linearidade).

6. **Métrica em unidade de engenharia** (RMSE em g de Bloom, não R² sozinho).
   Comparar：
   - contra o baseline (deve ser melhor, com margem, não só numericamente);
   - contra a incerteza de medição do alvo (deve ser menor — regra de aceite).

7. **Interpretar**, não só prever: importância de variáveis e, se possível,
   dependência parcial das 2-3 mais importantes. Confrontar o sinal do efeito
   com `contexto-processo`/mapa causal — efeito na direção oposta ao mecanismo
   conhecido é bandeira vermelha, não descoberta.

Código de referência para os passos 3–7: [references/receita-modelagem.md](references/receita-modelagem.md).

## O que reportar sempre

- n usado, período coberto, linhas descartadas (herdado de `dados-processo`).
- Baseline e métrica do modelo, lado a lado.
- Métrica do modelo vs. incerteza de medição do alvo — explícito, não implícito.
- Variáveis mais importantes e se o sinal delas bate com o mecanismo conhecido.
- Se o modelo não superou o baseline ou não bateu a incerteza de medição: dizer
  isso claramente como conclusão, não enterrar em rodapé.
- Se estava em modo degradado (sem code interpreter): que a saída é uma
  especificação para rodar no SEEQ Data Lab, não um resultado calculado.
