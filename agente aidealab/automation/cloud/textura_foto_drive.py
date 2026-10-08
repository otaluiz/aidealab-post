"""Refaz as texturas do hook, do CTA e do slide 3 (só de texto) nas pastas de 06-Aprovados-para-Postar/FILA e de 04-Carrosseis (aidealab).

Para workflow textura-foto-drive.yml (GitHub Actions, credenciais do Drive nos secrets). Aplica a configuração atual
do tema ("textura_foto" só fora do texto, "textura_slide" no slide inteiro) sempre a partir da versão LIMPA de cada
slide: a última revisão do Drive de antes de LIMPO (antes de qualquer textura) ou, se o arquivo é mais novo, a
primeira revisão. Rascunho de 04 que existe em clientes/aidealab/carrosseis/<slug>/png sobe o PNG do repo (já
renderizado com as texturas). Pula pasta cujo metadata já tem a configuração atual. Sobe como nova revisão do mesmo
arquivo, grava as marcas no metadata e copia para a fila do repo (casada por carousel_id), que o workflow commita.
Uso: textura_foto_drive.py [--dry-run]
"""
import io
import json
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[2]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(REPO / "motor"))
from drive_helper import get_service  # noqa: E402
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload  # noqa: E402
from PIL import Image  # noqa: E402
from textura_foto import aplicar, aplicar_slide  # noqa: E402
from upload_carrosseis import achar, filhos  # noqa: E402

LIMPO = "2026-10-06T18:45:00Z"  # 1º commit de textura: revisões de antes disso são os slides limpos
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


def limpa(svc, fid):
    revs = svc.revisions().list(fileId=fid, fields="revisions(id,modifiedTime)", pageSize=200).execute().get("revisions", [])
    if not revs:
        return baixar(svc.files().get_media(fileId=fid))
    antes = [r for r in revs if r["modifiedTime"] < LIMPO]
    r = max(antes, key=lambda r: r["modifiedTime"]) if antes else min(revs, key=lambda r: r["modifiedTime"])
    return baixar(svc.revisions().get_media(fileId=fid, revisionId=r["id"]))


def slide3_texto(meta):
    t = (meta.get("template") or "").split("-")
    return len(meta.get("slides", [])) > 3 and len(t) > 2 and t[2] in ("T2", "T2c", "T3")


def main():
    svc = get_service()
    tema = json.loads(TEMA.read_text(encoding="utf-8"))
    foto, slide = tema.get("textura_foto") or {}, tema.get("textura_slide") or {}
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
        if meta.get("postado") or not meta.get("slides"):
            continue
        if meta.get("textura_foto") == foto and meta.get("textura_slide") == slide and not meta.get("halftone"):
            continue
        novos = {}
        alvos = [("hook", meta["slides"][0]), ("cta", meta["slides"][-1])]
        if slide3_texto(meta):
            alvos.append(("slide3", meta["slides"][2]))
        for papel, s in alvos:
            arq = s["arquivo"]
            if arq not in fs:
                continue
            render = RAIZ / nome[3:] / "png" / arq
            out = tmp / f"{nome.replace('/', '_')}_{arq}"
            if nome.startswith("04/") and render.exists():
                out.write_bytes(render.read_bytes())
            else:
                im = Image.open(io.BytesIO(limpa(svc, fs[arq]))).convert("RGB")
                if foto.get(papel):
                    im = aplicar_slide(im, foto[papel])
                if slide.get(papel):
                    im = aplicar(im, slide[papel])
                im.save(out)
            novos[arq] = out
        if not novos:
            continue
        meta.pop("halftone", None)
        meta["textura_foto"], meta["textura_slide"] = foto, slide
        mj = tmp / f"{nome.replace('/', '_')}_metadata.json"
        mj.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"TEXTURA  {nome}: {', '.join(novos)}")
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
            rm["textura_foto"], rm["textura_slide"] = foto, slide
            (d / "metadata.json").write_text(json.dumps(rm, ensure_ascii=False, indent=2), encoding="utf-8")
        feitos += 1
    print(f"pastas atualizadas: {feitos}")


if __name__ == "__main__":
    main()
