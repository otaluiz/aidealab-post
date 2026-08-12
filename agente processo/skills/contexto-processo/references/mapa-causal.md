# Mapa causal — fabricação de gelatina

Referência para a skill `contexto-processo`. Toda relação aqui é
`[a validar]` contra a realidade da planta — o mecanismo é conhecido do setor,
a magnitude e até o sinal podem variar por matéria-prima e equipamento.

Formato: **mecanismo → efeito esperado → como testar**.

---

## 1. Trade-off central: agressividade da extração × Bloom × rendimento

**Mecanismo.** A extração de gelatina é hidrólise controlada do colágeno em
gelatina solúvel. Condição mais agressiva (temperatura mais alta, tempo mais
longo, pH mais extremo) rompe mais ligações — extrai mais massa (rendimento
sobe) — mas rompe também as cadeias já extraídas em fragmentos menores
(Bloom cai, porque a força de gel depende de cadeia longa o suficiente para
formar rede).

**Efeito esperado.** Dentro de uma mesma matéria-prima, rendimento e Bloom devem
se mover em direções opostas ao longo dos estágios de extração: primeiro estágio
(mais brando) tende a Bloom mais alto e rendimento por estágio mais baixo;
estágios finais (mais agressivos), o inverso.

**Como testar.** Regressão de Bloom e de rendimento contra temperatura/tempo do
estágio, controlando por estágio e matéria-prima. Sinais opostos nos
coeficientes é a assinatura do trade-off. Se saírem no mesmo sinal, suspeitar de
confundidor (ex: matéria-prima melhor sendo processada de forma mais branda).

**Consequência para `sugestao-setpoint`.** Este é o par de objetivos concorrentes
mais comum a otimizar. Nunca tratar como se um pudesse subir sem custo no outro
sem evidência.

---

## 2. pH do pré-tratamento × velocidade de extração e Bloom

**Mecanismo.** pH do banho (ácido para tipo A, alcalino para tipo B) controla o
grau de intumescimento e a quebra parcial das ligações cruzadas do colágeno
antes da extração. Pré-tratamento insuficiente deixa colágeno pouco reativo
(extração lenta, rendimento baixo); excessivo já degrada a estrutura antes da
extração começar (Bloom baixo mesmo em extração branda).

**Efeito esperado.** Relação em U invertido entre tempo de pré-tratamento e
Bloom resultante — ótimo em algum ponto intermediário, não nas bordas.

**Como testar.** Se houver variação suficiente de tempo/pH de pré-tratamento no
histórico, ajustar termo quadrático, não só linear. Com pouca variação, a skill
`modelo-preditivo` deve declarar que não há dado para estimar a curvatura.

---

## 3. Temperatura de concentração × degradação térmica

**Mecanismo.** Acima de um limiar, o próprio calor da concentração a vácuo
degrada a gelatina já extraída (mesmo efeito de hidrólise/oxidação térmica).

**Efeito esperado.** Bloom e viscosidade caem se a concentração rodar quente
demais ou por tempo longo demais, independentemente da extração ter sido branda.

**Como testar.** Cruzar tempo de residência na concentração (não só temperatura
de set) com Bloom final, controlando pelo Bloom do caldo antes da concentração
(se existir essa medida intermediária).

---

## 4. Condutividade pós-deionização × cinzas e clareza

**Mecanismo.** A deionização remove sais residuais dos pré-tratamentos.
Deionização incompleta deixa cinzas altas e pode afetar clareza/cor do produto.

**Efeito esperado.** Correlação direta entre condutividade de saída e cinzas do
produto.

**Como testar.** Regressão simples; é uma das relações mais diretas do processo,
útil como caso de calibração para validar que a tabela canônica está correta
antes de confiar em relações mais sutis.

---

## 5. Umidade final × parâmetros de secagem

**Mecanismo.** Umidade residual é função de temperatura do ar, umidade do ar de
entrada, tempo de residência e espessura do leito/fita na secagem.

**Efeito esperado.** Relação direta e geralmente a mais previsível do processo —
é also a que mais sofre de **atraso entre secagem e amostragem** (ver skill
`analise-umidade`): a umidade medida em laboratório pode ter sido amostrada horas
depois da secagem, com equilíbrio higroscópico já em curso.

**Como testar.** Antes de modelar, confirmar o delay entre fim de secagem e
timestamp da amostra de laboratório; se for grande e variável, é a primeira
suspeita para erro de modelo, antes de suspeitar de variável de processo.

---

## 6. Blend × atributos do produto final

**Mecanismo.** O produto embalado é mistura de múltiplos lotes de moagem,
combinados justamente para padronizar Bloom/viscosidade dentro de especificação.

**Efeito esperado.** Isso **atenua e mistura** o sinal de qualquer batelada
individual de extração no atributo final. Correlação entre variável de processo
de uma batelada específica e atributo do produto embalado deve ser mais fraca do
que a correlação entre a mesma variável e o atributo medido no lote antes do
blend, se essa medição intermediária existir.

**Como testar.** Preferir, quando disponível, a medida de qualidade **antes do
blend** como alvo de modelagem. Se só existir medida pós-blend, declarar essa
limitação explicitamente nos resultados de `modelo-preditivo`.
