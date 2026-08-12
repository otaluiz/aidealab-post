---
name: consulta-dados
description: Responde perguntas factuais e agregadas sobre indicadores de produção — "quanto", "quando", "qual foi" — direto da base relacional (Power BI publicado, tabelas do SharePoint), sem acionar modelagem. Use para consultas diretas de indicador, comparação de período ou de linha. Não use para "por quê" — isso é análise de causa raiz.
---

# Consulta de dados

Esta skill responde **o quanto**, não **o porquê**. É o caminho rápido para uma
pergunta que a base relacional já resolve — sem puxar série do SEEQ, sem
modelagem, sem code interpreter.

## Quando usar

Perguntas do tipo: "qual o rendimento médio de junho na Linha 1?", "quantas
bateladas fora de especificação tivemos essa semana?", "como está o Bloom médio
comparado ao mês passado?".

**Quando escalar em vez de responder aqui:** se a pergunta for "por que caiu",
"o que está causando", "qual variável influencia" — isso é
`analise-causa-raiz` ou a skill de atributo relevante (`analise-bloom` etc.),
não uma consulta. Um sinal claro: se a resposta exige olhar variável de
processo (SEEQ) e não só indicador já calculado, não é mais consulta.

## Dados necessários

Pelo menos uma fonte registrada em `dados-processo/references/fontes.md` com
alias `MODELO_BI` ou `TABELA_SHAREPOINT` cobrindo o indicador pedido. Se não
houver fonte registrada para o indicador, dizer isso — não estimar a partir de
outro dado.

## Procedimento

1. **Identificar entidade, recorte e período** da pergunta: qual indicador, qual
   linha/produto, qual janela de tempo. Se período não for claro, perguntar
   antes de assumir "tudo" ou "mês corrente".
2. **Escolher a fonte, nesta ordem:**
   - `MODELO_BI` (semantic model Power BI publicado) — indicador já agregado e
     validado, é a fonte primária para consulta.
   - `TABELA_SHAREPOINT` — quando o indicador não está no modelo publicado mas
     existe como planilha (ex: input manual recente).
   - Nunca ler `.pbix` diretamente — não é fonte de dado (ver
     `dados-processo/SKILL.md`, "Regra sobre Power BI e `.pbix`"). Se o
     indicador só existir lá, dizer que precisa ser publicado ou exportado.
3. **Responder com a fonte declarada**: valor, período coberto, fonte usada e,
   se disponível, data de última atualização do dado.
4. **Nunca misturar granularidades sem avisar** — comparar um agregado diário do
   modelo com uma leitura pontual de planilha manual é comparação inválida a
   menos que explicitamente normalizada e declarada.

## O que reportar sempre

- Fonte exata do número (nome da tabela/relatório), não só "o Power BI disse".
- Período e recorte (linha, produto) realmente cobertos pela resposta.
- Se o dado está desatualizado ou parcial para o período pedido.
- Se a pergunta na verdade pede explicação causal, dizer que vai encaminhar para
  a skill de análise apropriada em vez de forçar uma resposta numérica sem
  contexto.
