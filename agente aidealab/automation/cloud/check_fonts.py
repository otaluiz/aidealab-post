"""Valida no Chromium (nao so no fc-list) que a marca renderiza com as fontes
certas: .script = Tempting, .mono/.t-card-head = Inter, corpo = Manrope.
Uso: python check_fonts.py   (exit 1 se alguma cair em fallback)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "skills",
                                "criar-post", "templates", "render-engine"))
from capture import platform_fonts  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

HTML = """<html><body style="font-family:Manrope">
<div class="script" style="font-family:'Tempting',cursive;font-size:60px">Seu visitante</div>
<div class="mono" style="font-family:'Inter';font-weight:900;font-size:120px">APARECE.</div>
<div class="body" style="font-family:'Manrope';font-size:24px">corpo do cartao</div>
</body></html>"""
WANT = {".script": "Tempting", ".mono": "Inter", ".body": "Manrope"}

with sync_playwright() as p:
    b = p.chromium.launch(headless=True,
                          executable_path=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE") or None)
    page = b.new_page()
    page.set_content(HTML)
    page.wait_for_function("document.fonts.status === 'loaded'")
    bad = []
    for sel, want in WANT.items():
        got = platform_fonts(page, sel)
        print(f"{sel}: {got}")
        if want not in (got or []):
            bad.append(f"{sel} esperava {want}, renderizou {got}")
    b.close()
if bad:
    print("FALHA de fonte da marca:\n  " + "\n  ".join(bad), file=sys.stderr)
    sys.exit(1)
print("Fontes da marca OK (Inter + Tempting + Manrope).")
