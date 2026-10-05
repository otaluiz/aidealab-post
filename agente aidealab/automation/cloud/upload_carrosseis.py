"""Sobe para o Drive (Clientes/aidealab/04-Carrosseis) os carrosséis gerados pela rotina e grava o estado do Drive.

Etapa fixa do workflow `entregar.yml`: a rotina (claude.ai) não acessa o Drive. Para cada pasta em
`agente aidealab/clientes/aidealab/carrosseis/<slug>/` com `png/metadata.json` em status "rascunho",
cria `04-Carrosseis/<slug>/` e envia os PNGs, o metadata.json e o legenda.md. Pula slugs que já
existem em 04, em 06-Aprovados-para-Postar/FILA ou em 06-Aprovados-para-Postar/POSTADOS.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from drive_helper import get_service  # noqa: E402
from googleapiclient.http import MediaFileUpload  # noqa: E402

PASTA = "application/vnd.google-apps.folder"
RAIZ = Path(__file__).resolve().parents[2] / "clientes" / "aidealab" / "carrosseis"


def filhos(svc, pai):
    q = f"'{pai}' in parents and trashed = false and mimeType = '{PASTA}'"
    r = svc.files().list(q=q, fields="files(id,name)", pageSize=1000).execute()
    return {f["name"]: f["id"] for f in r["files"]}


def achar(svc, caminho):
    atual = "root"
    for nome in caminho.split("/"):
        atual = filhos(svc, atual).get(nome) or sys.exit(f"pasta não encontrada no Drive: {caminho} ({nome})")
    return atual


def main():
    svc = get_service()
    destino = achar(svc, "Clientes/aidealab/04-Carrosseis")
    seis = achar(svc, "Clientes/aidealab/06-Aprovados-para-Postar")
    subs = filhos(svc, seis)
    fila = sorted(filhos(svc, subs["FILA"])) if "FILA" in subs else []
    postados = sorted(filhos(svc, subs["POSTADOS"])) if "POSTADOS" in subs else []
    ja = set(filhos(svc, destino)) | set(fila) | set(postados)
    enviados = 0
    for d in sorted(RAIZ.iterdir()) if RAIZ.exists() else []:
        meta = d / "png" / "metadata.json"
        if not meta.exists() or d.name in ja:
            continue
        if json.loads(meta.read_text(encoding="utf-8")).get("status") != "rascunho":
            continue
        pasta = svc.files().create(body={"name": d.name, "mimeType": PASTA, "parents": [destino]}, fields="id").execute()["id"]
        arquivos = sorted((d / "png").iterdir()) + ([d / "legenda.md"] if (d / "legenda.md").exists() else [])
        for f in arquivos:
            svc.files().create(body={"name": f.name, "parents": [pasta]}, media_body=MediaFileUpload(str(f), resumable=True), fields="id").execute()
        print("enviado:", d.name, len(arquivos), "arquivos")
        enviados += 1
    print("total enviados:", enviados)
    # estado do Drive para a rotina (regra de lote e temas já usados), commitado pelo workflow
    # 04 só tem rascunho: aprovar = mover a pasta para 06/FILA
    estado = {"rascunhos_04": sorted(filhos(svc, destino)), "fila": fila, "postados": postados}
    (Path(__file__).parent / "estado-drive.json").write_text(json.dumps(estado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("estado:", {k: len(v) for k, v in estado.items()})


if __name__ == "__main__":
    main()
