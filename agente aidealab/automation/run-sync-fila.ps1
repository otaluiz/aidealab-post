# Ponte Drive -> fila do repo (post automático na nuvem). Tarefa "aidealab-sync-fila" (de hora em hora e no logon).
$ErrorActionPreference = "Stop"
$repo = "D:\claude\aidealab-fila"
$logDir = Join-Path $repo "agente aidealab\automation\logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("sync-fila-{0}.log" -f (Get-Date -Format "yyyy-MM-dd"))
Set-Location $repo
& {
    "=== $(Get-Date -Format s)"
    git pull --ff-only --quiet
    python "agente aidealab\automation\sync_fila_drive.py"
    git add -- "agente aidealab/skills/post-instagram/queue"
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        git commit --quiet -m "chore(post-instagram): sincroniza fila com o Drive (06/FILA, 06/POSTADOS) [skip ci]"
        git push --quiet
    }
} *>&1 | Tee-Object -FilePath $log -Append
