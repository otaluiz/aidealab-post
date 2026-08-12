# Avaliação de limite candidato — código de referência

Código para a skill `alarmes-e-limites`. Assume `tabela` = tabela canônica com
uma coluna de variável candidata e uma coluna booleana `desfecho_ruim`.

## 1. Varredura de limites candidatos

```python
import numpy as np
import pandas as pd

def varrer_limites(tabela, coluna_variavel, coluna_desfecho,
                     direcao="acima", n_candidatos=30):
    """
    direcao: 'acima' (alarme dispara quando variável > limite) ou 'abaixo'.
    Retorna, para cada limite candidato, taxa de falso alarme e taxa de
    detecção no histórico.
    """
    valores = tabela[coluna_variavel].dropna()
    candidatos = np.linspace(valores.quantile(0.05), valores.quantile(0.95), n_candidatos)

    linhas = []
    bons = tabela[~tabela[coluna_desfecho]]
    ruins = tabela[tabela[coluna_desfecho]]

    for limite in candidatos:
        if direcao == "acima":
            dispara_bom = (bons[coluna_variavel] > limite).mean()
            dispara_ruim = (ruins[coluna_variavel] > limite).mean()
        else:
            dispara_bom = (bons[coluna_variavel] < limite).mean()
            dispara_ruim = (ruins[coluna_variavel] < limite).mean()

        linhas.append({
            "limite": limite,
            "taxa_falso_alarme": dispara_bom,
            "taxa_deteccao": dispara_ruim,
        })

    return pd.DataFrame(linhas)
```

## 2. Antecedência média de detecção

```python
def antecedencia_deteccao(series_ruins: list[pd.DataFrame], coluna_variavel,
                            coluna_tempo, coluna_tempo_desfecho, limite,
                            direcao="acima"):
    """
    series_ruins: uma série temporal por batelada ruim (não a tabela agregada —
    aqui precisa do traço no tempo para saber QUANDO cruzou o limite).
    coluna_tempo_desfecho: timestamp em que o desfecho ruim se confirmou
    (ex: fim da batelada, ou momento da amostra de laboratório).
    """
    antecedencias = []
    for serie in series_ruins:
        if direcao == "acima":
            cruzamento = serie[serie[coluna_variavel] > limite]
        else:
            cruzamento = serie[serie[coluna_variavel] < limite]

        if cruzamento.empty:
            continue  # não detectou esta batelada ruim

        primeiro_disparo = cruzamento[coluna_tempo].min()
        momento_desfecho = serie[coluna_tempo_desfecho].iloc[0]
        antecedencia = (momento_desfecho - primeiro_disparo).total_seconds() / 60
        if antecedencia > 0:
            antecedencias.append(antecedencia)

    if not antecedencias:
        return None
    return {
        "antecedencia_media_min": np.mean(antecedencias),
        "n_detectadas_com_antecedencia": len(antecedencias),
        "n_total_ruins": len(series_ruins),
    }
```

## 3. Selecionar pontos de operação

```python
def pontos_de_operacao(varredura: pd.DataFrame):
    """
    Sugere três pontos: conservador (baixo falso alarme), balanceado
    (melhor F1-like entre detecção e falso alarme), agressivo (alta detecção).
    """
    v = varredura.copy()
    v["score_balanceado"] = v["taxa_deteccao"] - v["taxa_falso_alarme"]

    conservador = v.sort_values("taxa_falso_alarme").iloc[0]
    balanceado = v.sort_values("score_balanceado", ascending=False).iloc[0]
    agressivo = v.sort_values("taxa_deteccao", ascending=False).iloc[0]

    return {"conservador": conservador, "balanceado": balanceado, "agressivo": agressivo}
```

## 4. Template de condition SEEQ (texto, para preencher e entregar)

```
Nome sugerido:        Alarme_<Variavel>_<Linha>
Tipo de condition:     limite simples com sustentação de tempo
Expressão (esboço):    $variavel > <limite escolhido>
Sustentação:           disparar somente se condição persistir por >= <X min>
                        (reduz falso alarme por ruído de sensor pontual)
Propriedades a anexar: taxa_falso_alarme_historica, taxa_deteccao_historica,
                        antecedencia_media_min, data_calibracao
```
