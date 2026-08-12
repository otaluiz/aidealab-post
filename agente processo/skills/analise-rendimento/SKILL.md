---
name: analise-rendimento
description: Análise de rendimento do processo de extração de gelatina — o que influencia, previsão, comparação entre linhas/campanhas. Dispara por pedido do engenheiro sobre rendimento. Delega modelagem para modelo-preditivo, causa para analise-causa-raiz e otimização para sugestao-setpoint.
---

# Análise de rendimento

Skill fina: o que é específico do rendimento fica aqui, o método vem de outras
skills.

## <<PREENCHER>>

```
<<PREENCHER: DEFINIÇÃO E BASE DE CÁLCULO>>
Fórmula usada:            [ex: massa de gelatina seca / massa de matéria-prima
                           preparada — CONFIRMAR a base exata usada na planta,
                           é a fonte mais comum de divergência entre relatórios]
Onde é calculado hoje:     [Power BI / planilha manual / SEEQ]
Incerteza/repetibilidade:  [ex: balanço de massa com erro de fechamento de
                           ±X pp — importante para não modelar ruído de
                           medição de massa como se fosse efeito de processo]
Nível de agregação nativo: [por batelada / por dia / por campanha — confirmar
                           antes de tratar como "por batelada" por padrão]
<<FIM>>

<<PREENCHER: VARIÁVEIS SUSPEITAS>>
1. [ex: temperatura e tempo de extração, todos os estágios]
2. [ex: razão água/matéria-prima]
3. [ex: qualidade/idade da matéria-prima recebida]
<<FIM>>
```

## Quando usar

"Por que o rendimento caiu", "dá pra prever rendimento", "que variável mais
influencia rendimento", "compara rendimento entre linhas/campanhas".

## Dados necessários

Tabela canônica com coluna de rendimento e sua base de cálculo confirmada. Se a
base de cálculo não estiver clara (`<<PREENCHER>>` acima vazio), a skill deve
perguntar antes de comparar números — rendimento calculado com bases diferentes
não é comparável.

## Variáveis suspeitas `[a validar]`

1. Temperatura e tempo por estágio de extração — trade-off direto com Bloom
   (mecanismo 1 do mapa causal): condição mais agressiva tende a subir
   rendimento e descer Bloom.
2. Razão água/sólido na extração.
3. Qualidade e variabilidade da matéria-prima — maior confundidor não
   controlado tipicamente (ver `contexto-processo`, lista de confundidores).
4. Eficiência de cada estágio — rendimento por estágio individual, não só total.

## Armadilhas específicas do rendimento

- **Base de cálculo inconsistente entre fontes.** Power BI, planilha manual e
  cálculo de engenharia podem divergir na definição. Confirmar antes de juntar
  dados de fontes diferentes na mesma tabela canônica.
- **Matéria-prima é confundidor forte e raramente bem registrado.** Rendimento
  varia com qualidade/origem da matéria-prima independente do processo; sem essa
  variável na tabela, tratar qualquer modelo como sujeito a confundimento não
  controlado.
- **Nível de agregação nativo pode não ser por batelada** — se o indicador só
  existe agregado por dia ou campanha, isso limita a granularidade de qualquer
  causa-raiz ou modelagem; não desagregar artificialmente.

## Procedimento

1. Pergunta de **quanto**, sem "por quê": encaminhar para `consulta-dados` se o
   indicador já existir agregado no Power BI — não remontar do zero via SEEQ.
2. Pergunta de **previsão ou influência**: invocar `modelo-preditivo`, alvo =
   rendimento, incerteza = a preenchida acima.
3. Pergunta de **causa de queda/variação**: invocar `analise-causa-raiz`.
4. Pergunta de **otimização** (sozinho ou em trade-off com Bloom/outro
   atributo): invocar `sugestao-setpoint`.

## O que reportar sempre

- A base de cálculo do rendimento usada na análise.
- Se matéria-prima está ou não representada na tabela como controle.
- O nível de agregação real dos dados usados (batelada, dia, campanha).
