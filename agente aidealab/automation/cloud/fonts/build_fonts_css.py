#!/usr/bin/env python3
"""Gera fonts.css ao lado deste script com @font-face LOCAL (nada de Google Fonts em runtime).

Tempting e Helvetica Neue LT Std 57 Condensed sao comerciais: coloque os arquivos (.ttf/.otf/.woff2) nesta
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
EXTS = (".ttf", ".otf", ".woff2")
def find(pred):
    return next((f for f in sorted(os.listdir(HERE)) if f.lower().endswith(EXTS) and pred(f.lower())), None)
tempting = find(lambda n: n.startswith("tempting"))
helv = find(lambda n: "helvetica" in n and ("57" in n or "cn" in n or "cond" in n))
if tempting:
    faces.append(("Tempting", 400, "normal", tempting))
if helv:
    faces.append(("Helvetica Neue LT Std 57 Condensed", 400, "normal", helv))
out = []
for fam, w, st, f in faces:
    fmt = {"ttf": "truetype", "otf": "opentype", "woff2": "woff2"}[f.rsplit(".", 1)[1]]
    out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{st};src:url('fonts/{f}') format('{fmt}');}}")
script = "'Tempting','Playfair Display',Georgia,serif" if tempting else "'Playfair Display',Georgia,serif"
cond = "'Helvetica Neue LT Std 57 Condensed','Arial Narrow',sans-serif" if helv else "'Inter',sans-serif"
out.append(f":root{{--font-script:{script};--font-cond:{cond};}}")
open(os.path.join(HERE, "fonts.css"), "w").write("\n".join(out) + "\n")
print("Tempting:", tempting or "AUSENTE (usando Playfair Display Italic 900)")
print("Helvetica Neue 57 Condensed:", helv or "AUSENTE")
