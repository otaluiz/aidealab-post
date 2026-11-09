#!/usr/bin/env python3
"""Falha se a alternância reel/carrossel do publish_next quebrar. Uso: python test_intercalar.py"""
import json
import tempfile
from pathlib import Path

import publish_next as p


def it(kind, personagem=False, postado=False):
    return {"kind": kind, "metadata": {"postado": postado, "personagem": "x" if personagem else ""}, "label": kind}


with tempfile.TemporaryDirectory() as tmp:
    p.ULTIMO_TIPO = Path(tmp) / "u.json"
    fila = [it("carrossel", True), it("reel")]
    assert p.find_next(fila)["kind"] == "reel"  # sem histórico: o último conta como carrossel
    p.ULTIMO_TIPO.write_text(json.dumps({"formato": "reel", "historico": [True]}), encoding="utf-8")
    assert p.find_next(fila)["kind"] == "carrossel"  # depois de reel vem carrossel
    assert p.find_next([it("reel")])["kind"] == "reel"  # sem carrossel aprovado, não perde o dia
    p.ULTIMO_TIPO.write_text(json.dumps({"formato": "carrossel"}), encoding="utf-8")
    assert p.find_next([it("carrossel")])["kind"] == "carrossel"  # sem reel aprovado, segue o carrossel
    assert p.find_next([it("reel", postado=True), it("carrossel")])["kind"] == "carrossel"  # reel já postado não volta
    p.ULTIMO_TIPO.write_text(json.dumps({"formato": "reel", "historico": [True, True]}), encoding="utf-8")
    com, sem = it("carrossel", True), it("carrossel", False)
    assert p.find_next([com, sem]) is sem  # a regra de 2 com personagem para 1 sem continua
print("ok")
