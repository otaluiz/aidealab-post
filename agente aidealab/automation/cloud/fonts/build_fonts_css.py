#!/usr/bin/env python3
"""Gera fonts.css ao lado deste script com @font-face LOCAL (nada de Google Fonts em runtime).

Tempting e comercial e NAO esta no repo: coloque Tempting.ttf (ou .otf/.woff2) nesta
pasta. Se existir, vira --font-script principal; se nao, cai em Playfair Display
Italic 900 (par de emergencia documentado no SKILL.md).

Uso: python build_fonts_css.py  ->  escreve fonts.css; copie/aponte do build do slide.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
faces = [
    ("Inter", 400, "normal", "Inter-Regular.ttf"),
    ("Inter", 700, "normal", "Inter-Bold.ttf"),
    ("Inter", 900, "normal", "Inter-Black.ttf"),
    ("Playfair Display", 900, "italic", "PlayfairDisplay-BlackItalic.ttf"),
]
tempting = next((f for f in ("Tempting.ttf", "Tempting.otf", "Tempting.woff2") if os.path.isfile(os.path.join(HERE, f))), None)
if tempting:
    faces.append(("Tempting", 400, "normal", tempting))
out = []
for fam, w, st, f in faces:
    fmt = {"ttf": "truetype", "otf": "opentype", "woff2": "woff2"}[f.rsplit(".", 1)[1]]
    out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{st};src:url('fonts/{f}') format('{fmt}');}}")
script = "'Tempting','Playfair Display',Georgia,serif" if tempting else "'Playfair Display',Georgia,serif"
out.append(f":root{{--font-script:{script};}}")
open(os.path.join(HERE, "fonts.css"), "w").write("\n".join(out) + "\n")
print("Tempting:", tempting or "AUSENTE (usando Playfair Display Italic 900)")
