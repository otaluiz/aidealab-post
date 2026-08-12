# Registro de recomendações

Schema sugerido para uma lista/tabela no SharePoint onde cada recomendação
emitida por `sugestao-setpoint` é registrada. Não é obrigatório para a skill
funcionar, mas sem este registro nenhuma avaliação futura de "essa recomendação
funcionou?" é possível — e é a base de dado que uma fase de controle exigiria
antes de sequer ser considerada (ver `skills/_controle-futuro/ROADMAP.md`).

## <<PREENCHER>>

```
<<PREENCHER: LOCALIZAÇÃO DO REGISTRO>>
Site/lista SharePoint:  [caminho, se você optar por criar esta lista]
Alias de ferramenta:     TABELA_SHAREPOINT
<<FIM>>
```

Se não preenchido, a skill segue funcionando normalmente — apenas sem
persistência do histórico de recomendações, e deve mencionar isso quando emitir
uma recomendação.

## Schema

| Campo | Tipo | Descrição |
|---|---|---|
| id_recomendacao | texto | identificador único |
| data_emissao | data/hora | quando a skill gerou a recomendação |
| variavel | texto | variável manipulável recomendada |
| valor_atual | número | ponto de operação no momento da recomendação |
| faixa_min / faixa_max | número | faixa recomendada |
| objetivo | texto | atributo(s) alvo |
| impacto_esperado | texto | valor ± incerteza declarado no contrato |
| n_suporte | número | n de bateladas que sustentaram a recomendação |
| confianca | texto | baixa/média/alta |
| avaliado_por | texto | engenheiro que revisou |
| decisao | texto | aplicada / aplicada com ajuste / rejeitada / pendente |
| data_decisao | data/hora | quando a decisão acima foi tomada |
| resultado_observado | texto/número | o que de fato aconteceu, quando souber |
| observacoes | texto livre | contexto adicional |

## Uso pela skill

Ao final do procedimento (passo 6 do `SKILL.md`), se o registro estiver
preenchido em `<<PREENCHER>>` acima, a skill grava uma linha com os campos até
`confianca` (os campos de decisão/resultado ficam para o engenheiro preencher
depois, fora do fluxo do agente). Isso não bloqueia a entrega da recomendação —
é o último passo, não pré-requisito.
