"""Versão em nuvem do automation/sync_fila_drive.py: ponte Drive (aprovação humana) -> fila do repo (publicação).

Roda no GitHub Actions (entregar.yml), sem depender do Drive sincronizado no Windows. Mesma regra do script local:
  1. item da fila do repo com postado:true -> a pasta de 06/FILA vai para 06/POSTADOS no Drive (metadata com
     post_id/postado_em). Postados ANTES de hoje saem da fila do repo e o id vai para _arquivo-postados.json.
  2. pastas de 06/FILA que não estão na fila nem no arquivo entram como FILA-SEMANA-1/02-carrossel/Dia<N>-<slug>,
     até MAX_PENDENTES pendentes (o publish_next intercala personagem e banco pelo campo "personagem").
Uso: sync_fila_cloud.py [--dry-run]
"""
import io
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))
from drive_helper import get_service  # noqa: E402
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload  # noqa: E402
from upload_carrosseis import achar, filhos  # noqa: E402
import sync_fila_drive as local  # noqa: E402  (reaproveita fila, ledger, regras e textura)

DRY = "--dry-run" in sys.argv
local.DRY = DRY


def arquivos(svc, pasta):
    r = svc.files().list(q=f"'{pasta}' in parents and trashed = false", fields="files(id,name)", pageSize=1000).execute()
    return {f["name"]: f["id"] for f in r["files"]}


def baixar(svc, fid):
    buf = io.BytesIO(); dl = MediaIoBaseDownload(buf, svc.files().get_media(fileId=fid)); done = False
    while not done:
        _, done = dl.next_chunk()
    return buf.getvalue()


def ler_meta(svc, fs):
    return json.loads(baixar(svc, fs["metadata.json"]).decode("utf-8-sig")) if "metadata.json" in fs else None


CARROSSEIS = AQUI.parents[1] / "clientes" / "aidealab" / "carrosseis"


def render_do_repo(alvo, meta, png):
    """Vídeos do item novo vêm do render mais recente do repo (<carrossel>/png), nunca da cópia do Drive: a pasta
    em 06/FILA guarda o vídeo da época da aprovação (motion antigo). Sem render no repo o item fica sem vídeo e o
    motion_fila.py renderiza no motion atual."""
    for s in meta["slides"]:
        s.pop("video", None)
    meta.pop("formato_motion", None)
    if not png:
        return
    if (png / "limpas").is_dir():  # fotos limpas do motor: o motion_fila não precisa do banco
        shutil.copytree(png / "limpas", alvo / "limpas", dirs_exist_ok=True)
    videos = {s["arquivo"]: s.get("video") for s in local.ler(png / "metadata.json").get("slides", [])}
    if not all(videos.get(s["arquivo"]) and (png / videos[s["arquivo"]]).exists() for s in meta["slides"]):
        return
    for s in meta["slides"]:
        s["video"] = videos[s["arquivo"]]
        shutil.copy2(png / s["video"], alvo / s["video"])
    meta["formato_motion"] = local.ler(png / "metadata.json").get("formato_motion")
    print(f"         vídeos do render do repo ({png.parent.name})")


def main():
    svc = get_service()
    seis = achar(svc, "Clientes/aidealab/06-Aprovados-para-Postar")
    subs = filhos(svc, seis)
    fila_id, postados_id = subs["FILA"], subs["POSTADOS"]
    ledger = local.ler(local.LEDGER) if local.LEDGER.exists() else {"ultimo_dia": 0, "carousel_ids": []}
    arquivados = set(ledger["carousel_ids"])

    fila_drive = {}  # carousel_id -> (nome, folder_id, arquivos, meta)
    for nome, pid in sorted(filhos(svc, fila_id).items()):
        fs = arquivos(svc, pid); meta = ler_meta(svc, fs)
        if meta:
            fila_drive[meta.get("carousel_id")] = (nome, pid, fs, meta)

    itens = []
    for mf in local.QUEUE.glob("FILA-SEMANA-*/02-carrossel/*/metadata.json"):
        m = local.DIA_RE.match(mf.parent.name)
        itens.append({"dir": mf.parent, "meta": local.ler(mf), "dia": int(m.group(1)) if m else 0})
    hoje = datetime.now(local.CUIABA).date()

    def para_postados(nome, pid, fs, dm, meta=None):
        if meta:
            dm.update(postado=True, postado_em=meta.get("postado_em"), post_id=meta.get("post_id"), status="postado")
        print(f"POSTADO  {nome} -> POSTADOS")
        if DRY:
            return
        if meta:
            corpo = MediaIoBaseUpload(io.BytesIO(json.dumps(dm, ensure_ascii=False, indent=2).encode()), "application/json")
            svc.files().update(fileId=fs["metadata.json"], media_body=corpo).execute()
        svc.files().update(fileId=pid, addParents=postados_id, removeParents=fila_id, fields="id").execute()

    # 1. postados
    for it in itens:
        meta = it["meta"]
        if not meta.get("postado"):
            continue
        for cid in local.ids_de(meta):
            if cid in fila_drive:
                nome, pid, fs, dm = fila_drive.pop(cid)
                para_postados(nome, pid, fs, dm, meta)
        if meta.get("postado_em") and local.dia_cuiaba(meta["postado_em"]) < hoje:
            arquivados |= local.ids_de(meta)
            ledger["ultimo_dia"] = max(ledger["ultimo_dia"], it["dia"])
            print(f"ARQUIVA  {it['dir'].name} (fila do repo)")
            if not DRY:
                shutil.rmtree(it["dir"])
            it["arquivado"] = True
    for cid in list(fila_drive):
        if cid in arquivados:
            nome, pid, fs, dm = fila_drive.pop(cid)
            para_postados(nome, pid, fs, dm)

    # 2. aprovados novos entram na fila do repo
    vivos = [it for it in itens if not it.get("arquivado")]
    na_fila = set().union(*[local.ids_de(it["meta"]) for it in vivos]) if vivos else set()
    pendentes = sum(1 for it in vivos if not it["meta"].get("postado"))
    prox = max([ledger["ultimo_dia"], *[it["dia"] for it in vivos]]) + 1
    novos = [v for cid, v in fila_drive.items() if cid not in na_fila and cid not in arquivados]
    novos.sort(key=lambda v: (v[3].get("ordem_fila") or 999, v[0]))
    repo = {}  # carrosséis do motor no repo, por pasta e por carousel_id
    for mp in CARROSSEIS.glob("*/png/metadata.json"):
        repo.setdefault(local.ler(mp).get("carousel_id"), mp.parent)
        repo[mp.parents[1].name] = mp.parent
    for nome, pid, fs, meta in novos:
        if pendentes >= local.MAX_PENDENTES:
            break
        faltando = [s["arquivo"] for s in meta.get("slides", []) if s["arquivo"] not in fs]
        if faltando or not meta.get("legenda"):
            print(f"PULA     {nome}: slides faltando {faltando} ou sem legenda")
            continue
        alvo = local.DESTINO / f"Dia{prox}-{local.slug(nome)}"
        print(f"ENFILEIRA {nome} -> {alvo.name}")
        if not DRY:
            alvo.mkdir(parents=True)
            for s in meta["slides"]:
                (alvo / s["arquivo"]).write_bytes(baixar(svc, fs[s["arquivo"]]))
            meta.update(postado=False, status="aprovado")
            local.aplicar_textura(alvo, meta)
            render_do_repo(alvo, meta, repo.get(nome) or repo.get(meta.get("carousel_id")))
            local.gravar(alvo / "metadata.json", meta)
        prox += 1
        pendentes += 1

    ledger["carousel_ids"] = sorted(arquivados)
    local.gravar(local.LEDGER, ledger)
    print(f"pendentes na fila do repo: {pendentes}")


if __name__ == "__main__":
    main()
