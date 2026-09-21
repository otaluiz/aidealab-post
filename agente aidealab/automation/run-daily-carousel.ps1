# Rotina local diária: gera 3 carrosséis via skill criar-post.
# Disparado pelo Windows Task Scheduler (tarefa "aidealab-criar-post-diario").
$ErrorActionPreference = "Stop"
$repo = "D:\claude\agente aidealab"
$driveRoot = "C:\Users\luizr\Meu Drive (aidealabbr@gmail.com)\Clientes\aidealab"
$promptFile = Join-Path $repo "automation\daily-carousel-prompt.txt"
$logDir = Join-Path $repo "automation\logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir ("run-{0}.log" -f (Get-Date -Format "yyyy-MM-dd_HH-mm-ss"))

Set-Location $repo
$prompt = Get-Content -Raw -Encoding utf8 $promptFile

& claude -p $prompt `
    --dangerously-skip-permissions `
    --add-dir $driveRoot `
    --model claude-sonnet-5 `
    *>&1 | Tee-Object -FilePath $logFile
