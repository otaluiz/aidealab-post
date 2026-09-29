"""
Render a slide HTML into a PNG at exact pixel dimensions, no device-pixel-ratio
surprises. Portable (Linux/Windows/Mac, local or cloud sandbox) -- uses the
`playwright` Python package's own bundled Chromium instead of a hardcoded
local Chrome path.

Setup once per environment: `pip install playwright && playwright install chromium --with-deps`

Usage: python capture.py <url> <out_path.png> [width] [height]

Waits for document.fonts.ready AND for the page's own anticolisao/fit engine
to finish (the HTML templates set document.title to 'READY:...json...' when
done -- see templates/*.html in this skill). Never use device_scale_factor
other than 1, and never rely on a page's own devicePixelRatio: both have
caused letterbox/wrong-resolution renders in the past (see SKILL.md).

Checagem bloqueante (script/monumento): se a peca tem `.script`/`.mono`, o
`window.__fitReport.anticolisao` (embutido no title READY:...) precisa trazer
um `residual` de no maximo 4px de baseline ate o capTop do monumento -- ver
anticolisao.js. Fora disso, ou se a chave nem existir (a chamada travou/nunca
rodou), esta funcao levanta erro em vez de salvar o PNG errado: essa checagem
so existir como aviso foi exatamente como as pecas ruins de 2026-09-21
(Trafego-Pago-Oferta-Ruim, GEO-Busca-com-IA, TESTE-ia-sem-contexto-marca)
saíram com a script boiando longe do bold.
"""
import json
import os
import sys
import time
from playwright.sync_api import sync_playwright

RESIDUAL_TOLERANCE_PX = 4


class RenderCheckFailed(Exception):
    pass


def platform_fonts(page, selector):
    """Familias que o Chromium REALMENTE usou para desenhar o elemento
    (CDP CSS.getPlatformFontsForNode) -- pega fallback silencioso que
    document.fonts.check nao pega."""
    cdp = page.context.new_cdp_session(page)
    cdp.send("DOM.enable")
    cdp.send("CSS.enable")
    root = cdp.send("DOM.getDocument", {"depth": 0})["root"]["nodeId"]
    node = cdp.send("DOM.querySelector", {"nodeId": root, "selector": selector})["nodeId"]
    if not node:
        return None
    res = cdp.send("CSS.getPlatformFontsForNode", {"nodeId": node})
    return [f["familyName"] for f in res["fonts"]]


def check_brand_fonts(page):
    """Gate do padrao da casa (REQUIRE_BRAND_FONTS=1): script=Tempting,
    monumento/titulo=Inter. Sem substituta silenciosa."""
    want = [(".script", "Tempting"), (".mono", "Inter"), (".t-card-head", "Inter")]
    for sel, fam in want:
        got = platform_fonts(page, sel)
        if got is None:
            continue
        print(f"fonts {sel}: {got}", file=sys.stderr)
        if fam not in got:
            raise RenderCheckFailed(
                f"{sel} renderizou com {got}, esperado {fam}. Padrao da casa = Inter 900 + "
                "Tempting (+ Manrope no corpo); fallback proibido. Rode install_fonts.sh.")


def capture(url, out_path, width=1080, height=1440):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE") or None)
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        page.goto(url, wait_until="load", timeout=20000)

        page.wait_for_function("document.fonts.status === 'loaded'", timeout=10000)

        has_lockup = page.evaluate(
            "() => !!(document.querySelector('.script') && document.querySelector('.mono'))"
        )

        t0 = time.time()
        title = page.title()
        while not title.startswith("READY:") and time.time() - t0 < 8:
            time.sleep(0.25)
            title = page.title()
        print("title:", title, file=sys.stderr)
        if not title.startswith("READY:"):
            if has_lockup:
                browser.close()
                raise RenderCheckFailed(
                    f"{url}: pagina nunca setou document.title = 'READY:...' -- "
                    "o fit/anticolisao engine nao terminou (ou travou). Nao vou salvar PNG ruim."
                )
            # Sem .script/.mono no lockup: peca nao usa esse contrato (ex: slide de
            # card/conteudo), READY e opcional aqui -- so aguarda fonts.ready mesmo.
            print("INFO: sem .script/.mono e sem READY -- peca fora do contrato de "
                  "lockup, seguindo sem a checagem bloqueante.", file=sys.stderr)

        report = {}
        if title.startswith("READY:"):
            try:
                report = json.loads(title[len("READY:"):])
            except (ValueError, IndexError):
                print(f"WARNING: nao consegui decodificar o JSON do title: {title!r}", file=sys.stderr)

        dims = page.evaluate(
            "() => ({w: window.innerWidth, h: window.innerHeight, "
            "sw: document.querySelector('.slide')?.getBoundingClientRect().width, "
            "sh: document.querySelector('.slide')?.getBoundingClientRect().height})"
        )
        print("dims check:", dims, file=sys.stderr)

        if has_lockup:
            anticolisao = report.get("anticolisao")
            if not isinstance(anticolisao, dict) or "residual" not in anticolisao:
                browser.close()
                raise RenderCheckFailed(
                    f"{url}: peca tem .script/.mono mas window.__fitReport.anticolisao "
                    f"nao trouxe 'residual' (relatorio: {anticolisao!r}). A chamada pode "
                    "ter lancado erro antes de terminar -- ver console da pagina."
                )
            residual = anticolisao["residual"]
            print(f"anticolisao residual: {residual}px (tolerancia +-{RESIDUAL_TOLERANCE_PX}px)",
                  file=sys.stderr)
            if abs(residual) > RESIDUAL_TOLERANCE_PX:
                browser.close()
                raise RenderCheckFailed(
                    f"{url}: script/monumento residual = {residual}px, fora da tolerancia "
                    f"+-{RESIDUAL_TOLERANCE_PX}px. A script nao esta encostando no monumento "
                    "(ver SKILL.md, checagem bloqueante)."
                )

        if os.environ.get("REQUIRE_BRAND_FONTS") == "1":
            try:
                check_brand_fonts(page)
            except RenderCheckFailed:
                browser.close()
                raise

        page.screenshot(path=out_path, clip={"x": 0, "y": 0, "width": width, "height": height})
        browser.close()
        return dims


if __name__ == "__main__":
    url = sys.argv[1]
    out = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1080
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 1440
    dims = capture(url, out, width, height)
    from PIL import Image
    im = Image.open(out)
    print("SAVED", out, im.size, "dims_reported=", dims)
