# Gabarito — skill de análise de atributo novo

Use este gabarito para criar uma skill `analise-<atributo>` nova (ex: cor,
cinzas, pH final) sem reescrever o método — o método já existe em
`modelo-preditivo`, `analise-causa-raiz`, `perfil-processo`, `sugestao-setpoint`.
O que esta skill nova precisa fazer é só o que é específico do atributo.

Copie a estrutura, preencha os colchetes, e crie `analise-<atributo>/SKILL.md`.

```markdown
---
name: analise-<atributo>
description: Análise de <atributo> da gelatina — o que influencia, previsão, comparação com histórico. Dispara por pedido do engenheiro sobre <atributo>. Delega modelagem para modelo-preditivo, causa para analise-causa-raiz e otimização para sugestao-setpoint.
---

# Análise de <atributo>

Skill fina: o que é específico do <atributo> fica aqui, o método vem de outras
skills.

## <<PREENCHER>>

\`\`\`
<<PREENCHER: MÉTODO DE ENSAIO>>
Método usado:             [método de laboratório ou instrumento]
Repetibilidade/incerteza:  [número — decide se qualquer modelo é útil]
Ponto de amostragem:       [pré-blend / produto final]
Condições de medição:      [se relevante — ex: temperatura de referência]
<<FIM>>

<<PREENCHER: VARIÁVEIS SUSPEITAS>>
Em ordem de prioridade:
1. [variável de processo mais provável]
2. [...]
3. [...]
<<FIM>>
\`\`\`

## Quando usar

[Perguntas típicas sobre este atributo]

## Dados necessários

Tabela canônica com coluna de <atributo> e a incerteza de medição preenchida
acima.

## Variáveis suspeitas `[a validar]`

[Se houver mecanismo conhecido, referenciar
contexto-processo/references/mapa-causal.md; senão, declarar que é hipótese
sem mecanismo confirmado.]

## Armadilhas específicas do <atributo>

[O que costuma dar errado especificamente nesta análise — medição, confundidor,
ponto de amostragem.]

## Procedimento

1. Pergunta de **previsão ou influência**: invocar `modelo-preditivo`.
2. Pergunta de **causa de desvio**: invocar `analise-causa-raiz`.
3. Pergunta de **otimização**: invocar `sugestao-setpoint`.
4. Pergunta de **comparação com padrão**: invocar `perfil-processo`.

## O que reportar sempre

- A incerteza de medição junto com qualquer resultado de modelo.
- [Outros itens específicos do atributo.]
```
