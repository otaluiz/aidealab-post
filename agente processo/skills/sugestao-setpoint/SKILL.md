---
name: sugestao-setpoint
description: Propõe faixa de setpoint para uma ou mais variáveis manipuláveis, otimizando um ou mais atributos de qualidade sob restrição do envelope operável observado. Sempre entrega faixa, nunca valor único, e sempre como recomendação para validação do engenheiro. Invocada por skills de atributo ou por pedido direto de otimização.
---

# Sugestão de setpoint

Esta é a skill com maior potencial de dano se usada sem disciplina: uma sugestão
de setpoint mal fundamentada pode ser levada a campo. As regras abaixo não são
sugestões de estilo — são condição para a skill operar.

> **O agente não atua em controle.** Esta skill produz uma recomendação
> estruturada para avaliação humana. Nunca escreve em sistema de controle, nunca
> orienta o usuário a aplicar automaticamente, e nunca omite que é recomendação
> sujeita a validação e às restrições de segurança do processo.

## Quando usar

"Que temperatura de extração maximiza rendimento sem perder Bloom?", "qual o
melhor pH de pré-tratamento para essa matéria-prima?". Envolve trade-off entre
pelo menos um objetivo de qualidade e uma variável manipulável.

## Dados necessários

- Tabela canônica de `dados-processo`, cobrindo variação suficiente da(s)
  variável(is) manipulável(is) — sem variação histórica real na variável, não há
  base para recomendar mudança nela.
- **Envelope de segurança** de `contexto-processo` (`<<PREENCHER>>`: mín/máx
  operacional, taxa máxima de variação, intertravamentos). Sem envelope
  preenchido, a skill deve recusar-se a propor faixa e explicar por quê.
- Modelo do(s) atributo(s) de qualidade, via `modelo-preditivo` (chamado por esta
  skill ou já disponível de uma análise anterior).

## Procedimento

1. **Confirmar o envelope de segurança** para cada variável envolvida. Se
   ausente ou incompleto, parar aqui e pedir o preenchimento — não inferir
   limites a partir do próprio histórico de operação (histórico não é o mesmo
   que limite de segurança).

2. **Delimitar o envelope operável observado**: a região dos dados onde há
   suporte real (ex: percentil 5–95 das combinações já praticadas), que é
   tipicamente mais estreita que o envelope de segurança. **A otimização busca
   só dentro desta região — nunca fora dela**, mesmo que o envelope de segurança
   permita, porque fora da região observada não há dado que sustente a predição
   do modelo.

3. **Rodar a otimização** (grade ou busca simples) dentro do envelope operável,
   usando o(s) modelo(s) de `modelo-preditivo` para prever o impacto de cada
   combinação candidata nos objetivos envolvidos.

4. **Tratar trade-off multi-objetivo explicitamente** quando houver mais de um
   atributo (ex: Bloom × rendimento): apresentar a fronteira de opções, não um
   único ponto "ótimo" que esconde a escolha de peso entre objetivos — essa
   escolha é do engenheiro.

5. **Montar a recomendação no formato estruturado** — nunca só em prosa. Ver
   contrato em [references/contrato-recomendacao.md](references/contrato-recomendacao.md).

6. **Registrar a recomendação emitida**, se houver onde registrar (ver
   [references/registro-recomendacoes.md](references/registro-recomendacoes.md)).
   Isso não é opcional por rigor científico: é o histórico que permite, no
   futuro, avaliar se as recomendações desta skill realmente funcionaram.

Código de referência para os passos 2–4: [references/otimizacao-restrita.md](references/otimizacao-restrita.md).

## O que reportar sempre

- Faixa, nunca valor único, com impacto esperado e sua incerteza.
- Que a recomendação está dentro do envelope operável observado — e se algo do
  que o usuário pediu cairia fora dele, dizer isso em vez de extrapolar.
- Trade-off explícito quando multi-objetivo: o que se ganha e o que se cede.
- Que é recomendação sujeita a validação do engenheiro e às restrições de
  segurança do processo — em toda resposta, não só na primeira.
- Se o envelope de segurança não estava preenchido, isso impediu a análise.

## Nota para a fase de controle (futuro)

Esta skill já produz o contrato de recomendação e o registro que uma futura
camada de controle (supervisório ou malha fechada) consumiria — ver
`skills/_controle-futuro/ROADMAP.md`. Nada aqui aciona controle: o alias
`ESCRITA_SETPOINT` está reservado e não é chamado por esta skill nesta fase.
