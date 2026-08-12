# Skills — Agente de análise de processo de gelatina (Copilot Studio)

Cada pasta abaixo é uma Agent Skill (`SKILL.md`) exportável e importável
individualmente no Copilot Studio. Design completo em
[docs/superpowers/specs/2026-08-11-agente-processo-copilot-design.md](../../docs/superpowers/specs/2026-08-11-agente-processo-copilot-design.md).

## Ordem de importação recomendada

1. **`contexto-processo`** e **`dados-processo`** primeiro — as demais skills
   funcionam sozinhas, mas produzem resultado melhor (e mais seguro, no caso do
   envelope de segurança) com essas duas presentes.
2. **`consulta-dados`** — se o uso principal inicial for pergunta de indicador.
3. As skills de método (`modelo-preditivo`, `analise-causa-raiz`,
   `perfil-processo`, `alarmes-e-limites`, `sugestao-setpoint`) — importar
   conforme as skills de atributo que dependem delas forem sendo usadas.
4. As skills de atributo (`analise-rendimento`, `analise-bloom`,
   `analise-viscosidade`, `analise-umidade`) — são o ponto de entrada que o
   engenheiro vai acionar por fala.

Nenhuma importação depende de outra ter sido feita antes — é só a ordem que dá
o melhor resultado.

## Catálogo

| Skill | Dispara por fala? | Papel |
|---|---|---|
| `contexto-processo` | não | mapa da planta, envelope de segurança, mecanismos causais |
| `dados-processo` | não | extração, contextualização por batelada, tabela canônica, qualidade |
| `consulta-dados` | sim | pergunta factual/agregada, sem modelagem |
| `modelo-preditivo` | não | modelo validado: baseline, split temporal, incerteza |
| `analise-causa-raiz` | sim | hipóteses ranqueadas com teste de confirmação |
| `perfil-processo` | não | golden batch e score de desvio |
| `alarmes-e-limites` | não | limite derivado do histórico + taxa de falso alarme |
| `sugestao-setpoint` | não | faixa de setpoint sob restrição, nunca valor único |
| `analise-rendimento` | sim | orquestra os métodos acima para rendimento |
| `analise-bloom` | sim | orquestra os métodos acima para Bloom |
| `analise-viscosidade` | sim | orquestra os métodos acima para viscosidade |
| `analise-umidade` | sim | orquestra os métodos acima para umidade |

`_gabarito-analise-atributo.md` — matriz para criar uma skill de atributo novo
(cor, cinzas, pH final...) sem reescrever método.

`_controle-futuro/ROADMAP.md` — documento (não skill, não importar) sobre a
evolução para uma futura fase de controle de processo. Ver também a nota "Nota
para a fase de controle" em `sugestao-setpoint/SKILL.md`.

## Como preencher os `<<PREENCHER>>`

Cada skill que precisa de dado real da planta tem um bloco `<<PREENCHER>>` no
topo do `SKILL.md` (ou de um `references/*.md`). São, nesta ordem de
prioridade para o funcionamento básico:

1. `dados-processo/references/ferramentas.md` — mapeia os aliases
   (`SERIE_PROCESSO`, `MODELO_BI`, `TABELA_SHAREPOINT`, `DOCUMENTO`) para as
   ferramentas reais do seu agente, e confirma o contrato do conector SEEQ
   (`spy.pull`: entrada, saída, limite de linhas).
2. `dados-processo/references/fontes.md` — registra as worksheets, tabelas do
   modelo Power BI e planilhas do SharePoint que existem de verdade.
3. `contexto-processo/SKILL.md` — etapas, variáveis, faixas, unidade de
   análise e **envelope de segurança** (obrigatório para `sugestao-setpoint`
   funcionar).
4. Cada `analise-<atributo>/SKILL.md` — método de ensaio, incerteza de
   medição, variáveis suspeitas.

Sem os itens 1–2 preenchidos, `dados-processo` não tem como montar a tabela
canônica e deve dizer exatamente o que falta em vez de inventar.

## Convenções

- Uma pasta por skill, `SKILL.md` + `references/*.md` quando houver.
- Código Python fica em blocos dentro de `references/*.md` — nunca como script
  anexo (bundle executável não é garantido no Copilot Studio).
- Toda skill de método declara se está operando com code interpreter ou em modo
  degradado (especificação para o SEEQ Data Lab).
- Nenhuma skill escreve em sistema de controle. `sugestao-setpoint` sempre
  entrega faixa, nunca valor único, como recomendação sujeita a validação.

## Escopo

Exclusivamente o processo de fabricação de gelatina/colágeno desta planta,
para uso por engenheiros. Não cobre operação, gestão, nem controle automático.
