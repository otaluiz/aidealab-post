# Automação em nuvem (GitHub Actions) — setup

Esta pasta faz a `criar-post`/`criar-flyer` rodarem sozinhas todo dia/semana
num runner do GitHub Actions, sem depender do computador local ligado (a
rotina antiga, `agente aidealab/automation/run-daily-carousel.ps1` +
Windows Task Scheduler, continua funcionando à parte se você quiser manter
as duas).

Workflows: `.github/workflows/criar-post-diario.yml` (1 carrossel/execução, 8h
BRT) e `.github/workflows/criar-flyer-semanal.yml` (1 flyer/semana, segunda
8h BRT). Os dois usam o modelo **Haiku** por padrão — decisão explícita de
custo, não é a mesma coisa que a rotina local (que usa Sonnet). Se algum
carrossel sair com qualidade abaixo do esperado, o primeiro ajuste a tentar é
trocar `--model claude-haiku-4-5-20251001` por `--model claude-sonnet-5` no
respectivo `.yml`, antes de mexer nos prompts.

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
