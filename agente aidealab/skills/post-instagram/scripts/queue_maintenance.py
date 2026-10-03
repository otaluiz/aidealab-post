#!/usr/bin/env python3
"""Manutenção da fila: quando tudo foi postado, arquiva (apaga) os itens postados.

Os ids dos itens apagados vão para queue/_arquivo-postados.json, para que
list_rascunhos.py não os re-enfileire. `ultimo_dia` guarda o maior DiaNN já usado.

Uso: queue_maintenance.py [--archive]
Saída (stdout, KEY=VALUE, pronta para $GITHUB_OUTPUT): pending, next_dia, archived.
"""
import argparse
import json
import re
import shutil
from pathlib import Path

QUEUE_ROOT = Path(__file__).resolve().parent.parent / "queue"
LEDGER = QUEUE_ROOT / "_arquivo-postados.json"
DIA_RE = re.compile(r"^Dia(\d+)")


def load_items():
    items = []
    for fila in sorted(QUEUE_ROOT.glob("FILA-SEMANA-*")):
        img = fila / "01-Imagem"
        if img.is_dir():
            for mf in img.glob("*.metadata.json"):
                label = mf.name[: -len(".metadata.json")]
                items.append({"label": label, "meta": mf, "files": [mf, *img.glob(f"{label}.*")]})
        car = fila / "02-carrossel"
        if car.is_dir():
            for d in (p for p in car.iterdir() if p.is_dir()):
                mf = d / "metadata.json"
                if mf.exists():
                    items.append({"label": d.name, "meta": mf, "files": [d]})
    for it in items:
        it["data"] = json.loads(it["meta"].read_text(encoding="utf-8-sig"))
        m = DIA_RE.match(it["label"])
        it["dia"] = int(m.group(1)) if m else 0
    return items


def load_ledger():
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {"ultimo_dia": 0, "carousel_ids": []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", action="store_true")
    args = ap.parse_args()

    items = load_items()
    ledger = load_ledger()
    pending = [i for i in items if not i["data"].get("postado")]
    archived = 0

    if args.archive and items and not pending:
        ids = set(ledger["carousel_ids"])
        for it in items:
            for key in ("carousel_id", "origem_carousel_id"):
                if it["data"].get(key):
                    ids.add(it["data"][key])
            ledger["ultimo_dia"] = max(ledger["ultimo_dia"], it["dia"])
            for f in it["files"]:
                shutil.rmtree(f) if f.is_dir() else f.unlink()
            archived += 1
        ledger["carousel_ids"] = sorted(ids)
        LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
        items, pending = [], []
    else:
        ledger["ultimo_dia"] = max([ledger["ultimo_dia"], *[i["dia"] for i in items]])

    print(f"pending={len(pending)}")
    print(f"next_dia={ledger['ultimo_dia'] + 1}")
    print(f"archived={archived}")


if __name__ == "__main__":
    main()
