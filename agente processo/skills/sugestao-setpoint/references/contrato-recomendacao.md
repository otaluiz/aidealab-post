# Contrato da recomendação de setpoint

Toda saída de `sugestao-setpoint` segue esta estrutura — em prosa para o
engenheiro ler, mas com estes campos sempre presentes e identificáveis. Este
formato é deliberadamente o mesmo que uma futura camada de controle consumiria
como payload (ver `skills/_controle-futuro/ROADMAP.md`): o que muda entre a fase
consultiva atual e uma fase de controle futura é o destino do contrato, não a
sua forma.

## Campos

```
variavel:              nome da variável manipulável recomendada
valor_atual:            ponto de operação atual/típico, se conhecido
faixa_recomendada:      [min, max] — nunca um único valor
unidade:                unidade de engenharia
horizonte_aplicacao:    a que se aplica (ex: próxima batelada, próxima campanha
                         da mesma matéria-prima) — não é válido indefinidamente
objetivo(s):            atributo(s) que a recomendação busca melhorar
impacto_esperado:       valor esperado ± incerteza, por objetivo
trade_off:              o que se cede em outro objetivo, se houver
restricoes_ativas:      quais limites do envelope de segurança/operável
                         restringiram a busca (para transparência)
envelope_usado:         [min, max] efetivamente varrido — para auditoria
confianca:               qualitativa (baixa/média/alta), function de n e de
                         quão perto a faixa está da borda do envelope observado
n_suporte:               quantas bateladas sustentam a região recomendada
validade:                até quando a recomendação é razoável assumir válida
                         (processo muda; matéria-prima muda)
status:                  sempre "recomendação — requer validação do engenheiro"
```

## Exemplo preenchido

```
variavel:              Temperatura estágio 2 de extração — Linha 1
valor_atual:            72 °C
faixa_recomendada:      [74, 77] °C
unidade:                °C
horizonte_aplicacao:    próximas bateladas de gelatina tipo B, mesma
                         matéria-prima (couro bovino, fornecedor atual)
objetivo(s):            rendimento (maximizar), Bloom (manter >= 200 g)
impacto_esperado:        rendimento: +1.8 pp ± 0.9 pp
                         Bloom: -6 g ± 4 g (permanece acima do piso de 200 g)
trade_off:               ganho de rendimento custa parte da margem de Bloom
restricoes_ativas:       envelope operável observado (78 °C é o máximo com
                         suporte de dado suficiente; envelope de segurança
                         permitiria até 82 °C mas sem histórico ali)
envelope_usado:          [65, 78] °C
confianca:                média (faixa recomendada perto da borda superior do
                         envelope observado — poucas bateladas acima de 76 °C)
n_suporte:                34 bateladas
validade:                enquanto matéria-prima e receita de pré-tratamento
                         não mudarem; revalidar se qualquer um mudar
status:                  recomendação — requer validação do engenheiro e
                         verificação contra o envelope de segurança da planta
                         antes de qualquer aplicação
```
