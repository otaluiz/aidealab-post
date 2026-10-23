"""Fotos limpas dos carrosséis do motor (clientes/aidealab/carrosseis/<slug>): a foto já está na pasta
(carrossel.json slides[].imagem); aqui ela recebe cover, o filtro que reproduz a arte e a cor local do
png/slide-NN.png aprovado, e vai para png/limpas/slide-NN.png. Depois: python motor/motion/motion.py <slug>/png
(o mesmo motion da fila: texto em HTML por cima da foto limpa, nada apagado da arte).

Uso: python motor/motion/limpas_locais.py <pasta do carrossel> [...]
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))
from banco_match import cover, erro, filtros, gradua  # noqa: E402


def preparar(pasta):
    import cv2
    from camadas_png import mascara_moldura, mascara_texto
    car = json.loads((pasta / "carrossel.json").read_text(encoding="utf-8"))
    n = len(car["slides"])
    fx = filtros()
    feitos = {}
    for i, s in enumerate(car["slides"], 1):
        png = pasta / "png" / f"slide-{i:02d}.png"
        if i not in (1, 2, n) or not s.get("imagem") or not png.exists():
            continue
        arte = Image.open(png).convert("RGB")
        rgb = np.asarray(arte)
        mt, _ = mascara_texto(rgb)
        mm, _ = mascara_moldura(rgb)
        ok = cv2.dilate(mt | mm, np.ones((25, 25), np.uint8)) == 0
        base = cover(Image.open(pasta / s["imagem"]))
        nome, foto = min(((k, gradua(f(base), arte, ok)) for k, f in fx.items()), key=lambda z: erro(z[1], arte, ok))
        dest = pasta / "png" / "limpas" / f"slide-{i:02d}.png"
        dest.parent.mkdir(exist_ok=True)
        foto.save(dest, optimize=True)
        feitos[f"slide-{i:02d}"] = {"imagem": s["imagem"], "filtro": nome}
    if feitos:
        (pasta / "png" / "limpas" / "fonte.json").write_text(json.dumps(feitos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(pasta.name, feitos)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        preparar(Path(p))
