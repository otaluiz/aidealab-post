"""QA bloqueante do contrato do cartao de miolo. Uso: python qa_contract.py <url_slide> [...]
Falha (exit 1) se: chip fora do cartao / nao e o 1o filho; accent longo (>1 linha ou >70
chars) ou sem .t-card-body; body/head serifado; texto solto fora de cartao/lockup;
cartao invadindo header/rodape. Slides hook/CTA (.t-lockup) so checam texto solto + rodape."""
import os, sys
from playwright.sync_api import sync_playwright

JS = """() => {
 const r = e => e.getBoundingClientRect(), fam = e => getComputedStyle(e).fontFamily.toLowerCase();
 const out = {errors: []}, err = m => out.errors.push(m);
 const cards = [...document.querySelectorAll('.t-card')];
 const foot = document.querySelector('.t-footer-handle'), kick = document.querySelector('.t-kicker');
 const footTop = foot ? r(foot).top : 1354, headBot = kick ? r(kick).bottom : 90;
 cards.forEach((c, i) => {
   const chip = c.querySelector('.t-chip'), acc = c.querySelector('.t-card-accent'),
         body = c.querySelector('.t-card-body'), head = c.querySelector('.t-card-head');
   if (!chip || c.firstElementChild !== chip) err('card'+i+': .t-chip tem que ser o PRIMEIRO filho DENTRO do .t-card');
   if (!head) err('card'+i+': falta .t-card-head');
   if (!body || !body.textContent.trim()) err('card'+i+': falta .t-card-body (texto explicativo em sans)');
   if (acc) {
     const lh = parseFloat(getComputedStyle(acc).lineHeight);
     if (acc.textContent.trim().length > 70 || r(acc).height > lh * 1.6) err('card'+i+': .t-card-accent tem que ser UMA linha curta (<=70 chars)');
   }
   [head, body].forEach(e => { if (e && /playfair|tempting|serif/.test(fam(e)) && !/inter/.test(fam(e))) err('card'+i+': head/body nao pode ser serifado'); });
   if (body && /playfair|tempting|georgia/.test(fam(body))) err('card'+i+': body serifado');
   if (body) { const cs = getComputedStyle(body), m = cs.color.match(/\\d+/g).map(Number);
     if (parseFloat(cs.fontSize) < 32) err('card'+i+': .t-card-body menor que 32px ('+cs.fontSize+')');
     if (m[0] < 250 || m[1] < 250 || m[2] < 250) err('card'+i+': .t-card-body tem que ser BRANCO (#fff), veio '+cs.color); }
   const b = r(c); if (b.bottom > footTop - 10) err('card'+i+': invade o rodape ('+Math.round(b.bottom)+' > '+Math.round(footTop-10)+')');
   if (b.top < headBot + 10) err('card'+i+': invade o header');
 });
 const ok = '.t-card,.t-lockup,.t-sub,.t-cta-chip,.t-kicker,.t-footer-handle,.t-footer-cat,.t-footer-dots,.t-bg,[class^=t-vign],.t-scrim-card';
 [...document.querySelectorAll('.slide > *')].forEach(e => {
   if (e.matches(ok) || e.classList.contains('t-block')) return;
   if (e.textContent.trim()) err('texto solto fora de cartao/lockup: <'+e.tagName+' class="'+e.className+'">');
 });
 document.querySelectorAll('.t-chip').forEach(ch => { if (!ch.closest('.t-card')) err('chip fora de cartao'); });
 out.cards = cards.length; return out;
}"""

fails = 0
with sync_playwright() as p:
    kw = {"headless": True}
    if os.environ.get("CAPTURE_CHROMIUM_PATH"): kw["executable_path"] = os.environ["CAPTURE_CHROMIUM_PATH"]
    b = p.chromium.launch(**kw)
    for url in sys.argv[1:]:
        pg = b.new_page(viewport={"width": 1080, "height": 1440}, device_scale_factor=1)
        pg.goto(url, wait_until="load"); pg.wait_for_function("document.fonts.status==='loaded'")
        res = pg.evaluate(JS)
        print(("FAIL " if res["errors"] else "OK   ") + url, "cards=%d" % res["cards"], *res["errors"], sep="\n  " if res["errors"] else " ")
        fails += bool(res["errors"]); pg.close()
    b.close()
sys.exit(1 if fails else 0)
