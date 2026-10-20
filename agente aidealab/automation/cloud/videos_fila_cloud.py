"""Sobe para o Drive (06-Aprovados-para-Postar/FILA/<pasta>) os vídeos do carrossel animado da fila do repo.

Os itens da fila ganham `slide-NN.mp4` + `slides[].video` no repo (motor/motion/motion.py). Este passo do
`entregar.yml` casa cada item pendente do repo com a pasta de 06/FILA pelo `carousel_id` e envia os mp4 e o
metadata.json (só o que mudou, por md5). Não mexe em POSTADOS nem em item já postado.
Uso: videos_fila_cloud.py [--dry-run]
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from drive_helper import get_service  # noqa: E402
from sync_fila_cloud import arquivos, baixar  # noqa: E402
from upload_carrosseis import achar, filhos, sincronizar  # noqa: E402

QUEUE = AQUI.parents[1] / "skills" / "post-instagram" / "queue"
DRY = "--dry-run" in sys.argv


def main():
    svc = get_service()
    fila_id = filhos(svc, achar(svc, "Clientes/aidealab/06-Aprovados-para-Postar"))["FILA"]
    no_drive = {}
    for nome, pid in filhos(svc, fila_id).items():
        fs = arquivos(svc, pid)
        if "metadata.json" in fs:
            no_drive[json.loads(baixar(svc, fs["metadata.json"]).decode("utf-8-sig")).get("carousel_id")] = (nome, pid)
    for mf in sorted(QUEUE.glob("FILA-SEMANA-*/02-carrossel/*/metadata.json")):
        meta = json.loads(mf.read_text(encoding="utf-8-sig"))
        videos = [mf.parent / s["video"] for s in meta.get("slides", []) if s.get("video")]
        alvo = no_drive.get(meta.get("carousel_id"))
        if meta.get("postado") or not videos or not alvo or not all(v.exists() for v in videos):
            continue
        if DRY:
            print(f"VIDEOS   {mf.parent.name} -> 06/FILA/{alvo[0]} ({len(videos)} mp4)")
            continue
        n = sincronizar(svc, alvo[1], videos + [mf])
        if n:
            print(f"VIDEOS   {mf.parent.name} -> 06/FILA/{alvo[0]}: {n} arquivos")


if __name__ == "__main__":
    main()
