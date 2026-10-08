"""
Texturas por papel do slide, configuradas no tema.json:
  "textura_foto": {"hook": "halftone"}       só na foto (imagem e recorte), o texto fica limpo
  "textura_slide": {"cta": "cloth_letras"}   no slide inteiro, letras incluídas (aplicada no PNG final)
- halftone: filtro_halftone.halftone (retícula de impresso)
- cloth: trama de tecido assets/pano.png em soft-light 55% (a mesma da engine otalogia, --tex-pano)
- cloth_letras: cloth + ±9% de luz/sombra dos fios, para a trama aparecer também nas letras brancas

O render.py aplica na `imagem` e no `recorte` (alfa preservado) antes de desenhar o texto.
Para slides já renderizados (fila/Drive, sem as fotos de origem), `aplicar_slide` protege o texto com uma máscara
de cor + forma (branco, ciano quente, pílula do CTA) e texturiza o resto.

Uso: python textura_foto.py <halftone|cloth|cloth_letras> <entrada> [saida] [--slide]   (--slide = só fora do texto)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from filtro_halftone import halftone

PANO = Path(__file__).resolve().parent / "assets" / "pano.png"


def cloth(im, opac=0.55):
    b = np.asarray(im.convert("RGB")).astype(float) / 255
    s = np.asarray(Image.open(PANO).convert("L").resize(im.size, Image.BILINEAR)).astype(float)[..., None] / 255
    d = np.where(b <= 0.25, ((16 * b - 12) * b + 4) * b, np.sqrt(b))
    sl = np.where(s <= 0.5, b - (1 - 2 * s) * b * (1 - b), b + (2 * s - 1) * (d - b))  # soft-light (W3C)
    return Image.fromarray(((b + opac * (sl - b)).clip(0, 1) * 255).astype("uint8"))


def cloth_letras(im):
    """cloth + luz/sombra dos fios (±9%), para a trama marcar também o branco das letras (soft-light não muda o branco)."""
    t = np.asarray(cloth(im)).astype(float) / 255
    p = np.asarray(Image.open(PANO).convert("L").resize(im.size, Image.BILINEAR)).astype(float) / 255
    p = (p - p.mean()) / max(p.std(), 1e-6)
    return Image.fromarray(((t * (1 + 0.09 * p)[..., None]).clip(0, 1) * 255).astype("uint8"))


FILTROS = {"halftone": halftone, "cloth": cloth, "cloth_letras": cloth_letras}


def aplicar(im, tipo):
    """Textura na foto; RGBA (recorte) mantém o alfa."""
    rgba = im.mode == "RGBA"
    out = FILTROS[tipo](im.convert("RGB"))
    if rgba:
        out = out.convert("RGBA")
        out.putalpha(im.split()[-1])
    return out


def mascara_texto(im):
    """Pixels de texto do motor num slide renderizado: branco/ciano quente em formas de letra (<= 260u de altura) e a
    pílula do CTA; dilatada 3px. Áreas claras grandes da foto (céu, camiseta) não entram."""
    a = np.asarray(im.convert("RGB")).astype(int)
    branco = (a.min(2) > 225) & (np.ptp(a, axis=2) < 28)
    quente = np.abs(a - [110, 201, 247]).sum(2) < 60
    cand = branco | quente
    lab, n = ndimage.label(cand)
    if not n:
        return cand
    areas = ndimage.sum(cand, lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    for i, (sl, ar) in enumerate(zip(ndimage.find_objects(lab), areas), 1):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        letra = h <= 260 and w <= 1000 and ar >= 6
        pilula = 60 <= h <= 160 and w >= 200 and ar / (h * w) > 0.85 and w / h > 2.2
        keep[i] = letra or pilula
    return ndimage.binary_dilation(keep[lab], iterations=3)


def aplicar_slide(im, tipo):
    im = im.convert("RGB")
    w = ndimage.gaussian_filter(mascara_texto(im).astype(float), 1.0)[..., None]
    t = np.asarray(FILTROS[tipo](im)).astype(float)
    return Image.fromarray((t * (1 - w) + np.asarray(im).astype(float) * w).astype("uint8"))


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if x != "--slide"]
    if len(args) < 2 or args[0] not in FILTROS:
        sys.exit(__doc__)
    im = Image.open(args[1])
    out = aplicar_slide(im, args[0]) if "--slide" in sys.argv else aplicar(im, args[0])
    out.save(args[2] if len(args) > 2 else args[1])
    print("OK:", args[2] if len(args) > 2 else args[1])
