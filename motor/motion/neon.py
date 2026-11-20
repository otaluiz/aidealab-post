#!/usr/bin/env python3
"""Motion neon (tema vice-sunset): carrossel animado a partir das próprias artes aprovadas, sem refazer o texto.

Uso: python motor/motion/neon.py <pasta_da_fila> [--fonte <pasta_do_carrossel>] [--so-html] [--slides 1,3]
  <pasta_da_fila> tem metadata.json + slide-NN.png (ex.: queue/FILA-SEMANA-1/02-carrossel/Dia71-whatsapp-oi-23h).
  O carrossel de origem (carrossel.json) sai de --fonte ou de clientes/aidealab/carrosseis/<slug> (slug = nome sem "DiaNN-").
Saída na própria pasta: slide-NN.mp4 (6 s, 1080x1440) e metadata.json com slides[].video.

Como funciona: o motor estático renderiza o carrossel de novo com o texto escondido (só fundo, foto, recorte e
moldura); a diferença com a arte aprovada vira a camada de texto, cortada em linhas. Assim o texto animado é
exatamente o aprovado (fonte, cor, posição, texto atrás da cabeça) e o fundo continua o do tema.
Efeitos: fundo acende com push-in, faixa de pôr do sol varre de baixo pra cima, scanlines, linhas entram em
cascata com aberração cromática (magenta/teal) que assenta, título pisca como letreiro de neon (sequência fixa,
o mesmo vídeo sempre) e o botão do CTA pulsa com brilho teal. Precisa de node (npx hyperframes), ffmpeg e do
ambiente do render.py (Playwright).
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
MOTOR = AQUI.parent
CARROSSEIS = MOTOR.parent / "agente aidealab" / "clientes" / "aidealab" / "carrosseis"
S = 6
HF = "hyperframes@0.8.181"
ESCONDE = ".display, .emocao, .lista, .bloco-lista, .cta, .corpo, .gancho, .diagrama, .hl { visibility: hidden !important; }\n"


def fonte_do_item(pasta):
    if "--fonte" in sys.argv:
        return Path(sys.argv[sys.argv.index("--fonte") + 1]).resolve()
    slug = pasta.name.split("-", 1)[1] if pasta.name.startswith("Dia") and "-" in pasta.name else pasta.name
    return CARROSSEIS / slug


def render_fundo(src, tmp):
    """Renderiza o carrossel de origem com o texto escondido (tema copiado + regra que oculta o texto)."""
    cj = json.loads((src / "carrossel.json").read_text(encoding="utf-8"))
    tema = (src / "../../design-system/tema-gta").resolve()
    tema_tmp = tmp / "tema"
    shutil.copytree(tema, tema_tmp)
    with open(tema_tmp / "tema.css", "a", encoding="utf-8") as f:
        f.write("\n/* neon.py: só o fundo */\n" + ESCONDE)
    out = tmp / "fundo"
    subprocess.run([sys.executable, str(MOTOR / "render.py"), str(src / "carrossel.json"), str(out), "--tema", str(tema_tmp)], check=True)
    return out, len(cj["slides"])


def linhas(alfa, folga=10, junta=14):
    """Faixas horizontais com texto -> [(y0, y1, x0, x1)]."""
    rows = np.nonzero(alfa.max(1) > 40)[0]
    if not len(rows):
        return []
    faixas, ini, ant = [], rows[0], rows[0]
    for r in rows[1:]:
        if r - ant > junta:
            faixas.append((ini, ant)); ini = r
        ant = r
    faixas.append((ini, ant))
    out = []
    for y0, y1 in faixas:
        if y1 - y0 < 8:
            continue
        cols = np.nonzero(alfa[y0:y1 + 1].max(0) > 40)[0]
        H, W = alfa.shape
        out.append((max(0, y0 - folga), min(H, y1 + folga + 1), max(0, cols[0] - folga), min(W, cols[-1] + folga + 1)))
    return out


def camadas(final_png, fundo_png, proj, i):
    """Separa a arte aprovada em fundo + linhas de texto (RGBA). -> lista de dicts {src,x,y,w,h,pilula}."""
    fin = np.asarray(Image.open(final_png).convert("RGB")).astype(int)
    fun = np.asarray(Image.open(fundo_png).convert("RGB")).astype(int)
    dif = np.abs(fin - fun).max(2)
    alfa = np.clip((dif - 22) * 9, 0, 255).astype(np.uint8)
    alfa[:150] = 0   # topo (meta) e rodapé ficam no fundo
    alfa[-150:] = 0
    Image.open(fundo_png).convert("RGB").save(proj / f"fundo-{i:02d}.jpg", quality=95)
    rgba = np.dstack([fin.astype(np.uint8), alfa])
    res = []
    for k, (y0, y1, x0, x1) in enumerate(linhas(alfa)):
        bloco = rgba[y0:y1, x0:x1]
        nome = f"l{i:02d}-{k}.png"
        Image.fromarray(bloco, "RGBA").save(proj / nome)
        px = bloco[..., :3][bloco[..., 3] > 200].astype(int)
        mag = ((abs(px[:, 0] - 255) < 40) & (abs(px[:, 1] - 46) < 50) & (abs(px[:, 2] - 136) < 50)).mean() if len(px) else 0
        res.append({"src": nome, "x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0), "pilula": bool(mag > 0.55)})
    return res


def secao(i, ls, foto):
    imgs = "".join(f'<img class="ln{" pil" if l["pilula"] else ""}" src="{l["src"]}" style="left:{l["x"]}px;top:{l["y"]}px;width:{l["w"]}px;height:{l["h"]}px" alt="" />' for l in ls)
    return f'''<section id="s{i}" class="slide clip {"foto" if foto else "chapado"}" data-start="{(i - 1) * S}" data-duration="{S}" data-track-index="0">
    <img class="fundo" src="fundo-{i:02d}.jpg" alt="" />
    <div class="sol"></div>
    {imgs}
    <div class="scan"></div>
  </section>'''


TEMPLATE = """<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1440" />
<title>neon</title><script src="vendor/gsap.min.js"></script>
<style>
  body { margin: 0; background: #1A0B2E; }
  #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #1A0B2E; }
  .slide { position: absolute; inset: 0; overflow: hidden; }
  .fundo { position: absolute; inset: 0; width: 100%; height: 100%; transform-origin: 50% 60%; }
  .ln { position: absolute; transform-origin: 0 50%; }
  .sol { position: absolute; left: 0; right: 0; height: 520px; top: 1440px; mix-blend-mode: screen; opacity: 0;
         background: linear-gradient(180deg, rgba(255,154,60,0) 0%, rgba(255,154,60,.55) 35%, rgba(255,46,136,.6) 65%, rgba(255,46,136,0) 100%); }
  .scan { position: absolute; inset: 0; pointer-events: none; opacity: 0; mix-blend-mode: multiply;
          background: repeating-linear-gradient(0deg, rgba(26,11,46,.55) 0 2px, transparent 2px 5px); }
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1440" data-duration="{{DURACAO}}">
  {{SLIDES}}
</div>
<script>
  const S = 6, E = "expo.out";
  // letreiro de neon: sequência fixa (mesma entrada = mesmo vídeo)
  const PISCA = [[0, 0], [.06, .9], [.11, .15], [.19, 1], [.26, .35], [.31, 1], [.52, .6], [.56, 1]];
  const tl = gsap.timeline({ paused: true });
  document.querySelectorAll(".slide").forEach((sl, k) => {
    const t0 = k * S, q = s => sl.querySelectorAll(s), foto = sl.classList.contains("foto");
    tl.fromTo(q(".fundo"), { scale: foto ? 1.07 : 1.03, filter: "brightness(.55) saturate(1.3)" },
              { scale: 1, filter: "brightness(1) saturate(1)", duration: S, ease: "power2.out" }, t0);
    tl.fromTo(q(".sol"), { top: 1440, opacity: .9 }, { top: -560, opacity: 0, duration: 1.3, ease: "power2.inOut" }, t0 + 0.05);
    tl.fromTo(q(".scan"), { opacity: .5 }, { opacity: 0, duration: 1.4, ease: "power1.out" }, t0);
    tl.to(q(".scan"), { opacity: .12, duration: 0.6, ease: "none" }, t0 + 1.6);
    q(".ln").forEach((el, i) => {
      const t = t0 + 0.35 + i * 0.22;
      if (el.classList.contains("pil")) {
        tl.fromTo(el, { scale: .82, opacity: 0 }, { scale: 1, opacity: 1, duration: .8, ease: "back.out(1.8)" }, t);
        tl.fromTo(el, { filter: "drop-shadow(0 0 0px rgba(25,211,197,0))" }, { filter: "drop-shadow(0 0 26px rgba(25,211,197,.95))", duration: .7, ease: "sine.inOut", yoyo: true, repeat: 5 }, t + .9);
        return;
      }
      tl.fromTo(el, { clipPath: "inset(-10% 102% -10% -2%)", filter: "drop-shadow(7px 0 0 rgba(255,46,136,.9)) drop-shadow(-7px 0 0 rgba(25,211,197,.9))" },
                { clipPath: "inset(-10% -2% -10% -2%)", duration: .75, ease: "power3.out" }, t);
      tl.to(el, { filter: "drop-shadow(0px 0 0 rgba(255,46,136,0)) drop-shadow(0px 0 0 rgba(25,211,197,0))", duration: .6, ease: "power2.out" }, t + .55);
      if (i === 0) PISCA.forEach(([dt, o]) => tl.set(el, { opacity: o }, t + .1 + dt));
    });
  });
  window.__timelines["main"] = tl;
</script>
</body></html>
"""


def main():
    pasta = Path(sys.argv[1]).resolve()
    meta_path = pasta / "metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
    slides = sorted(meta["slides"], key=lambda s: s["ordem"])
    src = fonte_do_item(pasta)
    if not (src / "carrossel.json").exists():
        sys.exit(f"neon: carrossel de origem não encontrado em {src}")
    so = None
    if "--slides" in sys.argv:
        so = {int(x) for x in sys.argv[sys.argv.index("--slides") + 1].split(",")}
    cj = json.loads((src / "carrossel.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="neon-") as tmp:
        tmp = Path(tmp)
        fundo, n = render_fundo(src, tmp)
        proj = tmp / "proj"
        proj.mkdir()
        shutil.copytree(AQUI / "vendor", proj / "vendor")
        partes, ordem = [], []
        for i, s in enumerate(slides, 1):
            if so and i not in so:
                continue
            ls = camadas(pasta / s["arquivo"], fundo / f"slide-{i:02d}.png", proj, i)
            foto = bool(cj["slides"][i - 1].get("imagem"))
            j = len(ordem) + 1
            partes.append(secao(i, ls, foto).replace(f'data-start="{(i - 1) * S}"', f'data-start="{(j - 1) * S}"'))
            ordem.append((i, s))
        html = TEMPLATE.replace("{{DURACAO}}", str(len(ordem) * S)).replace("{{SLIDES}}", "\n  ".join(partes))
        (proj / "index.html").write_text(html, encoding="utf-8")
        if "--so-html" in sys.argv:
            shutil.copytree(proj, pasta / "_neon", dirs_exist_ok=True)
            print("projeto em", pasta / "_neon")
            return
        subprocess.run(["npx", "-y", HF, "render", "--quality", "looks", "--output", "completo.mp4"], cwd=proj, check=True)
        for j, (i, s) in enumerate(ordem, 1):
            video = Path(s["arquivo"]).with_suffix(".mp4").name
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str((j - 1) * S), "-t", str(S), "-i", str(proj / "completo.mp4"),
                            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", str(pasta / video)], check=True)
            s["video"] = video
    if not so:
        meta["formato_motion"] = {"fps": 30, "segundos_por_slide": S, "motor": HF, "estilo": "neon"}
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print("ok:", pasta.name, len(ordem), "vídeos neon")


if __name__ == "__main__":
    main()
