---
name: perfil-processo
description: Constrói o perfil de referência (golden batch) de uma linha/produto a partir do histórico de bateladas dentro de especificação, e calcula o desvio de uma batelada específica contra esse perfil. Invocada por outras skills ou por pedido direto para comparar uma batelada com o padrão esperado.
---

# Perfil de processo (golden batch)

Constrói um perfil médio de referência por fase e mede o quanto uma batelada
específica se desvia dele. Serve tanto para diagnóstico pontual ("essa batelada
está normal?") quanto como insumo para `alarmes-e-limites`.

## Quando usar

"Como está essa batelada comparada ao padrão?", "monta o perfil de referência da
Linha 2 para gelatina tipo B", ou invocada por `analise-causa-raiz` quando o
contraste bom/ruim se beneficia de um perfil já pronto.

## Dados necessários

Tabela canônica de `dados-processo`, estratificada por linha e tipo de produto
(perfis de processos diferentes não se misturam — ver `contexto-processo`).
**n mínimo recomendado: 15 bateladas dentro de especificação** para o perfil ser
estatisticamente estável; abaixo disso, apresentar como preliminar.

## Procedimento

1. **Selecionar o conjunto de referência**: bateladas da mesma linha e tipo de
   produto, dentro de especificação de qualidade (ou explicitamente as
   "melhores" se o pedido for um golden batch de excelência, não de normalidade).

2. **Alinhar temporalmente** — bateladas têm duração diferente entre si.
   Normalizar pelo **percentual de progresso da fase**, não pelo tempo absoluto,
   antes de calcular estatísticas ponto a ponto.

3. **Calcular perfil e banda**: mediana (mais robusta que média a outliers) e
   banda de tolerância (ex: percentil 10–90) por variável, em cada ponto da fase
   normalizada.

4. **Pontuar a batelada de interesse** contra o perfil: para cada variável,
   quanto ela sai da banda, agregando num score de desvio geral e apontando as
   variáveis que mais contribuem.

Código de referência: [references/alinhamento-perfis.md](references/alinhamento-perfis.md).

## O que reportar sempre

- Composição do conjunto de referência (n, linha, produto, critério de seleção).
- Se n está abaixo do mínimo recomendado, dizer que o perfil é preliminar.
- Variáveis com maior contribuição ao desvio, não só o score agregado.
- Se a batelada avaliada é de linha/produto diferente do perfil de referência —
  isso invalida a comparação e deve ser recusado, não aproximado.
