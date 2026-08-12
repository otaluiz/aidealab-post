---
name: contexto-processo
description: Mapa do processo de fabricação de gelatina — etapas, variáveis por etapa, unidades, faixas típicas, linhas/produtos e envelope de segurança. Consultada por outras skills para validar se um achado é fisicamente plausível e para traduzir nome de variável em significado de processo. Não responde pergunta de dado; é a memória de engenharia da planta.
---

# Contexto do processo de gelatina

Esta skill não calcula nada. Ela existe para que o agente **fale a língua da
planta** e para que nenhuma conclusão estatística seja apresentada sem passar
pelo teste de plausibilidade física.

> **Regra de uso:** antes de afirmar que a variável X causa o efeito Y, procure o
> mecanismo aqui. Se não houver mecanismo conhecido, a relação é apresentada como
> correlação a investigar — nunca como causa.

---

## <<PREENCHER>> — substituir pelo processo real da planta

Todo o conteúdo abaixo marcado `[a validar]` é conhecimento geral da fabricação
de gelatina, **não da sua planta**. Substitua pelos dados reais antes de confiar
em qualquer análise. Enquanto estiver `[a validar]`, o agente deve mencionar isso
ao usar a informação.

```
<<PREENCHER: LINHAS E PRODUTOS>>
Linhas de produção:      ex. Linha 1 (tipo B, bovino), Linha 2 (tipo A, suíno)
Tipos de produto:        ex. gelatina tipo A, tipo B, colágeno hidrolisado
Faixas de Bloom alvo:    ex. 80-100, 150-180, 220-250
<<FIM>>

<<PREENCHER: UNIDADE DE ANÁLISE>>
Unidade padrão:          batelada de extração
Identificador:           ex. nº do lote / nº da batelada
Onde vive:               ex. condition "Batelada" na worksheet SEEQ <nome>
Etapas contínuas:        quais etapas não têm batelada e usam janela fixa
                         (hora/turno) em vez disso
<<FIM>>

<<PREENCHER: ENVELOPE DE SEGURANÇA>>
Para cada variável manipulável, informe:
  variável | mín operacional | máx operacional | taxa máx de variação | intertravamento
Ex: Temp. extração estágio 1 | 50 °C | 62 °C | 2 °C/h | bloqueio acima de 65 °C

Este bloco é usado hoje para a skill sugestao-setpoint recusar qualquer
recomendação fora de faixa. É o mesmo campo que uma futura camada de controle
consumirá como restrição dura. Não deixe em branco se for usar sugestão de
setpoint.
<<FIM>>
```

---

## Etapas da fabricação `[a validar]`

| # | Etapa | O que acontece | Regime |
|---|---|---|---|
| 1 | Recepção e preparo | Classificação e preparo da matéria-prima (ossada, pele) | Lote |
| 2 | Pré-tratamento | Tipo A: tratamento ácido. Tipo B: maceração alcalina em cal. Ossos: desmineralização ácida (osseína) | Batelada longa (dias a semanas) |
| 3 | Lavagem e neutralização | Remoção de reagente e ajuste de pH antes da extração | Batelada |
| 4 | **Extração multi-estágio** | Extração sequencial com temperatura crescente. Cada estágio gera um caldo | Batelada |
| 5 | Filtração / clarificação | Remoção de sólidos e turbidez | Contínuo |
| 6 | Deionização | Troca iônica; remoção de sais, queda de condutividade e cinzas | Contínuo |
| 7 | Concentração | Evaporação a vácuo até o teor de sólidos alvo | Contínuo |
| 8 | Esterilização | Tratamento térmico curto (UHT) | Contínuo |
| 9 | Gelificação e secagem | Gelificação, extrusão e secagem em leito com rampa de ar | Batelada/contínuo |
| 10 | Moagem e blend | Moagem, peneiramento e **mistura de lotes para padronizar Bloom/viscosidade** | Lote |

A etapa 4 é onde mora a maior parte da variabilidade de qualidade. A etapa 10 é a
que mais atrapalha rastreabilidade: o produto final é mistura, então o atributo do
produto embalado **não pertence a uma única batelada de extração**. Toda análise
que ligue processo a qualidade precisa saber em que ponto da cadeia a amostra foi
tirada.

## Variáveis-chave por etapa `[a validar]`

| Etapa | Variável | Unidade | Faixa típica |
|---|---|---|---|
| Pré-tratamento | pH do banho | — | ácido 1,5–3,0 / alcalino 12–12,5 |
| Pré-tratamento | tempo de maceração | dias | dias (tipo A) a semanas (tipo B) |
| Pré-tratamento | temperatura do banho | °C | ambiente a 25 |
| Extração | temperatura por estágio | °C | crescente, ~55 → 90 |
| Extração | tempo por estágio | h | 2–8 |
| Extração | pH do caldo | — | 4–6 |
| Extração | razão água/sólido | — | específica da planta |
| Concentração | teor de sólidos | % ou °Brix | até 30–45 |
| Concentração | temperatura / vácuo | °C / mbar | — |
| Secagem | temperatura do ar (entrada/saída) | °C | rampa |
| Secagem | umidade do ar | %UR | — |
| Secagem | tempo de residência | h | — |
| Deionização | condutividade | µS/cm | — |
| Produto | Bloom, viscosidade, umidade, cinzas, pH | g, mPa·s, %, %, — | por especificação |

## Unidade de análise

Padrão: **uma linha por batelada de extração**, com as fases delimitadas pelas
conditions do SEEQ. Em etapa contínua sem batelada (filtração, deionização,
concentração), a unidade é uma **janela fixa** — hora ou turno — declarada no
bloco `<<PREENCHER>>`.

Estratificação obrigatória em qualquer análise: **linha** e **tipo de produto**.
São processos diferentes rodando no mesmo histórico; misturá-los produz
correlação espúria com muita facilidade.

## Confundidores conhecidos `[a validar]`

Em ordem de força típica:

1. **Matéria-prima** — origem, tipo, idade do animal, fornecedor, lote. Costuma
   ser a maior fonte de variabilidade basal de Bloom e rendimento, e raramente
   está bem registrada. Se não estiver no dado, é confundidor não controlado e
   isso precisa ser dito.
2. **Estágio de extração** — comparar caldos de estágios diferentes sem separar é
   erro grosseiro: Bloom e rendimento variam por construção entre estágios.
3. **Linha e tipo de produto** — ver acima.
4. **Campanha / sazonalidade** — mudança de receita, de fornecedor ou de estação
   aparece como "tendência" que não é do processo.
5. **Blend** — o atributo do produto acabado é média ponderada de vários lotes.

## Mecanismos causais

O mapa de relações conhecidas — incluindo o trade-off central entre rendimento e
Bloom na extração — está em [references/mapa-causal.md](references/mapa-causal.md).
Consulte-o sempre que precisar julgar se um achado estatístico faz sentido físico.

## O que reportar sempre

- Ao usar qualquer informação ainda marcada `[a validar]`, dizer que é
  conhecimento geral do setor e não a realidade confirmada da planta.
- Ao propor mecanismo causal, citar qual relação do mapa causal o sustenta.
- Se a análise cruzar linhas, tipos de produto ou estágios de extração sem
  estratificar, sinalizar como risco de confundimento antes de apresentar o
  resultado.
