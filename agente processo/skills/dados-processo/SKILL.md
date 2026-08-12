---
name: dados-processo
description: Extração, junção e checagem de qualidade dos dados de processo (SEEQ), laboratório (SharePoint) e agregados (Power BI), reduzidos à tabela canônica por batelada. Invocada por outras skills antes de qualquer análise ou modelagem — não dispara por fala direta do usuário.
---

# Dados de processo

Todas as skills de análise e modelagem partem da mesma tabela: **uma linha por
batelada** (ou por janela fixa, em etapa contínua — ver
[contexto-processo](../contexto-processo/SKILL.md)). Esta skill é a única que
conhece as fontes reais; as demais só recebem a tabela pronta.

> Se `contexto-processo` estiver disponível, use a definição de unidade de
> análise e o registro de linhas/produtos de lá. Se não estiver, pergunte ao
> usuário qual é a unidade de análise antes de prosseguir.

## Quando usar

Invocada por outra skill (`modelo-preditivo`, `analise-causa-raiz`,
`perfil-processo`, `alarmes-e-limites`, `sugestao-setpoint`, `analise-*`,
`consulta-dados`) sempre que for preciso montar ou atualizar a tabela canônica.
Não é para disparar diretamente por pedido em linguagem natural.

## Dados necessários

- Pelo menos uma fonte de série de processo (`SERIE_PROCESSO`) e uma fonte de
  laboratório (`TABELA_SHAREPOINT`) registradas em
  [references/fontes.md](references/fontes.md).
- Mapeamento de aliases preenchido em
  [references/ferramentas.md](references/ferramentas.md).

Se `fontes.md` ou `ferramentas.md` não estiverem preenchidos, pare e diga ao
usuário que a fonte de dado não está configurada — não adivinhe worksheet, nome
de coluna ou caminho de arquivo.

## Procedimento

1. **Confirmar unidade de análise e período** com quem invocou (batelada, linha,
   produto, janela de tempo).
2. **Puxar série de processo** via `SERIE_PROCESSO`, respeitando o contrato e o
   limite de linhas descritos em [references/ferramentas.md](references/ferramentas.md).
   Se o período exceder o limite por chamada, fatiar e agregar incrementalmente —
   nunca truncar em silêncio.
3. **Delimitar por batelada** usando as conditions/capsules retornadas. Sem
   capsule disponível, usar a janela fixa definida em `contexto-processo`.
4. **Agregar por fase**: para cada variável de processo, dentro de cada fase da
   batelada, calcular média, desvio-padrão, mínimo, máximo, tempo acima/abaixo de
   limiar relevante e taxa de variação. Código de referência em
   [references/tabela-canonica.md](references/tabela-canonica.md).
5. **Puxar laboratório** via `TABELA_SHAREPOINT` e juntar pela chave de batelada
   definida em `fontes.md`. Se a chave não bater 1:1 (ex. blend, mistura de
   lotes), declarar isso — não forçar junção aproximada por data.
6. **Checar qualidade**: gap de dado, sinal congelado (variância zero na janela),
   valor fora de faixa física, batelada com fase incompleta. Linhas reprovadas
   são descartadas e contadas, não silenciosamente removidas.
7. **Devolver a tabela canônica** com: chave de batelada, timestamps de início/fim
   por fase, features de processo agregadas, atributos de laboratório, metadados
   (linha, tipo de produto, matéria-prima, turno) — e o relatório de qualidade
   (n bruto, n após filtro, motivos de descarte).

## O que reportar sempre

- Número de bateladas antes e depois da checagem de qualidade, e por que cada uma
  foi descartada.
- Período efetivamente coberto pelos dados (pode ser menor que o pedido).
- Qualquer truncamento de chamada à ferramenta de série, mesmo que contornado por
  fatiamento.
- Se a fonte de laboratório vier de produto após blend, avisar que o atributo não
  pertence a uma única batelada de extração.

## Referências

- [references/ferramentas.md](references/ferramentas.md) — aliases, contrato do
  SEEQ, regra do `.pbix`.
- [references/fontes.md](references/fontes.md) — registro de worksheets,
  tabelas e planilhas.
- [references/tabela-canonica.md](references/tabela-canonica.md) — código de
  agregação e junção.
