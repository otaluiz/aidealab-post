# Agente de Análise de Processo de Gelatina — Copilot Studio

## Contexto

Existe um agente no Microsoft Copilot Studio, já criado, com MCPs e fontes de
dados configurados pelo usuário. O objetivo é dotá-lo de skills que o façam
analisar o processo de fabricação de gelatina/colágeno com o rigor de um
engenheiro sênior de processo com formação em data science.

O escopo é **exclusivamente gelatina**. As skills cobrem as diferentes etapas e
linhas da fabricação (maceração, extração multi-estágio, filtração, concentração,
esterilização, gelificação, secagem, moagem/blend; tipos e produtos distintos),
não outras indústrias. Atributos de interesse: rendimento, Bloom, viscosidade e
umidade, entre outros que venham a ser adicionados.

Fontes já disponíveis ao agente:

- **SEEQ** — variáveis de processo do banco SCADA. Extração via `spy.pull` sobre
  worksheets que já contêm sinais e conditions, em grid temporal predefinido. O
  agente pede *worksheet + período*, não nome de tag.
- **Power BI publicado** — semantic model no Service, múltiplas tabelas
  relacionais resumidas em páginas de relatório. Fonte primária de dado agregado.
- **Excel/CSV em SharePoint** — tabelas relacionais de input manual e resultados
  de laboratório.
- **SharePoint (documentos + `.pbix`)** — base de conhecimento: relatórios,
  procedimentos, e os arquivos `.pbix` em si. **`.pbix` é arquivo binário
  compactado — nenhum conector lê tabela de dentro dele.** É tratado como
  referência documental, nunca como fonte de dado; o dado consultável é o
  semantic model publicado no Service ou tabela exportada para Excel/CSV.

Público exclusivo: **engenheiros**. Isso permite linguagem técnica, exposição de
incerteza estatística e recusa explícita quando o dado não sustenta a pergunta.

## Objetivo

Um conjunto de skills no formato **Agent Skills (`SKILL.md`)**, importáveis
individualmente no Copilot Studio, que dão ao agente capacidade de entender o
processo, construir modelos preditivos validados, identificar perfis de operação,
derivar alarmes e propor faixas de setpoint.

## Restrição fundamental: onde a conta roda

Um agente do Copilot Studio não treina modelos por si. Uma tag de SCADA em grid
de 1 minuto gera ~43 mil pontos por mês; nenhum contexto de LLM raciocina sobre
isso cru. Três camadas resolvem.

### Camada 1 — Redução antes do agente

O dado nunca entra bruto. A `spy.pull` traz série em grid; a primeira coisa que
qualquer análise faz é **reduzir para uma linha por unidade de análise**,
agregando cada variável por fase: média, desvio, mínimo, máximo, tempo acima de
limiar, taxa de variação. Alguns milhares de linhas por dezenas de colunas —
cabe no agente e é o formato que a modelagem exige.

A *unidade de análise* padrão é a **batelada**. Em etapa contínua, é uma janela
fixa (hora ou turno). A definição fica declarada em `contexto-processo`.

### Camada 2 — Code interpreter como motor analítico

Sobre a tabela reduzida, o agente executa Python: correlação, regressão, PLS,
random forest com importância de variáveis, detecção de outlier, validação com
split temporal. É isso que produz análise em vez de opinião.

**Degradação graciosa:** sem code interpreter no tenant, cada skill de método
produz a *especificação da análise* (sinais, janela, features, método, critério
de validação) para execução no SEEQ Data Lab, e depois interpreta o resultado
trazido de volta. A skill declara em qual modo está operando.

### Camada 3 — Produtivização por especificação

Alarme e predição contínua não moram no chat. O agente entrega o **artefato de
implementação** — fórmula ou condition SEEQ, limite calculado, medida DAX, faixa
de setpoint — e o engenheiro implanta. O agente nunca escreve em sistema de
controle.

## Integração no ambiente Microsoft

### Aliases de ferramenta

As skills **nunca citam o nome real** de um conector, MCP ou flow. Referenciam um
alias, e o mapeamento alias → ferramenta real vive num único arquivo
(`dados-processo/references/ferramentas.md`). Renomear um flow ou trocar de
conector muda um arquivo, não onze skills.

| Alias | Papel | Realização típica no Copilot Studio |
|---|---|---|
| `SERIE_PROCESSO` | puxar série temporal contextualizada | ferramenta/flow que executa `spy.pull` sobre worksheet + período |
| `MODELO_BI` | consultar indicadores já calculados | semantic model publicado no Power BI Service, consulta DAX |
| `TABELA_SHAREPOINT` | ler resultados de laboratório, inputs manuais e tabelas exportadas | Excel/CSV em SharePoint via conector de arquivos/Graph |
| `DOCUMENTO` | base de conhecimento de processo | SharePoint como knowledge source do agente — inclui `.pbix` como documento, nunca como dado |
| `ESCRITA_SETPOINT` | **reservado, não implementado nesta fase** | ponto de extensão para uma futura camada de controle |

### Contrato da ferramenta SEEQ

O ponto mais frágil da integração, porque não é conector Microsoft nativo — é um
flow/MCP próprio. As skills assumem este contrato mínimo, declarado uma vez:

- **Entrada:** worksheet (nome ou URL), início, fim, e opcionalmente grid e lista
  de conditions.
- **Saída:** tabela em grid regular com coluna de timestamp e uma coluna por
  sinal; e, quando solicitado, a lista de capsules com início, fim e propriedades.
- **Limites declarados:** máximo de linhas por chamada e comportamento em
  truncamento.

Se a chamada exceder o limite, a skill instrui a fatiar por período e agregar
incrementalmente — nunca a analisar dado truncado em silêncio.

## Contrato de dados

### Tabela analítica canônica

Todas as skills de método consomem o mesmo formato: **uma linha por unidade de
análise**.

| Grupo | Conteúdo |
|---|---|
| Chave | identificador de batelada/lote |
| Tempo | início e fim de cada fase |
| Processo | features agregadas por fase, vindas do SEEQ |
| Qualidade | Bloom, viscosidade, umidade, rendimento e demais medidas de lab |
| Metadados | linha/equipamento, tipo de produto, matéria-prima, turno, campanha |

Os metadados de **linha e tipo de produto** são o que permite analisar processos
distintos da mesma planta sem duplicar skill: viram variável de estratificação,
não cópia de arquivo.

Somente `dados-processo` conhece SEEQ, SharePoint e Power BI. As demais enxergam
apenas a tabela canônica. Trocar de fonte muda uma skill, não onze.

### Registro de fontes

`dados-processo/references/fontes.md`: para cada fonte, nome, alias de
ferramenta, localização, granularidade, colunas-chave e chave de junção.
Entregue com estrutura definida e exemplo preenchido; o usuário completa conforme
estrutura as bases.

### Declaração por skill

Cada `SKILL.md` traz um bloco **Dados necessários**: colunas mínimas e número
mínimo de bateladas para a análise ser válida. Faltando qualquer um, a skill
instrui o agente a declarar o que falta em vez de produzir resultado.

### Código

O Python reutilizável (montagem da tabela canônica, validação de qualidade,
treino com split temporal) vai como **blocos de código dentro de arquivos de
referência em markdown**, que o agente adapta e executa. Não como scripts anexos:
bundle executável não é garantido no Copilot Studio; snippet em markdown funciona
em qualquer configuração.

## Catálogo de skills

```
skills/
  README.md
  _gabarito-analise-atributo.md
  _controle-futuro/
    ROADMAP.md
  contexto-processo/
  dados-processo/
  consulta-dados/
  modelo-preditivo/
  analise-causa-raiz/
  perfil-processo/
  alarmes-e-limites/
  sugestao-setpoint/
  analise-rendimento/
  analise-bloom/
  analise-viscosidade/
  analise-umidade/
```

### Base

**`contexto-processo`** — Mapa da planta: etapas da fabricação, variáveis-chave
por etapa, unidades de medida, faixas típicas, linhas e tipos de produto,
definição da unidade de análise, e relações causais conhecidas — incluindo o
trade-off central da extração, em que condição mais agressiva aumenta massa
extraída e degrada Bloom por hidrólise. Entregue preenchido com o conhecimento
geral do setor e **marcado como "a validar"**, para o usuário substituir pela
realidade da planta. É o que impede conclusões fisicamente implausíveis.

**`dados-processo`** — Extração via aliases, contextualização por batelada a
partir das conditions, junção laboratório × processo, checagens de qualidade
(gap, sinal congelado, valor fora de faixa física, batelada incompleta) e a
regra-mor da redução antes de qualquer modelagem.

### Consulta

**`consulta-dados`** — Responde pergunta factual ou agregada ("quanto", "quando",
"qual foi") direto da base relacional (`MODELO_BI`, depois `TABELA_SHAREPOINT`),
sem acionar modelagem. Não dispara para perguntas de "por quê" — aí escala para
`analise-causa-raiz` ou a skill de atributo relevante. Nunca responde a partir de
`.pbix` não publicado.

### Métodos

**`modelo-preditivo`** — Do problema ao modelo validado: definição do alvo,
feature engineering (agregação por fase, lag por tempo de residência), baseline
obrigatório (média e modelo trivial), **split temporal — nunca aleatório**,
métrica em unidade de engenharia, interpretabilidade (importância de variáveis,
dependência parcial), critério de aceite e o dever de declarar ausência de sinal.

**`analise-causa-raiz`** — Contraste entre bateladas boas e ruins, detecção de
mudança de regime, timeline de eventos, comparação de distribuições, e a
disciplina de separar correlação de causa confrontando toda hipótese com
`contexto-processo`. Saída: hipóteses ranqueadas, cada uma com o teste que a
confirmaria.

**`perfil-processo`** — Perfil de referência (golden batch): perfil médio e banda
de tolerância por fase, alinhamento temporal entre bateladas de duração
diferente, score de desvio de uma batelada contra a referência. Perfis são
estratificados por linha e tipo de produto.

**`alarmes-e-limites`** — Derivação de limite a partir do histórico, não de
opinião. Toda proposta acompanha taxa de falso alarme e antecedência média de
detecção naquele histórico. Entrega como condition/fórmula SEEQ pronta.

**`sugestao-setpoint`** — Otimização sob restrição: envelope operável observado,
trade-off multi-objetivo (tipicamente Bloom × rendimento), **proibição de
extrapolar** para região sem dados, saída como **faixa** e não valor único, com
impacto esperado e incerteza, sempre marcada como recomendação sujeita a
validação do engenheiro e às restrições de segurança do processo.

Já produz, sem implementar controle algum, dois artefatos que preparam uma fase
futura: o **contrato de recomendação** (formato estruturado — variável, faixa,
impacto, incerteza, confiança, validade) e o **registro de recomendações**
(schema de lista SharePoint: emitida, avaliada, aplicada, resultado observado).
O envelope de segurança usado para restringir a otimização vem de
`contexto-processo` e é o mesmo campo que uma futura camada de controle
consumiria. Nada disso aciona o alias `ESCRITA_SETPOINT`, reservado e não
chamado nesta fase — ver `skills/_controle-futuro/ROADMAP.md`.

### Atributos

`analise-rendimento`, `analise-bloom`, `analise-viscosidade`, `analise-umidade`.

Cada uma carrega apenas o específico do atributo: método de medição de
laboratório e **incerteza/repetibilidade do ensaio**, variáveis de processo
suspeitas em ordem de prioridade, armadilhas conhecidas. Depois delega ao método.

A incerteza de medição é decisiva: se a repetibilidade do ensaio de Bloom é da
ordem de ±15 g, um modelo com RMSE de 12 g está dentro do ruído do próprio
laboratório e não representa capacidade preditiva. A skill obriga essa comparação.

**`_gabarito-analise-atributo.md`** é a matriz para criar uma skill de atributo
novo (cor, turbidez, cinzas, pH final) sem reescrever método: preenche-se o
método de medição, a incerteza, as variáveis suspeitas e as armadilhas.

## Convenções

- **Nomes** em português, kebab-case.
- **Frontmatter** com `name` e `description`. A `description` das skills de
  atributo e de `analise-causa-raiz` é redigida para disparar por fala do
  engenheiro; a das skills de método e de base, para invocação por outra skill.
  Isso evita competição de trigger e seleção errada pelo agente.
- **Blocos `<<PREENCHER>>`** explícitos e concentrados no topo do arquivo, nunca
  diluídos no texto. Cobrem estrutura de dados (colunas, fontes, chave de
  batelada) e descrição do processo.
- **Autossuficiência:** referência a outra skill é sempre condicional ("se
  disponível"). Importar uma skill sozinha produz comportamento útil, porque o
  usuário exporta e importa uma a uma.
- **Uma pasta por skill**, com `SKILL.md` e, quando necessário,
  `references/*.md`.

## Guardrails transversais

1. Nenhum modelo é apresentado sem baseline, validação temporal e comparação com
   a incerteza da medição do alvo.
2. Toda análise reporta n, período coberto e linhas descartadas por qualidade.
3. Conclusão causal exige mecanismo no `contexto-processo` ou teste dirigido.
   Correlação é apresentada como correlação.
4. Recomendação de setpoint é faixa, dentro do envelope observado, com incerteza,
   sempre sujeita a validação humana. O agente não atua em controle.
5. Alarme proposto vem com o trade-off entre falso alarme e detecção.
6. Análise que mistura linhas ou tipos de produto sem estratificar é sinalizada
   como risco de confundimento.
7. "O dado não sustenta essa pergunta" é resposta válida e obrigatória quando for
   o caso.
8. Dado truncado por limite de ferramenta é declarado, nunca analisado em
   silêncio.

## Fora de escopo

- Criação ou alteração do agente no Copilot Studio, dos MCPs e das fontes de
  dados — já feitos pelo usuário.
- Implantação de alarmes, modelos ou setpoints em qualquer sistema. O agente
  especifica; o engenheiro implanta.
- Implementação de controle de processo. `sugestao-setpoint` produz os ganchos
  (contrato de recomendação, envelope de segurança, registro) para uma fase
  futura, mas não aciona nenhum sistema de controle.
- Processos de outras indústrias.
- Skills para outros públicos (operação, gestão).
