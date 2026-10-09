# Automação em nuvem (GitHub Actions) — setup

Esta pasta faz a `criar-post`/`criar-flyer` rodarem sozinhas todo dia/semana
num runner do GitHub Actions, sem depender do computador local ligado (a
rotina antiga, `agente aidealab/automation/run-daily-carousel.ps1` +
Windows Task Scheduler, continua funcionando à parte se você quiser manter
as duas).

Geração: rotina do Claude na nuvem "aidealab - carrossel diário 8h" (claude.ai, com o
conector Higgsfield), que segue `daily-carousel-prompt-cloud.txt`: 1 carrossel por dia no
MOTOR NOVO (`motor/` = cópia do carrossel-engine, tema
`agente aidealab/clientes/aidealab/design-system/tema/`), capa e CTA com os personagens
@luizota/@wel no Soul 2.0 e slide 2 no gpt_image_2_5. Ela commita numa branch própria.
Entrega: `.github/workflows/entregar.yml` leva a branch para a main, sobe os rascunhos para
`04-Carrosseis` (`upload_carrosseis.py`) e grava `estado-drive.json` (04, 06/FILA,
06/POSTADOS), que a rotina lê para a regra de lote (pula com 3+ rascunhos em 04). A skill
`criar-post` e o `render-engine` antigo não são mais usados. Rotina de flyer removida em
2026-10-05. Quando o carrossel-engine mudar, copie de novo os arquivos para `motor/`.

## O que falta pra ligar (nada disso eu consigo fazer por você)

### 1. Secret `CLAUDE_CODE_OAUTH_TOKEN` (usa sua assinatura, não API paga)

Não precisa criar conta de API nova nem pagar por token separadamente — os
workflows autenticam com a **mesma assinatura Claude/Claude Code** que você já
usa localmente (Pro/Max/Team), via um token OAuth de longa duração (1 ano).

Na sua máquina, onde você já está logado no Claude Code:
```bash
claude setup-token
```
Isso abre o navegador pra você aprovar (mesmo fluxo do `/login`) e imprime o
token no terminal **uma única vez** — copie na hora, ele não fica salvo em
arquivo local. Cole esse valor como secret `CLAUDE_CODE_OAUTH_TOKEN`
(Settings → Secrets and variables → Actions → New repository secret).

**Atenção a duas coisas:**
- Esse token expira em **1 ano** — sem aviso automático em CI, então marque
  um lembrete pra gerar um novo antes disso (`claude setup-token` de novo,
  atualiza o secret).
- As chamadas da automação **consomem a mesma janela de uso de 5 horas da
  sua assinatura** que o uso interativo normal (não é uma cota separada tipo
  API paga). Com Haiku e só 1 carrossel/execução + 1 flyer/semana o consumo deve
  ser baixo, mas se você usar o Claude Code pesado no mesmo horário do cron
  (8h BRT), pode competir pela mesma janela. Se notar isso, o ajuste é mudar
  o horário do cron nos `.yml` (`cron: "0 11 * * *"`) pra um horário que você
  não usa.

### 2. Secret `AIDEALAB_DRIVE_FOLDER_ID`

O ID da pasta `Clientes/aidealab` no Drive. No fim de 2026-09-21, essa pasta
tinha o ID `1GWcKhQDADU6M-xXBYjTwaeoKwqkjfK5D` (confirme abrindo a pasta no
navegador e olhando o final da URL — `drive.google.com/drive/folders/<ID>` —
antes de usar, IDs de pasta não mudam sozinhos mas é bom confirmar).

### 3. Credenciais do Google Drive (3 secrets) — a parte que dá mais trabalho

O MCP do Google Drive que você usa interativamente (conectado à sua conta
Anthropic) **não existe** dentro de um runner do GitHub Actions — não tem
como "levar" essa sessão pra lá. Em vez disso, `drive_helper.py` fala direto
com a Google Drive API usando um `refresh_token` OAuth que você gera **uma
vez, localmente**, e que fica salvo como secret pra sempre (até você revogar).
Uma Service Account NÃO funciona aqui — Service Account não tem cota de
armazenamento própria em conta Gmail pessoal (dá erro `storageQuotaExceeded`
tentando gravar em "Meu Drive").

**Passo a passo:**

1. Vá em [console.cloud.google.com](https://console.cloud.google.com), crie
   (ou reuse) um projeto.
2. **APIs & Services → Library** → busque "Google Drive API" → **Enable**.
3. **APIs & Services → OAuth consent screen**: tipo **External**; preencha
   nome do app e seu e-mail; em "Test users" adicione
   `aidealabbr@gmail.com`.
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID**,
   tipo **Desktop app** → Create → baixe o JSON (vai chamar algo como
   `client_secret_....json`).
5. Localmente (não no GitHub Actions — precisa abrir navegador), instale as
   libs e rode o script auxiliar desta pasta:
   ```bash
   pip install -r requirements.txt
   mv ~/Downloads/client_secret_*.json agente\ aidealab/automation/cloud/client_secret.json
   cd "agente aidealab/automation/cloud"
   python get_drive_refresh_token.py
   ```
   Uma aba do navegador abre — faça login com `aidealabbr@gmail.com`, clique
   em "Avançar"/"Continuar" no aviso de "app não verificado" (normal, é o seu
   próprio app, uso pessoal) e autorize. O script imprime 3 valores.
6. **Antes de considerar isso pronto**: volte em **OAuth consent screen /
   Audience** no Cloud Console e mude o **Publishing status de "Testing" para
   "In production"** (não precisa completar a verificação do Google, só
   confirmar — válido até 100 usuários, seu caso). **Isso é crítico**: com o
   app em "Testing", o Google **expira o refresh_token sozinho em 7 dias**,
   e a automação para de funcionar silenciosamente uma semana depois de você
   configurar tudo, sem nenhum erro óbvio na hora. Em "In production" o
   token só expira se for revogado ou ficar ~6 meses sem uso (o cron diário
   evita isso).
7. Copie os 3 valores impressos pelo script como secrets do repositório:
   `GOOGLE_DRIVE_CLIENT_ID`, `GOOGLE_DRIVE_CLIENT_SECRET`,
   `GOOGLE_DRIVE_REFRESH_TOKEN` (Settings → Secrets and variables → Actions →
   New repository secret).
8. Apague `client_secret.json` e `drive_token_output.json` localmente depois
   (já estão no `.gitignore`, mas não custa confirmar que não foram
   commitados).

### 4. Fazer o cron existir de verdade

GitHub Actions só agenda (`schedule:`) workflows que estão na **branch
padrão** (main). Esta configuração foi feita numa branch separada — alguém
precisa revisar e dar merge em `main` antes de qualquer coisa disparar
sozinha. Até lá, dá pra testar manualmente via **Actions → (nome do
workflow) → Run workflow** (usa o `workflow_dispatch` já configurado) mesmo
estando numa branch de feature.

## Limitações conhecidas desta configuração inicial

- **Higgsfield não está integrado nesta rotina em nuvem.** O MCP interativo
  não funciona em CI (exige OAuth via navegador); existe uma API REST própria
  da Higgsfield (`api.higgsfield.ai`, autenticação por API key gerada em
  `cloud.higgsfield.ai` — dashboard separado do app principal) que
  teoricamente resolveria isso, mas o endpoint exato do modelo `soul_2` e a
  existência de um equivalente a `remove_background` nela não foram
  confirmados na documentação oficial nesta pesquisa — não quis arriscar
  gastar crédito Higgsfield numa chamada que talvez nem exista. A rotina em
  nuvem roda **100% a partir do banco `img-ref`**, que é o que toda execução
  recente bem-sucedida da skill já faz de qualquer forma. Se quiser habilitar
  geração paga depois, confirme o endpoint em docs.higgsfield.ai e escreva um
  `higgsfield_helper.py` no mesmo espírito do `drive_helper.py` (chamada HTTP
  direta com a API key como secret, nunca MCP).
- **Fonte Tempting não vem instalada no runner.** Ver a nota de fontes dentro
  de cada prompt (`daily-carousel-prompt-cloud.txt` /
  `weekly-flyer-prompt-cloud.txt`) — o carrossel tem uma rede de segurança
  documentada (Playfair Display Italic 900), o flyer NÃO aceita serifada de
  jeito nenhum (regra explícita do cliente) e cai pra Inter sozinho.
- **`--permission-mode dontAsk --permission-prompts none`** são as flags
  recomendadas hoje pra automação não-supervisionada, mas são relativamente
  novas — se o job falhar logo no início com erro de flag desconhecida, troque
  por `--dangerously-skip-permissions` nos dois `.yml` (é o que a rotina
  local já usa, comprovadamente funcional).
- **1 carrossel por execução** (reduzido de 3, que estourava o orçamento de
  turnos/tempo de uma `claude -p` só no Haiku antes de terminar o pipeline
  completo). Pra gerar mais de um por dia, rode o workflow mais de uma vez
  (`workflow_dispatch` manual, ou vários `cron` no mesmo `.yml`) — a
  `concurrency: group: aidealab-criar-post` já serializa as execuções pra
  evitar duas rodadas brigando pela mesma imagem do banco `img-ref` ao mesmo
  tempo.

## Tudo em nuvem (desde 09/10/2026)

| Etapa | Onde | Arquivo |
|---|---|---|
| Nicho no Instagram via **Apify** (segunda 6h BRT) | GitHub Actions `nicho-semanal.yml` | `apify_nicho.py` → `estado-nicho.json` |
| Instagram + tendências do dia (7h30) | `entregar.yml` | `ig_insights.py`, `tendencias.py` |
| Pauta da semana + roteiros de Reels (segunda) e carrossel do dia (8h) | rotina claude.ai | `daily-carousel-prompt-cloud.txt` → `clientes/aidealab/campanha/semanas/`, `clientes/aidealab/roteiro/` |
| Rascunhos → `04-Carrosseis` | `entregar.yml` | `upload_carrosseis.py` |
| Campanha, melhorias e roteiros → Google Docs em `05-Campanhas` e `03-Roteiros` | `entregar.yml` | `docs_drive.py` |
| Aprovados em `06/FILA` → fila do repo; postados → `06/POSTADOS` | `entregar.yml` | `sync_fila_cloud.py` (substitui `sync_fila_drive.py` do Windows) |
| Publicação (intercala personagem e banco) | `post-instagram-cloud.yml` | `publish_next.py` |

Secrets do GitHub: além dos do Drive e do Instagram, **`APIFY_TOKEN`** (token grátis em
console.apify.com/account/integrations). Sem ele o `estado-nicho.json` sai só com `erro` e o resto segue normal.

Com o `sync_fila_cloud.py` rodando, **desligue no Agendador do Windows** as tarefas `run-sync-fila.ps1` e
`run-daily-carousel.ps1` (motor antigo), para não enfileirar em dobro nem gerar carrossel fora da pauta.
