#!/usr/bin/env python3
"""Carrossel animado (HyperFrames) a partir de um carrossel já renderizado pelo motor.

Uso: python motor/motion/motion.py <pasta> [--so-html]
  <pasta> tem metadata.json (slides[].arquivo/texto/papel, template "T1-T2-...-T4") e os slide-NN.png.
Saída na própria pasta: slide-NN.mp4 (6 s cada, 1080x1440) e metadata.json com slides[].video.

Regras de motion (skill criar-motion):
  - capa, slide 2 e CTA (e slides sem texto, ex. T5) usam a ARTE APROVADA (png) com efeito por cima:
    acende do escuro com push-in, brilho que varre, poeira na névoa.
  - os outros slides são refeitos em tipografia animada a partir do texto: display em caixa alta revelado
    por máscara + serifada/corpo ou lista (T3). Papel em T2/T2c, navy com grade LED em T3.
Precisa de node (npx hyperframes) e ffmpeg.
"""
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
S = 6  # segundos por slide
HF = "hyperframes@0.8.181"
MARCAS = {"WhatsApp", "IA", "Instagram", "Google", "Pix", "aidealab"}


def separar(texto):
    """'NÃO FALTA GENTE falta um sistema' -> ('NÃO FALTA GENTE', 'falta um sistema')."""
    pal = texto.split()
    i = 0
    while i < len(pal) and re.sub(r"[^A-Za-zÀ-ÿ]", "", pal[i]) and re.sub(r"[^A-Za-zÀ-ÿ]", "", pal[i]).isupper():
        # artigo de 1 letra seguido de minúscula abre o resto ("RÁPIDA O cliente"), não é display
        if i and len(pal[i]) == 1 and i + 1 < len(pal) and pal[i + 1][:1].islower():
            break
        i += 1
    if i < len(pal) and not re.sub(r"[^A-Za-zÀ-ÿ0-9]", "", pal[i]):
        i += 1
    return " ".join(pal[:i]), " ".join(pal[i:])


def itens(resto):
    """Itens de lista colados: quebra antes de cada palavra capitalizada (exceto marcas)."""
    out = []
    for p in resto.split():
        if out and p[:1].isupper() and p.strip(".,") not in MARCAS:
            out.append(p)
        elif out:
            out[-1] += " " + p
        else:
            out.append(p)
    return out


def linhas(display, max_l=3):
    """Quebra o display em até 3 linhas (testa todas as quebras) maximizando a fonte, sem linha com uma
    palavra curta sozinha; devolve (linhas, tamanho da fonte em px)."""
    from itertools import combinations
    pal = display.split()
    melhor = None
    for n in range(1, min(max_l, len(pal)) + 1):
        for cortes in combinations(range(1, len(pal)), n - 1):
            idx = (0, *cortes, len(pal))
            ls = [" ".join(pal[a:b]) for a, b in zip(idx, idx[1:])]
            if n > 1 and any(len(l) <= 3 for l in ls):
                continue
            tam = min(150, int(936 / (max(len(l) for l in ls) * 0.78)))
            if melhor is None or tam > melhor[1] + 8 or (tam >= melhor[1] - 8 and n == 2 and len(melhor[0]) != 2):
                melhor = (ls, tam)
    return melhor


def esc(s):
    return html.escape(s, quote=False)


def slide_png(i, arq, foto):
    efeitos = ('<img class="bloom" src="{a}" alt="" /><div class="poeira" data-layout-allow-overflow></div>'.format(a=arq)
               if foto else "")
    return f'''<section id="s{i}" class="slide png clip" data-start="{(i - 1) * S}" data-duration="{S}" data-track-index="0">
    <img class="foto" src="{arq}" alt="" />{efeitos}<div class="brilho" data-layout-allow-overflow></div>
  </section>'''


def slide_tipo(i, n, tpl, texto):
    display, resto = separar(texto)
    ls, tam = linhas(display)
    fundo = "ink" if tpl.startswith("T3") else "papel"
    spans = []
    for j, l in enumerate(ls):
        if j == len(ls) - 1:
            # palavra quente = a última com mais de 3 letras da última linha (nunca "DO", "NO", "QUE")
            w = l.split(" ")
            k = max((x for x in range(len(w)) if len(w[x].strip(".,?!")) > 3), default=None)
            l = " ".join(f'<span class="hot">{esc(p)}</span>' if x == k else esc(p) for x, p in enumerate(w))
        else:
            l = esc(l)
        spans.append(f'<span class="linha"><span class="lin">{l}</span></span>')
    corpo = ""
    lista = itens(resto) if tpl.startswith("T3") else []
    if len(lista) >= 2:
        corpo = '<ul class="lista">' + "".join(
            f'<li><span class="n">{k:02d}</span><span class="t">{esc(t)}</span><i class="fio"></i></li>' for k, t in enumerate(lista[:4], 1)
        ) + "</ul>"
    elif resto:
        cls = "serif" if len(resto) <= 48 else "corpo"
        corpo = f'<p class="{cls} sobe">{esc(resto)}</p>'
    dots = "".join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(1, n + 1))
    textura = '<div class="led" data-layout-allow-overflow></div>' if fundo == "ink" else '<div class="grade" data-layout-allow-overflow></div>'
    return f'''<section id="s{i}" class="slide {fundo} tipo clip" data-start="{(i - 1) * S}" data-duration="{S}" data-track-index="0">
    {textura}
    <div class="conteudo">
      <h2 class="display" style="font-size: {tam}px" data-layout-allow-overflow>{"".join(spans)}</h2>
      {corpo}
    </div>
    <div class="topo"><span>AIDEA LAB</span><span>MARKETING &amp; IA</span></div>
    <div class="rodape"><span>@idea_lab7</span><span class="dots">{dots}</span></div>
    <svg class="grao" width="100%" height="100%"><rect width="100%" height="100%" filter="url(#ruido)" /></svg>
  </section>'''


def montar(meta):
    slides = sorted(meta["slides"], key=lambda s: s["ordem"])
    tpls = (meta.get("template") or "").split("-")
    n = len(slides)
    partes = []
    for i, s in enumerate(slides, 1):
        tpl = tpls[i - 1] if i - 1 < len(tpls) else "T2"
        texto = (s.get("texto") or "").strip()
        if i in (1, 2, n) or not texto or tpl.startswith("T5"):
            partes.append(slide_png(i, s["arquivo"], foto=i in (1, 2, n)))
        else:
            partes.append(slide_tipo(i, n, tpl, texto))
    tpl_html = (AQUI / "template.html").read_text(encoding="utf-8")
    return tpl_html.replace("{{DURACAO}}", str(n * S)).replace("{{SLIDES}}", "\n  ".join(partes)).replace("{{TITULO}}", esc(meta.get("tema", "carrossel")))


def main():
    pasta = Path(sys.argv[1]).resolve()
    meta_path = pasta / "metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
    with tempfile.TemporaryDirectory(prefix="motion-") as tmp:
        proj = Path(tmp)
        shutil.copytree(AQUI / "fonts", proj / "fonts")
        for s in meta["slides"]:
            shutil.copy2(pasta / s["arquivo"], proj / s["arquivo"])
        (proj / "index.html").write_text(montar(meta), encoding="utf-8")
        if "--so-html" in sys.argv:
            shutil.copytree(proj, pasta / "_motion", dirs_exist_ok=True)
            print("projeto em", pasta / "_motion")
            return
        subprocess.run(["npx", "-y", HF, "check"], cwd=proj, check=False)
        subprocess.run(["npx", "-y", HF, "render", "--quality", "looks", "--output", "completo.mp4"], cwd=proj, check=True)
        for i, s in enumerate(sorted(meta["slides"], key=lambda s: s["ordem"]), 1):
            video = Path(s["arquivo"]).with_suffix(".mp4").name
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str((i - 1) * S), "-t", str(S), "-i", str(proj / "completo.mp4"),
                            "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(pasta / video)], check=True)
            s["video"] = video
    meta["formato_motion"] = {"fps": 30, "segundos_por_slide": S, "motor": HF}
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print("ok:", pasta.name, len(meta["slides"]), "vídeos")


if __name__ == "__main__":
    main()
