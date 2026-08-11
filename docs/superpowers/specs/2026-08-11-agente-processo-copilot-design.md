# Agente de Análise de Processo — Copilot Studio

## Contexto

Existe um agente no Microsoft Copilot Studio, já criado, com MCPs e fontes de
dados configurados pelo usuário. O objetivo é dotá-lo de skills que o façam
analisar processos industriais com o rigor de um engenheiro sênior de processo
com formação em data science.

O primeiro processo atendido é uma planta de gelatina/colágeno (atributos:
rendimento, Bloom, viscosidade, umidade). Mas o conjunto **não pode ser
específico dessa planta**: precisa receber processos diferentes sem reescrita.

Fontes já disponíveis ao agente:

- **SEEQ** — variáveis de processo do banco SCADA. Extração via `spy.pull` sobre
  worksheets que já contêm sinais e conditions, em grid temporal predefinido. O
  agente pede *worksheet + período*, não nome de tag.
- **Power BI** — dados agregados.
- **Excel em SharePoint** — tabelas relacionais de input manual e resultados de
  laboratório.
- **SharePoint** — base de conhecimento: relatórios e documentos de processo.

Público exclusivo: **engenheiros**. Isso permite linguagem técnica, exposição de
incerteza estatística e recusa explícita quando o dado não sustenta a pergunta.

## Objetivo

Um framework de skills no formato **Agent Skills (`SKILL.md`)**, importáveis
individualmente no Copilot Studio, dividido em um **núcleo agnóstico de processo**
e **pacotes de processo** plugáveis. Adicionar uma nova planta significa
adicionar um pacote — nenhuma alteração no núcleo.

## Princípio de arquitetura: núcleo agnóstico + pacote de processo

Esta é a decisão estruturante. Todo conhecimento que varia entre plantas fica
isolado em um pacote; tudo que é método fica no núcleo e nunca é editado.

```
skills/
  nucleo/                      <- agnóstico, não editar por processo
    dados-processo/
    modelo-preditivo/
    analise-causa-raiz/
    perfil-processo/
    alarmes-e-limites/
    sugestao-setpoint/
    novo-processo/
  processos/
    gelatina/                  <- pacote do 1º processo
      contexto-processo/
      analise-rendimento/
      analise-bloom/
      analise-viscosidade/
      analise-umidade/
    <proximo-processo>/
      contexto-processo/
      analise-<atributo>/
  _gabaritos/
    contexto-processo.md
    analise-atributo.md
```

O que distingue as camadas:

| | Núcleo | Pacote de processo |
|---|---|---|
| Contém | método estatístico e de engenharia de dados | vocabulário, etapas, variáveis, atributos, fontes |
| Muda quando | o método melhora | entra uma planta nova |
| Editado pelo usuário | não | sim, sempre |
| Reusado entre plantas | integralmente | nunca |

Uma skill do núcleo jamais cita Bloom, extração ou maceração. Uma skill de
pacote jamais explica como se faz validação cruzada temporal.

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

A *unidade de análise* é definida pelo pacote de processo: batelada, campanha,
lote de secagem, ou janela fixa (hora/turno) em processo contínuo.

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

As skills **nunca citam o nome real** de um conector, MCP ou flow. Referenciam
um alias, e o mapeamento alias → ferramenta real vive num único arquivo do
pacote de processo (`references/ferramentas.md`). Assim a mesma skill funciona em
tenants onde as ferramentas têm nomes diferentes, e a manutenção é um arquivo.

| Alias | Papel | Realização típica no Copilot Studio |
|---|---|---|
| `SERIE_PROCESSO` | puxar série temporal contextualizada | ferramenta/flow que executa `spy.pull` sobre worksheet + período |
| `TABELA_LAB` | ler resultados de laboratório e inputs manuais | Excel em SharePoint via conector de arquivos/Graph |
| `AGREGADO_BI` | consultar indicadores já calculados | conector Power BI |
| `DOCUMENTO` | base de conhecimento de processo | SharePoint como knowledge source do agente |

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
incrementalmente — nunca a silenciosamente analisar dado truncado.

## Contrato de dados

### Tabela analítica canônica

Todas as skills de método consomem o mesmo formato: **uma linha por unidade de
análise**.

| Grupo | Conteúdo |
|---|---|
| Chave | identificador da unidade de análise |
| Tempo | início e fim de cada fase |
| Processo | features agregadas por fase, vindas do SEEQ |
| Qualidade | atributos medidos (definidos pelo pacote de processo) |
| Metadados | equipamento/linha, matéria-prima, turno, campanha |

Somente `dados-processo` conhece SEEQ, SharePoint e Power BI. As demais enxergam
apenas a tabela canônica. Trocar de fonte muda uma skill, não onze.

### Registro de fontes

O pacote de processo carrega `references/fontes.md`: para cada fonte, nome, alias
de ferramenta, localização, granularidade, colunas-chave e chave de junção.
Entregue com estrutura definida e exemplo preenchido; o usuário completa.

### Declaração por skill

Cada `SKILL.md` traz um bloco **Dados necessários**: colunas mínimas e número
mínimo de unidades de análise para a análise ser válida. Faltando qualquer um, a
skill instrui o agente a declarar o que falta em vez de produzir resultado.

### Código

O Python reutilizável (montagem da tabela canônica, validação de qualidade,
treino com split temporal) vai como **blocos de código dentro de arquivos de
referência em markdown**, que o agente adapta e executa. Não como scripts anexos:
bundle executável não é garantido no Copilot Studio; snippet em markdown funciona
em qualquer configuração.

## Catálogo de skills

### Núcleo — infraestrutura

**`dados-processo`** — Procedimento de extração via aliases, contextualização por
unidade de análise a partir das conditions, junção laboratório × processo,
checagens de qualidade (gap, sinal congelado, valor fora de faixa física, unidade
incompleta) e a regra-mor da redução antes de qualquer modelagem. Lê a definição
de unidade de análise e o registro de fontes do pacote de processo ativo.

**`novo-processo`** — Onboarding de uma planta nova: conduz o preenchimento do
`contexto-processo` a partir do gabarito, o registro de fontes e ferramentas, e a
geração de uma skill `analise-<atributo>` por atributo relevante. É o que torna o
framework operável por quem não participou deste design.

### Núcleo — métodos

**`modelo-preditivo`** — Do problema ao modelo validado: definição do alvo,
feature engineering (agregação por fase, lag por tempo de residência), baseline
obrigatório (média e modelo trivial), **split temporal — nunca aleatório**,
métrica em unidade de engenharia, interpretabilidade (importância de variáveis,
dependência parcial), critério de aceite e o dever de declarar ausência de sinal.

**`analise-causa-raiz`** — Contraste entre unidades boas e ruins, detecção de
mudança de regime, timeline de eventos, comparação de distribuições, e a
disciplina de separar correlação de causa confrontando toda hipótese com o
`contexto-processo` do pacote ativo. Saída: hipóteses ranqueadas, cada uma com o
teste que a confirmaria.

**`perfil-processo`** — Perfil de referência (golden batch): perfil médio e banda
de tolerância por fase, alinhamento temporal entre unidades de duração diferente,
score de desvio de uma unidade contra a referência.

**`alarmes-e-limites`** — Derivação de limite a partir do histórico, não de
opinião. Toda proposta acompanha taxa de falso alarme e antecedência média de
detecção naquele histórico. Entrega como condition/fórmula SEEQ pronta.

**`sugestao-setpoint`** — Otimização sob restrição: envelope operável observado,
trade-off multi-objetivo, **proibição de extrapolar** para região sem dados,
saída como **faixa** e não valor único, com impacto esperado e incerteza, sempre
marcada como recomendação sujeita a validação do engenheiro e às restrições de
segurança do processo.

### Pacote de processo

**`contexto-processo`** — Mapa da planta: etapas, variáveis-chave por etapa,
unidades de medida, faixas típicas, unidade de análise, e relações causais
conhecidas. Para gelatina, entregue como esqueleto preenchido com conhecimento
geral do setor e **marcado como "a validar"** — incluindo o trade-off central da
extração, em que condição mais agressiva aumenta massa extraída e degrada Bloom
por hidrólise. O usuário substitui pela realidade da planta.

**`analise-<atributo>`** — Uma por atributo. Para o pacote gelatina:
`analise-rendimento`, `analise-bloom`, `analise-viscosidade`, `analise-umidade`.
Cada uma carrega apenas o específico do atributo: método de medição e
**incerteza/repetibilidade do ensaio**, variáveis de processo suspeitas em ordem
de prioridade, armadilhas conhecidas. Depois delega ao método.

A incerteza de medição é decisiva: se a repetibilidade do ensaio de Bloom é da
ordem de ±15 g, um modelo com RMSE de 12 g está dentro do ruído do próprio
laboratório e não representa capacidade preditiva. A skill obriga essa comparação.

### Gabaritos

`_gabaritos/contexto-processo.md` e `_gabaritos/analise-atributo.md` são as
matrizes que `novo-processo` instancia. O pacote gelatina é a primeira
instanciação e serve de exemplo de referência.

## Convenções

Padrões que fazem o conjunto se manter organizado ao crescer:

- **Nomes** em português, kebab-case, verbo ou substantivo de domínio.
- **Frontmatter** com `name` e `description`. A `description` das skills de
  atributo e de `analise-causa-raiz` é redigida para disparar por fala do
  engenheiro; a das skills de método e de base, para invocação por outra skill.
  Isso evita competição de trigger e seleção errada.
- **Blocos `<<PREENCHER>>`** explícitos e concentrados no topo do arquivo, nunca
  diluídos no texto. Só existem em skills de pacote de processo.
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
6. "O dado não sustenta essa pergunta" é resposta válida e obrigatória quando for
   o caso.
7. Dado truncado por limite de ferramenta é declarado, nunca analisado em
   silêncio.

## Onboarding de um novo processo

O procedimento que a skill `novo-processo` executa:

1. Preencher `contexto-processo` a partir do gabarito: etapas, variáveis,
   unidades, faixas, unidade de análise, relações causais conhecidas.
2. Preencher `references/ferramentas.md` mapeando os quatro aliases para as
   ferramentas reais daquele agente.
3. Preencher `references/fontes.md` com worksheets SEEQ, planilhas e relatórios.
4. Instanciar uma `analise-<atributo>` por atributo relevante a partir do
   gabarito, informando método de medição e incerteza.
5. Validar com uma pergunta real de ponta a ponta antes de liberar aos demais
   engenheiros.

Nenhum passo toca o núcleo.

## Fora de escopo

- Criação ou alteração do agente no Copilot Studio, dos MCPs e das fontes de
  dados — já feitos pelo usuário.
- Implantação de alarmes, modelos ou setpoints em qualquer sistema. O agente
  especifica; o engenheiro implanta.
- Skills para outros públicos (operação, gestão).
