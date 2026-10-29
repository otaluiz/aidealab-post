"""Motion da fila: item pendente sem vídeo em todos os slides é renderizado no motion atual (motor/motion/motion.py).

Etapa do `entregar.yml`, depois do sync_fila_cloud.py: aprovado que entra na fila sem render no repo (carrossel antigo
do Drive) não vai mais para o Instagram como PNG estático nem com o vídeo velho da pasta do Drive. Sem foto limpa
(`limpas/`), o banco_match.py procura no banco img-ref antes do render. Se o render falhar, o item segue sem vídeo e
o publish_next posta os PNGs.
Uso: motion_fila.py [--dry-run]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
QUEUE = AQUI.parents[1] / "skills" / "post-instagram" / "queue"
MOTION = AQUI.parents[2] / "motor" / "motion"
DRY = "--dry-run" in sys.argv


def sem_video(mf):
    meta = json.loads(mf.read_text(encoding="utf-8-sig"))
    return not meta.get("postado") and not all(s.get("video") and (mf.parent / s["video"]).exists() for s in meta["slides"])


def main():
    faltam = [mf.parent for mf in sorted(QUEUE.glob("FILA-SEMANA-*/02-carrossel/*/metadata.json")) if sem_video(mf)]
    if not faltam:
        print("motion da fila: todos os pendentes já têm vídeo")
        return
    print("motion da fila:", ", ".join(d.name for d in faltam))
    if DRY:
        return
    if not shutil.which("ffmpeg"):
        subprocess.run("sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg", shell=True, check=True)
    subprocess.run(["bash", str(AQUI / "setup-motor.sh")], check=True)
    for fila in sorted({d.parent for d in faltam if not (d / "limpas").is_dir()}):
        subprocess.run([sys.executable, str(MOTION / "banco_match.py"), str(fila), "--faltando"], check=False)
    falhas = [d.name for d in faltam if subprocess.run([sys.executable, str(MOTION / "motion.py"), str(d)]).returncode]
    if falhas:
        sys.exit(f"motion falhou (vão com os PNGs): {', '.join(falhas)}")


if __name__ == "__main__":
    main()
