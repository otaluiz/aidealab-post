# Rotina local diária: publica o próximo item aprovado via skill post-instagram.
# Disparado pelo Windows Task Scheduler (tarefa "aidealab-post-instagram-diario").
$ErrorActionPreference = "Stop"
$repo = "D:\claude\agente aidealab"
$script = Join-Path $repo "skills\post-instagram\scripts\publish_next.py"
$logDir = Join-Path $repo "automation\logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir ("run-instagram-{0}.log" -f (Get-Date -Format "yyyy-MM-dd_HH-mm-ss"))

python $script *>&1 | Tee-Object -FilePath $logFile
