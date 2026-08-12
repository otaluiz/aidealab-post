---
name: alarmes-e-limites
description: Deriva limite de alarme para uma variável de processo a partir do histórico — não de opinião — com taxa de falso alarme e antecedência de detecção, entregando a especificação pronta para virar condition/fórmula no SEEQ. Invocada por outras skills ou por pedido direto de proposta de alarme.
---

# Alarmes e limites

Todo limite proposto aqui vem do dado, e vem acompanhado do custo de propô-lo: a
taxa de falso alarme que ele geraria no histórico. Um limite sem essa contrapartida
não é entregável por esta skill.

## Quando usar

"Propõe um alarme para temperatura de extração", "esse limite atual está bom ou
gera alarme demais?", ou invocada depois de `analise-causa-raiz` identificar uma
variável associada a resultado ruim.

## Dados necessários

Tabela canônica de `dados-processo` com a variável de interesse e o desfecho que
o alarme deveria antecipar (ex: batelada fora de especificação de Bloom). **n
mínimo: histórico com pelo menos alguns casos do desfecho indesejado** — sem
nenhum caso ruim no histórico, não há como estimar taxa de detecção, só banda de
normalidade (que é uma entrega diferente, mais fraca).

## Procedimento

1. **Definir o desfecho a antecipar** — fora de especificação, degradação de
   Bloom, etc. — e o horizonte de antecedência desejado (alarme durante o
   estágio 1 para evitar problema que só se confirma no estágio 3, por exemplo).

2. **Varrer limites candidatos** para a variável e, para cada um, calcular no
   histórico:
   - **taxa de falso alarme** — fração de bateladas boas que teriam disparado;
   - **antecedência média de detecção** — quanto tempo antes do desfecho o
     alarme teria soado, nas bateladas ruins que de fato dispararam;
   - **taxa de detecção** — fração de bateladas ruins que o limite pega.

3. **Escolher o ponto de operação** no trade-off detecção × falso alarme —
   apresentar 2-3 opções (conservador/balanceado/agressivo), não só uma escolha
   unilateral, porque o custo operacional do falso alarme é decisão de quem vai
   conviver com ele.

4. **Entregar como especificação pronta**: variável, limite, janela de avaliação
   (instantâneo ou sustentado por X minutos), e um template de condition/fórmula
   SEEQ para o engenheiro implantar.

Código de referência para os passos 2–3: [references/avaliacao-limite.md](references/avaliacao-limite.md).

## O que reportar sempre

- Taxa de falso alarme e antecedência média de detecção, sempre juntas — nunca
  um limite sem essas duas.
- n de bateladas boas e ruins usadas na varredura.
- As opções no trade-off, não só a recomendada.
- Que a implantação é responsabilidade do engenheiro — a skill entrega a
  especificação, não ativa o alarme.
