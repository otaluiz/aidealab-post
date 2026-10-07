#!/usr/bin/env python3
"""Ponte entre o Drive (aprovação humana) e a fila do repo (publicação na nuvem).

Pastas no Drive (Clientes/aidealab):
  04-Carrosseis/                       rascunhos, aguardando aprovação
  06-Aprovados-para-Postar/FILA/       aprovados, esperando a vez (ordem = ordem_fila)
  06-Aprovados-para-Postar/POSTADOS/   já publicados (metadata com post_id)

A cada execução:
  1. Item da fila do repo com postado:true -> a pasta correspondente sai de FILA para
     POSTADOS no Drive, com post_id/postado_em no metadata. Itens postados ANTES de hoje
     saem da fila do repo e o id vai para _arquivo-postados.json (os de hoje ficam, porque
     o publish_next usa eles para garantir 1 post por dia).
  Pastas de FILA sem "textura_foto" no metadata ganham a textura só na foto do hook e do CTA (no próprio Drive).
  2. Pastas de FILA que ainda não estão na fila nem no arquivo de postados entram na fila
     do repo como FILA-SEMANA-1/02-carrossel/Dia<N>-<slug>, até MAX_PENDENTES pendentes.

Só mexe em arquivos; o commit/push fica com run-sync-fila.ps1.
Uso: sync_fila_drive.py [--dry-run]
"""
import json
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DRIVE = Path(r"C:\Users\luizr\Meu Drive (aidealabbr@gmail.com)\Clientes\aidealab\06-Aprovados-para-Postar")
FILA, POSTADOS = DRIVE / "FILA", DRIVE / "POSTADOS"
REPO = Path(__file__).resolve().parents[2]
QUEUE = REPO / "agente aidealab" / "skills" / "post-instagram" / "queue"
DESTINO = QUEUE / "FILA-SEMANA-1" / "02-carrossel"
LEDGER = QUEUE / "_arquivo-postados.json"
MAX_PENDENTES = 10  # ponytail: buffer fixo de ~10 dias com o PC desligado; aumentar se precisar
CUIABA = timezone(timedelta(hours=-4))
DIA_RE = re.compile(r"^Dia(\d+)")
DRY = "--dry-run" in sys.argv
sys.path.insert(0, str(REPO / "motor"))


TEMA = REPO / "agente aidealab" / "clientes" / "aidealab" / "design-system" / "tema" / "tema.json"


def aplicar_textura(d, meta):
    """Textura só na foto do hook (1º slide) e do CTA (último), conforme "textura_foto" do tema (o texto fica limpo).
    Idempotente via meta["textura_foto"]. Pastas com o legado meta["halftone"] (slide inteiro) ficam para o workflow
    textura-foto-drive.yml, que recupera a versão limpa no histórico do Drive."""
    if meta.get("textura_foto") or meta.get("halftone") or meta.get("postado") \
            or meta.get("cliente", "aidealab") != "aidealab" or not meta.get("slides"):
        return False
    from PIL import Image
    try:
        from textura_foto import aplicar_slide
    except ImportError as e:  # scipy ausente no PC: não quebra a sincronização
        print(f"AVISO    textura pulada ({e}); instale: pip install scipy")
        return False
    cfg = ler(TEMA).get("textura_foto") or {}
    for papel, s in (("hook", meta["slides"][0]), ("cta", meta["slides"][-1])):
        if cfg.get(papel):
            aplicar_slide(Image.open(d / s["arquivo"]), cfg[papel]).save(d / s["arquivo"])
    meta["textura_foto"] = cfg
    return True


def ler(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def gravar(p, data):
    if not DRY:
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def ids_de(meta):
    return {meta.get(k) for k in ("carousel_id", "origem_carousel_id") if meta.get(k)}


def slug(nome):
    return re.sub(r"[^A-Za-z0-9_-]+", "-", nome).strip("-")


def dia_cuiaba(iso):
    dt = datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)  # publish_next grava utcnow sem fuso
    return dt.astimezone(CUIABA).date()


def main():
    ledger = ler(LEDGER) if LEDGER.exists() else {"ultimo_dia": 0, "carousel_ids": []}
    arquivados = set(ledger["carousel_ids"])
    fila_drive = {}
    for d in sorted(p for p in FILA.iterdir() if p.is_dir()) if FILA.exists() else []:
        if (d / "metadata.json").exists():
            fila_drive[ler(d / "metadata.json").get("carousel_id")] = d

    itens = []
    for mf in QUEUE.glob("FILA-SEMANA-*/02-carrossel/*/metadata.json"):
        m = DIA_RE.match(mf.parent.name)
        itens.append({"dir": mf.parent, "meta": ler(mf), "dia": int(m.group(1)) if m else 0})
    hoje = datetime.now(CUIABA).date()

    # 1. postados: Drive FILA -> POSTADOS; repo: arquiva os de dias anteriores
    for it in itens:
        meta = it["meta"]
        if not meta.get("postado"):
            continue
        for cid in ids_de(meta):
            d = fila_drive.pop(cid, None)
            if d:
                dm = ler(d / "metadata.json")
                dm.update(postado=True, postado_em=meta.get("postado_em"), post_id=meta.get("post_id"), status="postado")
                gravar(d / "metadata.json", dm)
                print(f"POSTADO  {d.name} -> POSTADOS (post {meta.get('post_id')})")
                if not DRY:
                    shutil.move(str(d), str(POSTADOS / d.name))
        if meta.get("postado_em") and dia_cuiaba(meta["postado_em"]) < hoje:
            arquivados |= ids_de(meta)
            ledger["ultimo_dia"] = max(ledger["ultimo_dia"], it["dia"])
            print(f"ARQUIVA  {it['dir'].name} (fila do repo)")
            if not DRY:
                shutil.rmtree(it["dir"])
            it["arquivado"] = True

    # itens arquivados antes (ledger) que ainda estão na FILA do Drive também vão para POSTADOS
    for cid in list(fila_drive):
        if cid in arquivados:
            d = fila_drive.pop(cid)
            print(f"POSTADO  {d.name} -> POSTADOS (já no arquivo de postados)")
            if not DRY:
                shutil.move(str(d), str(POSTADOS / d.name))

    # aprovados no Drive (FILA) ganham a textura (só na foto) no hook e no CTA, para visualizar lá também
    for d in fila_drive.values():
        dm = ler(d / "metadata.json")
        if not DRY and all((d / s["arquivo"]).exists() for s in dm.get("slides", [])) and aplicar_textura(d, dm):
            gravar(d / "metadata.json", dm)
            print(f"TEXTURA  {d.name} (Drive)")

    # 2. aprovados novos entram na fila do repo
    vivos = [it for it in itens if not it.get("arquivado")]
    na_fila = set().union(*[ids_de(it["meta"]) for it in vivos]) if vivos else set()
    pendentes = sum(1 for it in vivos if not it["meta"].get("postado"))
    prox = max([ledger["ultimo_dia"], *[it["dia"] for it in vivos]]) + 1
    novos = [(cid, d) for cid, d in fila_drive.items() if cid not in na_fila and cid not in arquivados]
    novos.sort(key=lambda x: (ler(x[1] / "metadata.json").get("ordem_fila") or 999, x[1].name))
    for cid, d in novos:
        if pendentes >= MAX_PENDENTES:
            break
        meta = ler(d / "metadata.json")
        faltando = [s["arquivo"] for s in meta.get("slides", []) if not (d / s["arquivo"]).exists()]
        if faltando or not meta.get("legenda"):
            print(f"PULA     {d.name}: slides faltando {faltando} ou sem legenda")
            continue
        alvo = DESTINO / f"Dia{prox}-{slug(d.name)}"
        print(f"ENFILEIRA {d.name} -> {alvo.name}")
        if not DRY:
            alvo.mkdir(parents=True)
            for s in meta["slides"]:
                shutil.copy2(d / s["arquivo"], alvo / s["arquivo"])
            meta.update(postado=False, status="aprovado")
            aplicar_textura(alvo, meta)
            gravar(alvo / "metadata.json", meta)
        prox += 1
        pendentes += 1

    ledger["carousel_ids"] = sorted(arquivados)
    gravar(LEDGER, ledger)
    print(f"pendentes na fila do repo: {pendentes}")


if __name__ == "__main__":
    main()
