# Ferramentas — mapeamento de aliases

Referência para a skill `dados-processo`. Nenhuma skill deste conjunto cita o
nome real de um conector, MCP ou flow — todas usam os aliases abaixo. Quando você
trocar de conector ou renomear um flow, é este o único arquivo que muda.

## <<PREENCHER>>

```
<<PREENCHER: MAPEAMENTO DE ALIASES>>

SERIE_PROCESSO
  Ferramenta real:     [nome do conector/flow/MCP no Copilot Studio]
  Como chamar:         [nome da action, parâmetros de entrada]

MODELO_BI
  Ferramenta real:     [conector Power BI usado]
  Workspace/dataset:    [nome do workspace, nome do semantic model]

TABELA_SHAREPOINT
  Ferramenta real:     [conector de arquivos SharePoint / Graph]
  Site/biblioteca:      [caminho do site e da biblioteca de documentos]

DOCUMENTO
  Ferramenta real:     [knowledge source configurada no agente]
  Site/biblioteca:      [caminho]

ESCRITA_SETPOINT
  Status:               RESERVADO — não implementado nesta fase.
                         Nenhuma skill deve invocar este alias.
<<FIM>>
```

## Contrato de `SERIE_PROCESSO` (SEEQ)

```
<<PREENCHER: CONTRATO SEEQ>>
Entrada aceita:
  - worksheet:   [nome ou URL — confirmar qual formato o flow espera]
  - início/fim:  [formato de data/hora esperado]
  - grid:        [se configurável, ou fixo pela worksheet]
  - conditions:  [se é possível pedir capsules junto, ou é chamada separada]

Saída:
  - formato:            [JSON / CSV / tabela]
  - colunas:             timestamp + uma coluna por sinal, conforme grid da worksheet
  - capsules (se pedidas): início, fim, propriedades da condition

Limites observados:
  - máximo de linhas por chamada:  [preencher]
  - comportamento ao exceder:      [erro / truncamento silencioso / paginação —
                                     CONFIRMAR. Se for truncamento silencioso,
                                     dados-processo deve sempre fatiar por
                                     sub-período preventivamente]
<<FIM>>
```

Se o comportamento em excesso de linhas não estiver confirmado, tratar como
truncamento silencioso por padrão (o pior caso) até verificação: fatiar qualquer
período longo em sub-períodos que fiquem com folga abaixo do limite, puxar cada
um separadamente e concatenar.

## Regra sobre `.pbix`

Arquivos `.pbix` alcançáveis por `TABELA_SHAREPOINT` ou `DOCUMENTO` são
documento, não dado. Não há leitura de tabela interna de `.pbix` por conector.
Dado tabular do Power BI só vem de `MODELO_BI` (modelo publicado, consulta
DAX/tabular). Ver `dados-processo/SKILL.md`, seção "Regra sobre Power BI e
`.pbix`".

## `ESCRITA_SETPOINT` — reservado

Ponto de extensão para uma futura fase de controle de processo (ver
`skills/_controle-futuro/ROADMAP.md`). Não está implementado. Nenhuma skill deste
conjunto deve tentar invocá-lo ou instruir o usuário a configurá-lo para
atuação automática nesta fase.
