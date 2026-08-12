---
name: analise-viscosidade
description: Análise de viscosidade da gelatina — o que influencia, previsão, comparação com histórico. Dispara por pedido do engenheiro sobre viscosidade. Delega modelagem para modelo-preditivo, causa para analise-causa-raiz e otimização para sugestao-setpoint.
---

# Análise de viscosidade

Skill fina: o que é específico da viscosidade fica aqui, o método vem de outras
skills.

## <<PREENCHER>>

```
<<PREENCHER: MÉTODO DE ENSAIO>>
Método usado:             [ex: viscosímetro capilar / rotacional, condição
                           padrão de medição]
Condições de referência:   [temperatura e concentração da solução de teste —
                           CRÍTICO: viscosidade só é comparável entre amostras
                           medidas nas mesmas condições]
Repetibilidade/incerteza:  [preencher]
Ponto de amostragem:       [pré-blend / produto final]
<<FIM>>

<<PREENCHER: VARIÁVEIS SUSPEITAS>>
1. [ex: grau de degradação térmica acumulada — concentração/esterilização]
2. [ex: peso molecular médio das cadeias, se houver proxy de processo]
3. [ex: estágio de extração de origem]
<<FIM>>
```

## Quando usar

"Por que a viscosidade caiu", "dá pra prever viscosidade", "o que mais
influencia viscosidade".

## Dados necessários

Tabela canônica com coluna de viscosidade **e a condição de medição
declarada** (temperatura, concentração da solução testada). Sem isso, valores de
fontes/datas diferentes podem não ser comparáveis entre si.

## Variáveis suspeitas `[a validar]`

1. Degradação térmica acumulada ao longo do processo — concentração e
   esterilização, não só extração (mecanismo 3 do mapa causal: calor excessivo
   na concentração degrada mesmo caldo bem extraído).
2. Estágio de extração de origem — viscosidade, como Bloom, varia por
   construção entre estágios.
3. Tempo total de processo em temperatura elevada (soma de exposições, não só
   pico).

## Armadilhas específicas da viscosidade

- **Dependência de temperatura e concentração da própria leitura.** Viscosidade
  medida em condições de teste diferentes não é a mesma grandeza — confirmar
  que todas as amostras comparadas usam a mesma condição de medição antes de
  qualquer análise.
- **Correlaciona-se com Bloom mas não é a mesma coisa** — ambos refletem
  tamanho de cadeia, mas por mecanismos de medição diferentes; não assumir que
  o que explica Bloom explica viscosidade na mesma magnitude sem checar.
- **Degradação é acumulativa ao longo de todo o processo**, não só da extração
  — analisar isoladamente a etapa de extração pode perder o efeito de
  concentração/esterilização.

## Procedimento

1. Pergunta de **previsão ou influência**: invocar `modelo-preditivo`, alvo =
   viscosidade, incerteza = a preenchida acima.
2. Pergunta de **causa de queda/variação**: invocar `analise-causa-raiz`.
3. Pergunta de **otimização**: invocar `sugestao-setpoint`.
4. Pergunta de **comparação com padrão**: invocar `perfil-processo`.

## O que reportar sempre

- Condição de medição (temperatura, concentração) usada para os valores
  analisados.
- Se etapas pós-extração (concentração, esterilização) foram incluídas na
  análise — omiti-las é a armadilha mais provável aqui.
