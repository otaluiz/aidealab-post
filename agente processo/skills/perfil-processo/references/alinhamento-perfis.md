# Alinhamento e score de perfil — código de referência

Código para a skill `perfil-processo`. Assume acesso à série (não só à tabela
agregada) das bateladas de referência, com timestamp e um marcador de fase, para
poder normalizar por progresso.

## 1. Normalizar por progresso de fase

```python
import pandas as pd
import numpy as np

def normalizar_progresso(serie_batelada: pd.DataFrame, inicio, fim,
                           n_pontos=50) -> pd.DataFrame:
    """
    Reamostra a série de uma batelada (ou fase) para n_pontos igualmente
    espaçados em progresso [0, 1], via interpolação — permite comparar
    bateladas de duração diferente ponto a ponto.
    """
    trecho = serie_batelada[
        (serie_batelada["timestamp"] >= inicio) & (serie_batelada["timestamp"] <= fim)
    ].copy()
    if trecho.empty:
        return pd.DataFrame()

    duracao_total = (fim - inicio).total_seconds()
    trecho["progresso"] = (
        (trecho["timestamp"] - inicio).dt.total_seconds() / duracao_total
    )

    grade = np.linspace(0, 1, n_pontos)
    colunas_numericas = trecho.select_dtypes(include="number").columns
    colunas_numericas = [c for c in colunas_numericas if c != "progresso"]

    reamostrado = {"progresso": grade}
    for col in colunas_numericas:
        reamostrado[col] = np.interp(grade, trecho["progresso"], trecho[col])

    return pd.DataFrame(reamostrado)
```

## 2. Perfil de referência (mediana + banda)

```python
def construir_perfil(lista_bateladas_normalizadas: list[pd.DataFrame],
                       colunas_processo: list[str]) -> pd.DataFrame:
    """
    lista_bateladas_normalizadas: uma entrada por batelada de referência,
    já normalizada por normalizar_progresso (mesma grade de progresso).
    """
    empilhado = pd.concat(lista_bateladas_normalizadas, keys=range(len(lista_bateladas_normalizadas)))
    perfil = empilhado.groupby("progresso")[colunas_processo].agg(
        ["median", lambda s: s.quantile(0.10), lambda s: s.quantile(0.90)]
    )
    perfil.columns = [
        f"{col}_{'p10' if fn == '<lambda_0>' else 'p90' if fn == '<lambda_1>' else 'mediana'}"
        for col, fn in perfil.columns
    ]
    return perfil.reset_index()
```

## 3. Score de desvio de uma batelada contra o perfil

```python
def score_desvio(batelada_normalizada: pd.DataFrame, perfil: pd.DataFrame,
                   colunas_processo: list[str]) -> dict:
    """
    Para cada variável, mede a fração dos pontos fora da banda p10-p90 do
    perfil, e a distância média (normalizada pela banda) quando fora.
    """
    juntado = batelada_normalizada.merge(perfil, on="progresso")
    contribuicoes = {}

    for col in colunas_processo:
        p10, p90, valor = juntado[f"{col}_p10"], juntado[f"{col}_p90"], juntado[col]
        fora = (valor < p10) | (valor > p90)
        largura_banda = (p90 - p10).replace(0, np.nan)
        distancia = np.where(
            valor < p10, (p10 - valor) / largura_banda,
            np.where(valor > p90, (valor - p90) / largura_banda, 0),
        )
        contribuicoes[col] = {
            "fracao_fora_da_banda": fora.mean(),
            "distancia_media_normalizada": np.nanmean(distancia),
        }

    score_geral = np.mean([c["fracao_fora_da_banda"] for c in contribuicoes.values()])
    ranking = sorted(contribuicoes.items(), key=lambda kv: -kv[1]["fracao_fora_da_banda"])

    return {"score_geral": score_geral, "ranking_variaveis": ranking}
```
