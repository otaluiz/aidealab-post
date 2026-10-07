"""Refaz a textura do hook e do CTA nas pastas de 06-Aprovados-para-Postar/FILA e de 04-Carrosseis (aidealab), só na foto.

Para workflow textura-foto-drive.yml (GitHub Actions, credenciais do Drive nos secrets). Por pasta:
- metadata com "textura_foto" -> já feita, pula.
- metadata com o legado "halftone": true (halftone no slide inteiro, texto junto) -> baixa do histórico do Drive a
  última revisão do 1º e do último slide de antes da marca (modifiedTime do metadata.json - 5 min = versão limpa).
- sem marca -> usa o arquivo atual.
Rascunho de 04 que existe em clientes/aidealab/carrosseis/<slug>/png (renderizado com a textura_foto) sobe o PNG do
repo. Senão aplica textura_foto.aplicar_slide (texto protegido por máscara) conforme "textura_foto" do tema, sobe como nova
revisão do mesmo arquivo e grava "textura_foto" no metadata. A mesma imagem vai para a cópia na fila do repo
(queue/FILA-SEMANA-1/02-carrossel/*, casada por carousel_id), que o workflow commita.
Uso: textura_foto_drive.py [--dry-run]
"""
import io
import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[2]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(REPO / "motor"))
from drive_helper import get_service  # noqa: E402
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload  # noqa: E402
from PIL import Image  # noqa: E402
from textura_foto import aplicar_slide  # noqa: E402
from upload_carrosseis import achar, filhos  # noqa: E402

TEMA = REPO / "agente aidealab" / "clientes" / "aidealab" / "design-system" / "tema" / "tema.json"
RAIZ = REPO / "agente aidealab" / "clientes" / "aidealab" / "carrosseis"
QUEUE = REPO / "agente aidealab" / "skills" / "post-instagram" / "queue"
DRY = "--dry-run" in sys.argv


def baixar(req):
    buf = io.BytesIO()
    d = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = d.next_chunk()
    return buf.getvalue()


def arquivos(svc, pasta):
    r = svc.files().list(q=f"'{pasta}' in parents and trashed = false", fields="files(id,name)", pageSize=200).execute()
    return {f["name"]: f["id"] for f in r["files"]}


def limpa(svc, fid, corte):
    revs = svc.revisions().list(fileId=fid, fields="revisions(id,modifiedTime)", pageSize=200).execute().get("revisions", [])
    antes = [r for r in revs if r["modifiedTime"] < corte]
    if not antes:
        return None
    return baixar(svc.revisions().get_media(fileId=fid, revisionId=max(antes, key=lambda r: r["modifiedTime"])["id"]))


def main():
    svc = get_service()
    cfg = json.loads(TEMA.read_text(encoding="utf-8"))["textura_foto"]
    fila = filhos(svc, filhos(svc, achar(svc, "Clientes/aidealab/06-Aprovados-para-Postar"))["FILA"])
    fila.update({f"04/{k}": v for k, v in filhos(svc, achar(svc, "Clientes/aidealab/04-Carrosseis")).items()})
    repo = {}
    for mf in QUEUE.glob("FILA-SEMANA-*/02-carrossel/*/metadata.json"):
        repo[json.loads(mf.read_text(encoding="utf-8")).get("carousel_id")] = mf.parent
    tmp = Path(tempfile.mkdtemp())
    feitos = 0
    for nome, pid in sorted(fila.items()):
        fs = arquivos(svc, pid)
        if "metadata.json" not in fs:
            continue
        meta = json.loads(baixar(svc.files().get_media(fileId=fs["metadata.json"])).decode("utf-8-sig"))
        if meta.get("textura_foto") or meta.get("postado") or not meta.get("slides"):
            continue
        legado = bool(meta.get("halftone"))
        corte = None
        if legado:  # o halftone e a marca no metadata foram gravados juntos: revisões de antes disso são limpas
            mt = svc.files().get(fileId=fs["metadata.json"], fields="modifiedTime").execute()["modifiedTime"]
            corte = (datetime.fromisoformat(mt.replace("Z", "+00:00")) - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        novos = {}
        for papel, s in (("hook", meta["slides"][0]), ("cta", meta["slides"][-1])):
            arq = s["arquivo"]
            if not cfg.get(papel) or arq not in fs:
                continue
            render = RAIZ / nome[3:] / "png" / arq
            if nome.startswith("04/") and render.exists():
                novos[arq] = render
                continue
            dado = limpa(svc, fs[arq], corte) if legado else baixar(svc.files().get_media(fileId=fs[arq]))
            if dado is None:
                print(f"PULA     {nome}/{arq}: sem revisão de antes de {corte}")
                continue
            out = tmp / f"{nome.replace('/', '_')}_{arq}"
            aplicar_slide(Image.open(io.BytesIO(dado)), cfg[papel]).save(out)
            novos[arq] = out
        if not novos:
            continue
        meta.pop("halftone", None)
        meta["textura_foto"] = cfg
        mj = tmp / f"{nome.replace('/', '_')}_metadata.json"
        mj.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"TEXTURA  {nome}: {', '.join(novos)}" + (" (de revisão limpa)" if legado else ""))
        if DRY:
            continue
        for arq, f in novos.items():
            svc.files().update(fileId=fs[arq], media_body=MediaFileUpload(str(f), mimetype="image/png")).execute()
        svc.files().update(fileId=fs["metadata.json"], media_body=MediaFileUpload(str(mj), mimetype="application/json")).execute()
        d = repo.get(meta.get("carousel_id"))
        if d:  # mesma imagem na fila do repo (a publicação lê de lá)
            for arq, f in novos.items():
                (d / arq).write_bytes(f.read_bytes())
            rm = json.loads((d / "metadata.json").read_text(encoding="utf-8"))
            rm.pop("halftone", None)
            rm["textura_foto"] = cfg
            (d / "metadata.json").write_text(json.dumps(rm, ensure_ascii=False, indent=2), encoding="utf-8")
        feitos += 1
    print(f"pastas atualizadas: {feitos}")


if __name__ == "__main__":
    main()
