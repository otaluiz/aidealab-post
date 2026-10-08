"""Sobe para o Drive (Clientes/aidealab/04-Carrosseis) os carrosséis gerados pela rotina e grava o estado do Drive.

Etapa fixa do workflow `entregar.yml`: a rotina (claude.ai) não acessa o Drive. Para cada pasta em
`agente aidealab/clientes/aidealab/carrosseis/<slug>/` com `png/metadata.json` em status "rascunho",
cria `04-Carrosseis/<slug>/` e envia os PNGs, o metadata.json e o legenda.md. Se o slug já existe em 04
(rascunho re-renderizado), substitui só os arquivos cujo md5 mudou. Nunca toca em
06-Aprovados-para-Postar/FILA nem em 06-Aprovados-para-Postar/POSTADOS.
"""
import hashlib
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


def sincronizar(svc, pasta, arquivos):
    """Substitui no Drive os arquivos com md5 diferente do local e cria os que faltam. Devolve quantos mudaram."""
    r = svc.files().list(q=f"'{pasta}' in parents and trashed = false", fields="files(id,name,md5Checksum)", pageSize=1000).execute()
    remotos = {f["name"]: f for f in r["files"]}
    mudados = 0
    for f in arquivos:
        md5 = hashlib.md5(f.read_bytes()).hexdigest()
        atual = remotos.get(f.name)
        if atual and atual.get("md5Checksum") == md5:
            continue
        media = MediaFileUpload(str(f), resumable=True)
        if atual:
            svc.files().update(fileId=atual["id"], media_body=media).execute()
        else:
            svc.files().create(body={"name": f.name, "parents": [pasta]}, media_body=media, fields="id").execute()
        mudados += 1
    return mudados


def main():
    svc = get_service()
    destino = achar(svc, "Clientes/aidealab/04-Carrosseis")
    seis = achar(svc, "Clientes/aidealab/06-Aprovados-para-Postar")
    subs = filhos(svc, seis)
    fila = sorted(filhos(svc, subs["FILA"])) if "FILA" in subs else []
    postados = sorted(filhos(svc, subs["POSTADOS"])) if "POSTADOS" in subs else []
    em04 = filhos(svc, destino)
    fechados = set(fila) | set(postados)
    enviados = 0
    for d in sorted(RAIZ.iterdir()) if RAIZ.exists() else []:
        meta = d / "png" / "metadata.json"
        if not meta.exists() or d.name in fechados:
            continue
        if json.loads(meta.read_text(encoding="utf-8")).get("status") != "rascunho":
            continue
        arquivos = sorted((d / "png").iterdir()) + ([d / "legenda.md"] if (d / "legenda.md").exists() else [])
        if d.name in em04:
            n = sincronizar(svc, em04[d.name], arquivos)
            if n:
                print("atualizado:", d.name, n, "arquivos")
            continue
        pasta = svc.files().create(body={"name": d.name, "mimeType": PASTA, "parents": [destino]}, fields="id").execute()["id"]
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
