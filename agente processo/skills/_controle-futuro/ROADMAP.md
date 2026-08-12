# Roadmap — do agente consultivo ao controle de processo

Documento, não skill. Não é importado no Copilot Studio. Registra a evolução
planejada e por que a escrita em sistema de controle é decisão de outra fase,
com outra análise de risco — para que essa decisão não se perca nem seja tomada
por acidente ao editar uma skill existente.

## Onde este conjunto de skills está hoje

**Estágio 1 — consultivo.** O agente lê dados, analisa, modela e recomenda.
Nunca escreve em SEEQ, SCADA ou qualquer sistema de controle. Toda sugestão de
setpoint sai como faixa, com incerteza, e explicitamente marcada como
recomendação sujeita a validação humana.

Três peças já existem neste estágio, deliberadamente, para não forçar reescrita
das skills quando a evolução for decidida:

1. **Envelope de segurança** declarado em `contexto-processo` — hoje usado para
   `sugestao-setpoint` recusar sugestão fora de faixa.
2. **Contrato de recomendação estruturado**
   (`sugestao-setpoint/references/contrato-recomendacao.md`) — o mesmo formato
   que uma camada de controle consumiria como entrada; só o destino muda.
3. **Registro de recomendações**
   (`sugestao-setpoint/references/registro-recomendacoes.md`) — histórico de
   recomendação emitida × decisão do engenheiro × resultado observado. Sem esse
   histórico acumulado desde já, nenhum estágio seguinte tem base para avaliar
   se as recomendações realmente funcionam.

## Estágios seguintes (não implementados)

**Estágio 2 — aplicação assistida com registro fechado.** O engenheiro aplica a
recomendação manualmente (ainda sem escrita automática), mas o registro de
recomendações passa a ser sistematicamente fechado (decisão e resultado sempre
preenchidos, não opcionalmente). Isso é o que permite, pela primeira vez, medir
a qualidade real das recomendações ao longo do tempo — pré-requisito para
justificar qualquer automação.

**Estágio 3 — controle assistido por sistema.** Aqui a decisão de arquitetura
fica em aberto e não deve ser presumida por este roadmap:

- **Supervisório**: o sistema escreve o setpoint, mas dentro de limites
  revisados periodicamente por um engenheiro, com possibilidade de override
  manual sempre disponível.
- **Malha fechada**: o sistema ajusta continuamente sem intervenção por
  ciclo — exige validação de modelo, estabilidade e uma análise de risco muito
  mais rigorosa que qualquer coisa coberta por este conjunto de skills.

A escolha entre os dois — e mesmo se vale a pena ir além do estágio 2 — depende
de quão bem as recomendações do estágio 1/2 performaram no registro acumulado,
e é decisão de segurança de processo, não de engenharia de dados. Não é decisão
que uma skill deva tomar ou sugerir sozinha.

## O que cada estágio exige antes de avançar

| De → Para | Pré-requisito mínimo |
|---|---|
| 1 → 2 | Registro de recomendações em uso real, não só disponível |
| 2 → 3 | Meses de registro fechado mostrando recomendações consistentemente boas; análise de risco formal da planta; decisão explícita de engenharia/segurança sobre supervisório vs. malha fechada |

## O que isso significa para as skills hoje

- O alias `ESCRITA_SETPOINT` existe em `dados-processo/references/ferramentas.md`
  apenas como reservado, marcado "não implementado". Nenhuma skill o invoca.
- Nenhuma skill deste conjunto deve ser editada para chamar esse alias sem
  revisar este roadmap primeiro e sem que a decisão de estágio tenha sido
  tomada explicitamente fora do agente.
