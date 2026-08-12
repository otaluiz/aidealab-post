# Otimização restrita — código de referência

Código para a skill `sugestao-setpoint`. Assume `tabela` = tabela canônica,
`modelo` = modelo treinado por `modelo-preditivo` para o atributo alvo, e
`envelope_seguranca` = dict vindo de `contexto-processo`.

## 1. Envelope operável observado (não confundir com envelope de segurança)

```python
import numpy as np
import pandas as pd

def envelope_operavel(tabela, coluna_variavel, p_baixo=5, p_alto=95):
    """
    Região onde há dado real o suficiente para confiar na predição do
    modelo — tipicamente mais estreita que o envelope de segurança.
    """
    return {
        "min_observado": tabela[coluna_variavel].quantile(p_baixo / 100),
        "max_observado": tabela[coluna_variavel].quantile(p_alto / 100),
    }


def envelope_efetivo(envelope_seguranca: dict, envelope_obs: dict):
    """
    A otimização nunca busca fora do menor dos dois. Envelope de segurança
    mais largo que o observado NÃO amplia a busca — só o observado garante
    que o modelo tem sustentação ali.
    """
    return {
        "min": max(envelope_seguranca["min"], envelope_obs["min_observado"]),
        "max": min(envelope_seguranca["max"], envelope_obs["max_observado"]),
    }
```

## 2. Busca em grade dentro do envelope

```python
def buscar_grade(modelo, tabela, coluna_variavel, envelope_ef, n_pontos=25):
    """
    Varia a variável de interesse dentro do envelope efetivo, mantém as
    demais features na mediana (ou no ponto de operação atual, se informado),
    e avalia o modelo em cada ponto.
    """
    candidatos = np.linspace(envelope_ef["min"], envelope_ef["max"], n_pontos)
    X_base = tabela.drop(columns=[coluna_variavel]).median().to_frame().T

    linhas = []
    for v in candidatos:
        X_linha = X_base.copy()
        X_linha[coluna_variavel] = v
        pred = modelo.predict(X_linha)[0]
        linhas.append({coluna_variavel: v, "predito": pred})

    return pd.DataFrame(linhas)
```

## 3. Trade-off multi-objetivo (ex: Bloom × rendimento)

```python
def fronteira_trade_off(modelo_obj1, modelo_obj2, tabela, coluna_variavel,
                          envelope_ef, n_pontos=25):
    """
    Avalia os dois objetivos na mesma grade de candidatos e retorna a
    fronteira — não escolhe um ponto único, porque o peso entre objetivos
    é decisão do engenheiro.
    """
    candidatos = np.linspace(envelope_ef["min"], envelope_ef["max"], n_pontos)
    X_base = tabela.drop(columns=[coluna_variavel]).median().to_frame().T

    linhas = []
    for v in candidatos:
        X_linha = X_base.copy()
        X_linha[coluna_variavel] = v
        linhas.append({
            coluna_variavel: v,
            "objetivo_1": modelo_obj1.predict(X_linha)[0],
            "objetivo_2": modelo_obj2.predict(X_linha)[0],
        })

    df = pd.DataFrame(linhas)
    # pontos não-dominados (fronteira de Pareto simples, para 2 objetivos
    # onde ambos "maior é melhor" — ajustar sinal se for o contrário)
    df_ordenado = df.sort_values("objetivo_1", ascending=False)
    fronteira = []
    melhor_obj2 = -np.inf
    for _, row in df_ordenado.iterrows():
        if row["objetivo_2"] > melhor_obj2:
            fronteira.append(row)
            melhor_obj2 = row["objetivo_2"]

    return pd.DataFrame(fronteira)
```

## 4. Propagação simples de incerteza

```python
def faixa_com_incerteza(valor_predito, rmse_modelo, largura_intervalo=1.0):
    """
    Faixa simples em torno do valor predito usando o RMSE de validação do
    modelo como proxy de incerteza — conservador e fácil de explicar.
    """
    return {
        "central": valor_predito,
        "faixa_min": valor_predito - largura_intervalo * rmse_modelo,
        "faixa_max": valor_predito + largura_intervalo * rmse_modelo,
    }
```
