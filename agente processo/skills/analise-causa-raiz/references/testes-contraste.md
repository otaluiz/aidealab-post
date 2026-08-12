# Testes de contraste — código de referência

Código para a skill `analise-causa-raiz`. Assume `tabela` = tabela canônica com
uma coluna categórica de grupo (ex: `grupo` = "bom"/"ruim", ou uma coluna de data
para detecção de regime).

## 1. Contraste bom vs. ruim por variável

```python
import pandas as pd
from scipy import stats

def contrastar_grupos(tabela, coluna_grupo, colunas_processo, grupo_a, grupo_b):
    """
    Para cada variável de processo, compara distribuição entre dois grupos.
    Usa Mann-Whitney (não paramétrico) por padrão — mais robusto a outliers e
    não assume normalidade, comum em dado de processo industrial.
    """
    resultados = []
    a = tabela[tabela[coluna_grupo] == grupo_a]
    b = tabela[tabela[coluna_grupo] == grupo_b]

    for col in colunas_processo:
        if col not in tabela or a[col].isna().all() or b[col].isna().all():
            continue
        stat, p = stats.mannwhitneyu(
            a[col].dropna(), b[col].dropna(), alternative="two-sided"
        )
        resultados.append({
            "variavel": col,
            "media_a": a[col].mean(),
            "media_b": b[col].mean(),
            "desvio_a": a[col].std(),
            "desvio_b": b[col].std(),
            "diferenca": a[col].mean() - b[col].mean(),
            "p_valor": p,
            "n_a": a[col].notna().sum(),
            "n_b": b[col].notna().sum(),
        })

    df = pd.DataFrame(resultados).sort_values("p_valor")
    return df
```

## 2. Detecção de mudança de regime (degrau no tempo)

```python
import numpy as np

def detectar_degrau(tabela, coluna_tempo, coluna_alvo, janela_min=5):
    """
    Varre pontos de corte no tempo e mede a diferença de média entre 'antes'
    e 'depois' de cada corte, normalizada pelo desvio conjunto — um jeito
    simples de achar onde um degrau é mais provável, sem exigir libs de
    detecção de changepoint que podem não estar disponíveis no ambiente.
    """
    ordenada = tabela.sort_values(coluna_tempo).reset_index(drop=True)
    y = ordenada[coluna_alvo].values
    n = len(y)
    melhores = []

    for corte in range(janela_min, n - janela_min):
        antes, depois = y[:corte], y[corte:]
        desvio_conjunto = np.sqrt(
            (antes.std() ** 2 + depois.std() ** 2) / 2
        ) or 1e-9
        diff_normalizada = abs(antes.mean() - depois.mean()) / desvio_conjunto
        melhores.append((ordenada[coluna_tempo].iloc[corte], diff_normalizada))

    resultado = pd.DataFrame(melhores, columns=["data_corte", "forca_degrau"])
    return resultado.sort_values("forca_degrau", ascending=False).head(5)
```

## 3. Ranquear hipóteses cruzando com mecanismo conhecido

```python
def ranquear_hipoteses(contraste_df, mecanismos_conhecidos: dict[str, str],
                         p_limite=0.05):
    """
    mecanismos_conhecidos: {variavel: 'sobe'|'desce'|None} — direção do efeito
    esperado pelo mapa causal, se conhecida.
    Hipótese cujo sinal observado bate com o mecanismo sobe no ranking;
    contradiz, é sinalizada.
    """
    candidatas = contraste_df[contraste_df["p_valor"] < p_limite].copy()
    def avaliar(row):
        esperado = mecanismos_conhecidos.get(row["variavel"])
        observado = "sobe" if row["diferenca"] > 0 else "desce"
        if esperado is None:
            return "sem mecanismo conhecido — investigar"
        if esperado == observado:
            return "consistente com mecanismo conhecido"
        return "CONTRADIZ mecanismo conhecido — checar confundidor"

    candidatas["avaliacao"] = candidatas.apply(avaliar, axis=1)
    return candidatas.sort_values(["avaliacao", "p_valor"])
```
