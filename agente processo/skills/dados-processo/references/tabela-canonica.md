# Tabela analítica canônica — código de referência

Código que a skill `dados-processo` adapta e executa no code interpreter para
montar a tabela de uma linha por batelada. Ajustar nomes de coluna e worksheet
conforme `fontes.md` preenchido.

Se o code interpreter não estiver disponível no tenant, usar este código como
**especificação** do que pedir ao SEEQ Data Lab, e adaptar o passo 6
(validação de qualidade) para ser feito sobre o resultado que voltar.

## 1. Puxar série de processo, fatiando por limite de linhas

```python
import pandas as pd

def puxar_serie_fatiada(worksheet: str, inicio, fim, limite_linhas: int,
                          chamar_serie_processo):
    """
    chamar_serie_processo: função que encapsula o alias SERIE_PROCESSO,
    assinatura (worksheet, inicio, fim) -> DataFrame com coluna 'timestamp'.
    Fatia o período se a duração estimada exceder o limite conhecido da
    ferramenta (ver dados-processo/references/ferramentas.md).
    """
    periodo = pd.date_range(inicio, fim, freq="7D")  # ajustar granularidade
    partes = []
    for i in range(len(periodo) - 1):
        parte = chamar_serie_processo(worksheet, periodo[i], periodo[i + 1])
        if len(parte) >= limite_linhas:
            raise ValueError(
                f"Sub-período {periodo[i]}–{periodo[i+1]} ainda excede o "
                f"limite ({len(parte)} linhas). Reduzir o passo de fatiamento."
            )
        partes.append(parte)
    return pd.concat(partes).drop_duplicates(subset="timestamp").sort_values("timestamp")
```

## 2. Recortar por capsule (batelada) e agregar por fase

```python
def agregar_por_fase(serie: pd.DataFrame, capsules: pd.DataFrame,
                       colunas_processo: list[str]) -> pd.DataFrame:
    """
    capsules: DataFrame com colunas ['nº_batelada', 'fase', 'inicio', 'fim'].
    Retorna uma linha por (nº_batelada, fase) com estatísticas agregadas.
    """
    linhas = []
    for _, cap in capsules.iterrows():
        trecho = serie[(serie["timestamp"] >= cap["inicio"]) &
                        (serie["timestamp"] <= cap["fim"])]
        if trecho.empty:
            continue
        registro = {"nº_batelada": cap["nº_batelada"], "fase": cap["fase"]}
        for col in colunas_processo:
            if col not in trecho:
                continue
            registro[f"{col}_media"] = trecho[col].mean()
            registro[f"{col}_desvio"] = trecho[col].std()
            registro[f"{col}_min"] = trecho[col].min()
            registro[f"{col}_max"] = trecho[col].max()
            # taxa de variação média (unidade / minuto), útil para detectar
            # rampas fora do padrão
            registro[f"{col}_taxa"] = trecho[col].diff().abs().mean()
        linhas.append(registro)
    return pd.DataFrame(linhas)
```

## 3. Pivotar fase para colunas e juntar com laboratório

```python
def montar_tabela_canonica(agregado_por_fase: pd.DataFrame,
                             laboratorio: pd.DataFrame,
                             metadados: pd.DataFrame,
                             chave_juncao: str = "nº_batelada") -> pd.DataFrame:
    """
    Pivota (nº_batelada, fase) -> uma linha por nº_batelada com colunas
    prefixadas pela fase, depois junta com laboratório e metadados.
    """
    pivotada = agregado_por_fase.pivot(index="nº_batelada", columns="fase")
    pivotada.columns = [f"{fase}__{col}" for col, fase in pivotada.columns]
    pivotada = pivotada.reset_index()

    tabela = pivotada.merge(laboratorio, on=chave_juncao, how="left")
    tabela = tabela.merge(metadados, on=chave_juncao, how="left")
    return tabela
```

## 4. Validação de qualidade

```python
def validar_qualidade(tabela: pd.DataFrame, colunas_alvo: list[str],
                        faixas_fisicas: dict[str, tuple[float, float]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Retorna (tabela_valida, relatorio_descarte).
    faixas_fisicas: {coluna: (min, max)} vindas de contexto-processo.
    """
    motivos = pd.DataFrame(index=tabela.index)

    # batelada incompleta: falta qualquer alvo de laboratório
    motivos["sem_laboratorio"] = tabela[colunas_alvo].isna().any(axis=1)

    # fora de faixa física
    for col, (lo, hi) in faixas_fisicas.items():
        if col in tabela:
            motivos[f"fora_faixa_{col}"] = ~tabela[col].between(lo, hi) & tabela[col].notna()

    # sinal congelado: desvio zero em variável de processo que deveria variar
    colunas_desvio = [c for c in tabela.columns if c.endswith("_desvio")]
    motivos["sinal_congelado"] = (tabela[colunas_desvio] == 0).any(axis=1)

    descartar = motivos.any(axis=1)
    relatorio = motivos[descartar].sum().sort_values(ascending=False)
    relatorio = relatorio[relatorio > 0]

    return tabela[~descartar].copy(), relatorio
```

## 5. Uso conjunto — sempre reportar n e descarte

```python
tabela_bruta = montar_tabela_canonica(agregado, laboratorio, metadados)
tabela_valida, descartes = validar_qualidade(
    tabela_bruta,
    colunas_alvo=["bloom", "viscosidade", "umidade", "rendimento_pct"],
    faixas_fisicas={"bloom": (0, 400), "umidade": (0, 20)},  # exemplo — ajustar
)

print(f"n = {len(tabela_valida)} de {len(tabela_bruta)} bateladas")
print("Descartadas por motivo:")
print(descartes)
```

Este print (ou equivalente) faz parte do que toda skill de método deve reportar
ao apresentar qualquer resultado construído sobre esta tabela.
