---
name: analise-bloom
description: Análise de Bloom (força de gel) da gelatina — o que influencia, previsão a partir do processo, comparação com histórico. Dispara por pedido do engenheiro sobre Bloom. Delega modelagem para modelo-preditivo, causa para analise-causa-raiz e otimização para sugestao-setpoint.
---

# Análise de Bloom

Skill fina: o que é específico do Bloom fica aqui, o método vem de outras
skills. Não recalcula estatística — orquestra.

## <<PREENCHER>>

```
<<PREENCHER: MÉTODO DE ENSAIO>>
Método usado:            [ex: BS 757 / GME / método interno]
Repetibilidade/incerteza: [ex: ± 15 g — este número decide se qualquer modelo
                           de Bloom é útil ou está competindo com ruído do
                           próprio ensaio. Preencher com o dado real do
                           laboratório antes de usar modelo-preditivo.]
Tempo de resposta:        [horas/dias entre amostragem e resultado disponível]
Ponto de amostragem:      [pré-blend / produto final — ver contexto-processo,
                           "Blend × atributos do produto final"]
<<FIM>>

<<PREENCHER: VARIÁVEIS SUSPEITAS>>
Em ordem de prioridade, as variáveis de processo mais associadas a Bloom nesta
planta (preencher com conhecimento do engenheiro ou após primeira análise):
1. [ex: temperatura do último estágio de extração]
2. [ex: tempo de pré-tratamento]
3. [ex: pH do caldo]
<<FIM>>
```

Até este bloco ser preenchido, a lista abaixo (marcada `[a validar]`) é usada
como ponto de partida, vinda do mapa causal geral do setor.

## Quando usar

Perguntas sobre Bloom: "por que caiu", "dá pra prever", "o que mais influencia",
"compara essa batelada com o histórico".

## Dados necessários

Tabela canônica com coluna de Bloom preenchida (via `dados-processo`) e a
incerteza de medição preenchida acima. Sem a incerteza, `modelo-preditivo` não
consegue aplicar o critério de aceite — a skill deve pedir esse número antes de
prosseguir para modelagem (não é necessário para consulta ou perfil descritivo).

## Variáveis suspeitas `[a validar]`

Do mapa causal (`contexto-processo/references/mapa-causal.md`):

1. Temperatura e tempo de cada estágio de extração — trade-off direto com
   rendimento (mecanismo 1).
2. Tempo e pH do pré-tratamento — relação não-linear, ótimo intermediário
   (mecanismo 2).
3. Tempo de residência e temperatura na concentração — degradação térmica
   adicional (mecanismo 3).
4. Estágio de extração de origem do caldo (Bloom varia por construção entre
   estágios — sempre estratificar).

## Armadilhas específicas do Bloom

- **Ruído do ensaio maior que o efeito buscado.** Se a repetibilidade é ±15 g e
  a hipótese em teste prevê efeito de 5 g, o dado não tem resolução para
  confirmar isso — dizer isso antes de tentar modelar.
- **Blend mistura o sinal.** Se só há medida pós-blend, o Bloom de uma batelada
  individual de extração fica diluído; preferir medida pré-blend quando
  existir.
- **Não misturar estágios de extração** como se fossem a mesma população —
  Bloom por estágio tem faixa própria.

## Procedimento

1. Se a pergunta pede **previsão ou entendimento de influência**: invocar
   `modelo-preditivo` com alvo = Bloom, incerteza de medição = a preenchida
   acima, e as variáveis suspeitas como ponto de partida de feature engineering.
2. Se a pergunta pede **por que um resultado específico saiu diferente**:
   invocar `analise-causa-raiz`.
3. Se a pergunta pede **que condição usar para atingir um Bloom alvo** (sozinho
   ou em trade-off com outro atributo): invocar `sugestao-setpoint`.
4. Se a pergunta pede **comparação com padrão**: invocar `perfil-processo`.

## O que reportar sempre

- A incerteza de medição do Bloom junto com qualquer resultado de modelo —
  nunca apresentar RMSE sem esse contraste ao lado.
- Estágio de extração e ponto de amostragem (pré/pós-blend) usados na análise.
- Se as variáveis suspeitas ainda estão `[a validar]`, dizer isso.
