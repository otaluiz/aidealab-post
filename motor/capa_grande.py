"""Título grande atrás do sujeito na capa (T1 com recorte): bloco centralizado e largo, cabeça mordendo
só a parte de baixo da última linha do display.

Uso (da pasta do carrossel): python capa_grande.py carrossel.json --tema <pasta_do_tema> [--mordida 50] [--alinhar centro]
Precisa de `sujeito.cabeca` no slide 1 (escrito pelo compor.py). Renderiza em png/ e ajusta `bloco.y` até a base do
display ficar `mordida` px abaixo do topo da cabeça (nunca acima de y=150). Confira o resultado: se a cabeça cair
embaixo de uma letra-chave, rode de novo com --alinhar direita ou esquerda.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("json"); ap.add_argument("--tema", required=True)
ap.add_argument("--mordida", type=int, default=50); ap.add_argument("--alinhar", default="centro")
a = ap.parse_args()
jp = Path(a.json); j = json.loads(jp.read_text(encoding="utf-8")); s = j["slides"][0]
cab = (s.get("sujeito") or {}).get("cabeca")
if not cab or not s.get("recorte"):
    sys.exit("slide 1 sem recorte/sujeito.cabeca: rode o compor.py antes")
larg = 1020 if a.alinhar == "centro" else 936
s["bloco"] = {"y": 150, "alinhar": a.alinhar, "largura": larg, "manual": True}
for _ in range(4):
    jp.write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
    out = subprocess.run([sys.executable, str(AQUI / "render.py"), jp.name, "png", "--tema", a.tema],
                         cwd=jp.parent, capture_output=True, text=True).stdout
    m = re.search(r"slide 1: .*?display=\[\d+, (\d+), \d+, (\d+)\]", out)
    if not m:
        sys.exit("render falhou:\n" + out[-800:])
    y0, y1 = map(int, m.groups()); alvo = max(150, cab[1] + a.mordida - (y1 - y0))
    print(f"display {y0}-{y1}, cabeça topo {cab[1]} -> y {alvo}")
    if alvo == s["bloco"]["y"]:
        break
    s["bloco"]["y"] = alvo
print("ok: confira png/slide-01.png (nenhuma letra pode sumir atrás do sujeito)")
