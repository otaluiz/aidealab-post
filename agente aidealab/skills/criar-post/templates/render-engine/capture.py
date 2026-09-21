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
"""
import sys
import time
from playwright.sync_api import sync_playwright


def capture(url, out_path, width=1080, height=1440):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        page.goto(url, wait_until="load", timeout=20000)

        page.wait_for_function("document.fonts.status === 'loaded'", timeout=10000)

        t0 = time.time()
        title = page.title()
        while not title.startswith("READY:") and time.time() - t0 < 8:
            time.sleep(0.25)
            title = page.title()
        if not title.startswith("READY:"):
            print("WARNING: page never set document.title to READY:... -- "
                  "anticolisao/fit engine may not have run. Continuing anyway.",
                  file=sys.stderr)
        print("title:", title, file=sys.stderr)

        dims = page.evaluate(
            "() => ({w: window.innerWidth, h: window.innerHeight, "
            "sw: document.querySelector('.slide')?.getBoundingClientRect().width, "
            "sh: document.querySelector('.slide')?.getBoundingClientRect().height})"
        )
        print("dims check:", dims, file=sys.stderr)

        geom = page.evaluate(
            "() => { const m = document.querySelector('.mword'), s = document.querySelector('.script'); "
            "if (!m || !s) return null; "
            "const mr = m.getBoundingClientRect(), sr = s.getBoundingClientRect(); "
            "return {mword_top: Math.round(mr.top), mword_bottom: Math.round(mr.bottom), "
            "mword_left: Math.round(mr.left), mword_right: Math.round(mr.right), "
            "mword_width: Math.round(mr.width), script_top: Math.round(sr.top), "
            "script_bottom: Math.round(sr.bottom), gap: Math.round(mr.top - sr.bottom)}; }"
        )
        print("geom:", geom, file=sys.stderr)
        if geom is not None and not (-35 <= geom["gap"] <= -10):
            print(f"WARNING: script/monumento gap = {geom['gap']}px, fora da faixa "
                  f"documentada (-15 a -35px). Ver SKILL.md, checagem bloqueante.",
                  file=sys.stderr)

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
