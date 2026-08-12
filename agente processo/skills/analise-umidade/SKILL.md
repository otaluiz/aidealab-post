---
name: analise-umidade
description: Análise de umidade final da gelatina — o que influencia, previsão a partir dos parâmetros de secagem, comparação com histórico. Dispara por pedido do engenheiro sobre umidade. Delega modelagem para modelo-preditivo, causa para analise-causa-raiz e otimização para sugestao-setpoint.
---

# Análise de umidade

Skill fina: o que é específico da umidade fica aqui, o método vem de outras
skills. Entre os quatro atributos, é tipicamente o mais previsível a partir do
processo — mas também o mais sensível a um erro de alinhamento temporal
específico (ver armadilha abaixo).

## <<PREENCHER>>

```
<<PREENCHER: MÉTODO DE ENSAIO>>
Método usado:             [ex: estufa / Karl Fischer / balança de infravermelho]
Repetibilidade/incerteza:  [preencher]
Atraso amostragem-resultado: [horas entre coleta e resultado disponível]
<<FIM>>

<<PREENCHER: ATRASO SECAGEM-AMOSTRAGEM>>
Tempo típico entre fim da secagem e coleta da amostra de laboratório:
  [preencher — CRÍTICO para esta skill, ver armadilha abaixo]
Se variável (não constante), como varia:
  [ex: depende do turno, da fila de produção]
<<FIM>>

<<PREENCHER: VARIÁVEIS SUSPEITAS>>
1. [ex: temperatura do ar de secagem, entrada e saída]
2. [ex: umidade do ar de entrada]
3. [ex: tempo de residência no secador]
4. [ex: espessura do leito/fita]
<<FIM>>
```

## Quando usar

"Por que a umidade saiu fora de especificação", "dá pra prever umidade a partir
da secagem", "o que mais influencia umidade final".

## Dados necessários

Tabela canônica com coluna de umidade e, essencial aqui mais que nos outros
atributos, o **timestamp de fim de secagem e o timestamp da amostragem** —
ambos, não só a data do resultado de laboratório.

## Variáveis suspeitas `[a validar]`

Do mapa causal (mecanismo 5): temperatura do ar, umidade do ar de entrada,
tempo de residência e espessura do leito são preditores diretos e é o
mecanismo mais bem compreendido dos quatro atributos.

## Armadilhas específicas da umidade

- **Atraso entre secagem e amostragem.** A umidade medida pode refletir
  equilíbrio higroscópico atingido horas depois da secagem, não o estado no fim
  do secador. Se esse atraso não for conhecido e constante, ele é a primeira
  suspeita para erro de modelo — checar antes de suspeitar de variável de
  processo (ver mapa causal, mecanismo 5).
- **Sensibilidade à umidade do ar de entrada**, que varia com estação/clima —
  se essa variável não estiver na tabela, é confundidor não controlado
  plausível para variação sazonal aparente.
- **Espessura do leito/fita** muda o tempo de secagem efetivo mesmo com mesma
  configuração de temperatura — se não registrada, perda de variável relevante.

## Procedimento

1. Antes de qualquer modelagem: confirmar o atraso secagem-amostragem está
   preenchido e, se variável, incluído como feature (ex: hora do dia, turno,
   fila).
2. Pergunta de **previsão ou influência**: invocar `modelo-preditivo`, alvo =
   umidade, incerteza = a preenchida acima.
3. Pergunta de **causa de desvio**: invocar `analise-causa-raiz`, priorizando o
   atraso de amostragem como primeira hipótese a descartar.
4. Pergunta de **otimização de parâmetro de secagem**: invocar
   `sugestao-setpoint`.

## O que reportar sempre

- O atraso secagem-amostragem assumido na análise, e se é conhecido ou
  estimado.
- Se a umidade do ar de entrada (fator sazonal) foi incluída ou está ausente.
