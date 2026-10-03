#!/usr/bin/env python3
"""Lista as pastas de 06-Aprovados-para-Postar/RASCUNHOS do aidealab, do carrossel
mais antigo ao mais novo, ainda não presentes na fila do repo.

Saída: JSON em stdout (lista de {id, name, carousel_id, data, dia}). `dia` é o número
sequencial (a partir de --start-dia) que o item recebe na fila (DiaNN-slug), para que
a ordem de publicação siga a ordem de criação.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HELPER = str(HERE / "drive_helper.py")
QUEUE_ROOT = HERE.parent / "skills" / "post-instagram" / "queue"


def helper(*args):
    out = subprocess.run([sys.executable, HELPER, *args], check=True, capture_output=True, text=True)
    return out.stdout


def find_folder(name, parent_id):
    found = json.loads(helper("find-folder", "--name", name, "--parent-id", parent_id))
    if not found:
        sys.exit(f"ERRO: pasta '{name}' nao encontrada em {parent_id}")
    return found[0]["id"]


def queued_ids():
    ids = set()
    for p in QUEUE_ROOT.rglob("*metadata.json"):
        try:
            meta = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        for key in ("carousel_id", "origem_carousel_id"):
            if meta.get(key):
                ids.add(meta[key])
    ledger = QUEUE_ROOT / "_arquivo-postados.json"
    if ledger.exists():
        ids.update(json.loads(ledger.read_text(encoding="utf-8")).get("carousel_ids", []))
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-dia", type=int, required=True)
    args = ap.parse_args()

    root = os.environ["AIDEALAB_FOLDER_ID"]
    aprovados = find_folder("06-Aprovados-para-Postar", root)
    rascunhos = find_folder("RASCUNHOS", aprovados)
    folders = json.loads(helper("list", "--parent-id", rascunhos, "--folders-only"))

    already = queued_ids()
    items = []
    for f in folders:
        files = json.loads(helper("list", "--parent-id", f["id"]))
        meta_file = next((x for x in files if x["name"] == "metadata.json"), None)
        if not meta_file or not any(x["name"].lower().endswith(".png") for x in files):
            print(f"[SKIP] {f['name']}: sem metadata.json ou sem PNG", file=sys.stderr)
            continue
        meta = json.loads(helper("read-text", "--file-id", meta_file["id"]))
        cid = meta.get("carousel_id") or f["name"]
        if meta.get("postado") or meta.get("status") == "bloqueado" or cid in already:
            print(f"[SKIP] {f['name']}: postado/bloqueado/ja na fila", file=sys.stderr)
            continue
        data = meta.get("data_criacao") or f["createdTime"][:10]
        m = re.match(r"(\d{4}-\d{2}-\d{2})_", f["name"])
        if m:
            data = min(data, m.group(1))
        items.append({"id": f["id"], "name": f["name"], "carousel_id": cid, "data": data, "created": f["createdTime"]})

    items.sort(key=lambda i: (i["data"], i["created"], i["name"]))
    for n, it in enumerate(items, start=args.start_dia):
        it["dia"] = n
        del it["created"]
    print(json.dumps(items, ensure_ascii=False))


if __name__ == "__main__":
    main()
