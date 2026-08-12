# Registro de fontes

Referência para a skill `dados-processo`. Cada fonte de dado real do seu agente
é declarada aqui: onde está, que granularidade tem, e como se junta com as
outras. `dados-processo` lê este arquivo antes de montar a tabela canônica.

## <<PREENCHER>>

Copie o bloco abaixo para cada fonte nova. O exemplo preenchido logo depois
mostra o nível de detalhe esperado.

```
<<PREENCHER: FONTE>>
Nome:                [nome curto e estável, usado nas outras skills]
Tipo:                [worksheet SEEQ | tabela do modelo Power BI | Excel/CSV SharePoint]
Alias de ferramenta:  [SERIE_PROCESSO | MODELO_BI | TABELA_SHAREPOINT]
Localização:          [nome da worksheet / nome da tabela / caminho do arquivo]
Granularidade:        [grid da worksheet | uma linha por batelada | uma linha por dia...]
Colunas-chave:        [lista das colunas relevantes para análise]
Chave de junção:       [coluna usada para juntar com outras fontes, ex: nº de lote]
Observações:          [atrasos conhecidos, qualidade, quem mantém]
<<FIM>>
```

---

## Exemplo preenchido (referência de formato — substituir por dado real)

```
Nome:                Extração — Linha 1
Tipo:                worksheet SEEQ
Alias de ferramenta:  SERIE_PROCESSO
Localização:          "Extração L1 - Estágios" (worksheet)
Granularidade:        grid de 1 min; condition "Batelada Extração L1" delimita
                       cada unidade de análise; condition "Estágio" subdivide
                       cada batelada em fases
Colunas-chave:        temp_estagio_1..4, ph_caldo, tempo_estagio_1..4,
                       razao_agua_solido
Chave de junção:       nº_batelada (propriedade da condition "Batelada")
Observações:          grid começou a ser usado em 2025-01; antes disso,
                       histórico está em outra worksheet com grid de 5 min
```

```
Nome:                Laboratório — Resultados por lote
Tipo:                Excel/CSV SharePoint
Alias de ferramenta:  TABELA_SHAREPOINT
Localização:          [site]/Qualidade/Laboratorio_Resultados.xlsx, aba "Lotes"
Granularidade:        uma linha por lote de laboratório
Colunas-chave:        nº_lote, bloom, viscosidade, umidade, cinzas, ph,
                       data_amostra, ponto_amostragem
Chave de junção:       nº_lote — CONFIRMAR se nº_lote mapeia 1:1 para
                       nº_batelada ou se é pós-blend (ver contexto-processo,
                       "Blend × atributos do produto final")
Observações:          ponto_amostragem distingue "pré-blend" de "produto final";
                       preferir pré-blend como alvo quando existir
```

```
Nome:                Indicadores de produção
Tipo:                tabela do modelo Power BI
Alias de ferramenta:  MODELO_BI
Localização:          workspace "[nome]", dataset "[nome]", tabela "Producao"
Granularidade:        agregado diário por linha
Colunas-chave:        data, linha, rendimento_pct, volume_produzido, oee
Chave de junção:       data + linha
Observações:          fonte primária para consulta-dados; não confundir com
                       o .pbix do mesmo relatório salvo no SharePoint — este
                       último é só documento (ver ferramentas.md)
```
