# Receita de modelagem — código de referência

Código para a skill `modelo-preditivo`. Assume que `tabela` é a tabela canônica
já validada por `dados-processo`, ordenada por tempo, com uma coluna de alvo
(ex: `bloom`) e colunas de features numéricas.

## 1. Baseline

```python
import numpy as np

def baseline_media(y_treino, y_teste, y_teste_estrato=None):
    """
    Baseline simples: prever a média do treino para tudo.
    Se y_teste_estrato (ex: linha/produto) for passado, usa média por estrato
    quando houver dado suficiente, senão cai para média geral.
    """
    media_geral = y_treino.mean()
    pred = np.full_like(y_teste, media_geral, dtype=float)
    rmse = np.sqrt(np.mean((y_teste - pred) ** 2))
    return pred, rmse
```

## 2. Split temporal

```python
def split_temporal(tabela, coluna_tempo, frac_treino=0.7):
    """
    Ordena por tempo e corta cronologicamente. Nunca usar train_test_split
    aleatório aqui — bateladas vizinhas no tempo compartilham campanha,
    fornecedor e ajuste de processo, e isso vaza informação se embaralhado.
    """
    ordenada = tabela.sort_values(coluna_tempo).reset_index(drop=True)
    corte = int(len(ordenada) * frac_treino)
    return ordenada.iloc[:corte], ordenada.iloc[corte:]
```

## 3. Pipeline de modelagem crescente

```python
from sklearn.linear_model import RidgeCV
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import numpy as np

def treinar_e_avaliar(X_treino, y_treino, X_teste, y_teste, incerteza_medicao):
    resultados = {}

    # 1. Linear regularizado
    modelo_linear = make_pipeline(StandardScaler(), RidgeCV())
    modelo_linear.fit(X_treino, y_treino)
    pred = modelo_linear.predict(X_teste)
    resultados["linear"] = {
        "modelo": modelo_linear,
        "rmse": np.sqrt(np.mean((y_teste - pred) ** 2)),
    }

    # 2. PLS — útil quando features de processo são muito correlacionadas
    #    entre si (comum: temperatura e tempo de um mesmo estágio)
    n_componentes = min(5, X_treino.shape[1] - 1) if X_treino.shape[1] > 1 else 1
    modelo_pls = PLSRegression(n_components=max(1, n_componentes))
    modelo_pls.fit(X_treino, y_treino)
    pred = modelo_pls.predict(X_teste).ravel()
    resultados["pls"] = {
        "modelo": modelo_pls,
        "rmse": np.sqrt(np.mean((y_teste - pred) ** 2)),
    }

    # 3. Random forest — só se n permitir (regra de bolso: >= 60 linhas de treino)
    if len(X_treino) >= 60:
        modelo_rf = RandomForestRegressor(
            n_estimators=300, max_depth=5, min_samples_leaf=3, random_state=0
        )
        modelo_rf.fit(X_treino, y_treino)
        pred = modelo_rf.predict(X_teste)
        resultados["random_forest"] = {
            "modelo": modelo_rf,
            "rmse": np.sqrt(np.mean((y_teste - pred) ** 2)),
        }

    # Critério de aceite: melhor RMSE precisa ficar abaixo da incerteza de
    # medição do próprio ensaio. Senão, o modelo está competindo com ruído.
    melhor = min(resultados.items(), key=lambda kv: kv[1]["rmse"])
    resultados["melhor"] = melhor[0]
    resultados["aceitavel"] = melhor[1]["rmse"] < incerteza_medicao

    return resultados
```

## 4. Interpretabilidade

```python
def importancia_variaveis(modelo_rf, nomes_features, top_n=5):
    importancias = sorted(
        zip(nomes_features, modelo_rf.feature_importances_),
        key=lambda x: -x[1],
    )
    return importancias[:top_n]


def dependencia_parcial_simples(modelo, X, coluna, n_pontos=20):
    """
    Versão simplificada: varia uma coluna no range observado, mantém as
    demais na mediana, e observa a predição — dá o formato da relação sem
    depender de sklearn.inspection (nem sempre disponível no ambiente).
    """
    import numpy as np
    X_base = X.median().to_frame().T
    valores = np.linspace(X[coluna].min(), X[coluna].max(), n_pontos)
    preds = []
    for v in valores:
        linha = X_base.copy()
        linha[coluna] = v
        preds.append(modelo.predict(linha)[0])
    return valores, preds
```

## 5. Relato — o que sempre imprimir

```python
def relatar(resultados, baseline_rmse, incerteza_medicao, n_treino, n_teste):
    melhor = resultados["melhor"]
    rmse_melhor = resultados[melhor]["rmse"]
    print(f"n treino={n_treino}, n teste={n_teste}")
    print(f"Baseline (média): RMSE={baseline_rmse:.2f}")
    print(f"Melhor modelo ({melhor}): RMSE={rmse_melhor:.2f}")
    print(f"Incerteza de medição do alvo: {incerteza_medicao:.2f}")
    if rmse_melhor >= baseline_rmse:
        print("=> Modelo não supera o baseline. Não há sinal utilizável.")
    elif rmse_melhor >= incerteza_medicao:
        print("=> Modelo supera o baseline mas está dentro do ruído do "
              "próprio ensaio. Não representa capacidade preditiva real.")
    else:
        print("=> Modelo supera baseline e incerteza de medição. Prosseguir "
              "para interpretação de variáveis.")
```
