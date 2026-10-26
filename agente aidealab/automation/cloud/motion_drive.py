"""Sobe os motion graphics da branch `motion-entrega` para Clientes/aidealab/09 - motion no Drive.

Os motions são feitos numa sessão do Claude na nuvem (repo claude-motion), que não tem as credenciais do Drive.
Ela dá push numa branch `motion-entrega` com `motion-entrega/<Nome>/` (vídeo+sfx .mp4 e trilha .wav); o
`motion-drive.yml` roda este script e apaga a branch, para os vídeos não ficarem no histórico da main.
Cada subpasta vira uma pasta em 09 - motion (mesmo nome); só envia o que mudou (md5).
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from drive_helper import get_service  # noqa: E402
from upload_carrosseis import PASTA, achar, filhos, sincronizar  # noqa: E402

SRC = AQUI.parents[2] / "motion-entrega"


def main():
    svc = get_service()
    raiz = achar(svc, "Clientes/aidealab/09 - motion")
    for d in sorted(p for p in SRC.iterdir() if p.is_dir()):
        pid = filhos(svc, raiz).get(d.name) or svc.files().create(
            body={"name": d.name, "mimeType": PASTA, "parents": [raiz]}, fields="id").execute()["id"]
        n = sincronizar(svc, pid, sorted(f for f in d.iterdir() if f.is_file()))
        print(f"09 - motion/{d.name}: {n} arquivo(s) enviado(s)")


if __name__ == "__main__":
    main()
