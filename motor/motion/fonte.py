#!/usr/bin/env python3
"""Carrossel animado completo a partir do carrossel.json (fonte do motor), com texto animado em TODOS os slides.

Uso: python motor/motion/fonte.py <pasta do carrossel> [--so-html]
  <pasta> tem carrossel.json, as imagens limpas (imagem/recorte de cada slide) e, opcionalmente, os vídeos
  image-to-video dos slides com foto em `motion/<imagem sem extensão>.mp4` (personagem animado). Recorte em
  vídeo (fundo transparente, webm) em `motion/<recorte sem extensão>.webm` mantém o título atrás da cabeça.
Saída: <pasta>/png/slide-NN.mp4 + slides[].video no png/metadata.json (se existir).

Parallax: cada slide tem camadas com profundidade (fundo, foto, texto, frente) que andam em velocidades
diferentes durante os 6 s; o vídeo da foto já traz o movimento de câmera.
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
S = 6
HF = "hyperframes@0.8.181"


def marcar(t):
    """[x] -> palavra quente; {x} -> marca-texto (caixa na cor quente)."""
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]", r'<span class="hot">\1</span>', t)
    return re.sub(r"\{([^}]+)\}", r'<span class="mt"><i></i><b>\1</b></span>', t)


def tamanho(linhas, largura, maximo):
    n = max(len(re.sub(r"[\[\]{}]", "", l)) for l in linhas)
    return min(maximo, int(largura / (n * 0.74)))


def midia(pasta, nome, kind, i):
    """Vídeo animado da imagem (motion/<nome>.mp4|webm) ou a própria imagem. Vídeo é clip próprio na raiz
    (não pode ficar dentro da section temporizada), dentro de um wrapper que leva o parallax."""
    stem = Path(nome).stem
    for ext in (".webm", ".mp4"):
        v = pasta / "motion" / f"{stem}{ext}"
        if v.exists():
            return (f'<div class="raiz-midia {kind}-w" id="{kind}{i}"><video id="v-{kind}{i}" class="clip {kind}" src="motion/{v.name}" muted playsinline '
                    f'data-start="{(i - 1) * S}" data-duration="{S}" data-track-index="{2 if kind == "recorte" else 1}"></video></div>')
    return (f'<div class="raiz-midia {kind}-w" id="{kind}{i}"><img class="clip {kind}" src="{nome}" alt="" '
            f'data-start="{(i - 1) * S}" data-duration="{S}" data-track-index="{2 if kind == "recorte" else 1}" /></div>')


def slide(i, n, s, pasta):
    tpl = s["template"]
    foto = s.get("imagem") and tpl in ("T1", "T1b", "T2", "T4")
    fundo = "foto" if foto else ("ink" if tpl in ("T3", "T4", "T1", "T1b") else "papel")
    bloco = s.get("bloco") or {}
    larg = bloco.get("largura", 936)
    linhas = s.get("display") or []
    if linhas and max(len(l) for l in linhas) > 14 and "y" not in (s.get("bloco") or {}):
        # linhas longas do motor estático ficam miúdas no vídeo: requebra equilibrado (até 4 linhas)
        from motion import linhas as quebra
        linhas = quebra(" ".join(linhas), max_l=4)[0]
    tam = tamanho(linhas, larg, 130) if linhas else 0
    display = "".join(f'<span class="linha"><span class="lin">{marcar(l)}</span></span>' for l in linhas)
    partes = [f'<h2 class="display camada" data-prof="3" style="font-size:{tam}px">{display}</h2>']
    em = s.get("emocao")
    if em:
        txt = "".join(f'<span class="em-l">{marcar(x.strip())}</span>' for x in em["texto"].split(" / "))
        partes.append(f'<p class="serif camada sobe" data-prof="5" style="font-size:{max(72, int(tam * 0.75))}px">{txt}</p>')
    if s.get("lista"):
        partes.append('<ul class="lista camada" data-prof="4">' + "".join(
            f'<li><span class="n">{k:02d}</span><span class="t">{marcar(t)}</span><i class="fio"></i></li>'
            for k, t in enumerate(s["lista"], 1)) + "</ul>")
    if s.get("cta"):
        partes.append(f'<div class="pill camada" data-prof="6">{marcar(s["cta"]["acao"])}</div>')
        partes.append(f'<p class="apoio camada sobe" data-prof="6">{marcar(s["cta"]["texto"])}</p>')
    # posição do bloco de texto: a do motor quando manual (y/alinhar), senão centrado no vertical
    estilo = f"top:{bloco['y']}px;justify-content:flex-start;" if "y" in bloco else ""
    alinhar = bloco.get("alinhar", "esquerda")
    if alinhar == "centro":
        estilo += "align-items:center;text-align:center;"
    camadas, raiz = [], []
    if foto:
        raiz.append(midia(pasta, s["imagem"], "foto", i))
        if s.get("recorte"):
            raiz.append(midia(pasta, s["recorte"], "recorte", i))
    elif fundo == "ink":
        camadas.append('<div class="camada led" data-prof="1"></div>')
    else:
        camadas.append('<div class="camada grade" data-prof="1"></div>')
    dots = "".join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(1, n + 1))
    return f'''<section id="s{i}" class="slide {fundo} {tpl.lower()} clip" data-start="{(i - 1) * S}" data-duration="{S}" data-track-index="0">
    {"".join(camadas)}
    <div class="conteudo" style="{estilo}">{"".join(partes)}</div>
    <div class="topo"><span>AIDEA LAB</span><span>MARKETING &amp; IA</span></div>
    <div class="rodape"><span>@idea_lab7</span><span class="dots">{dots}</span></div>
    <svg class="grao" width="100%" height="100%"><rect width="100%" height="100%" filter="url(#ruido)" /></svg>
  </section>''', "".join(raiz)


def montar(car, pasta):
    slides = car["slides"]
    feitos = [slide(i, len(slides), s, pasta) for i, s in enumerate(slides, 1)]
    corpo = "\n  ".join(m for _, m in feitos) + "\n  " + "\n  ".join(sec for sec, _ in feitos)
    t = (AQUI / "fonte.html").read_text(encoding="utf-8")
    return t.replace("{{DURACAO}}", str(len(slides) * S)).replace("{{SLIDES}}", corpo).replace("{{TITULO}}", car.get("id", "carrossel"))


def main():
    pasta = Path(sys.argv[1]).resolve()
    car = json.loads((pasta / "carrossel.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="motion-") as tmp:
        proj = Path(tmp)
        shutil.copytree(AQUI / "fonts", proj / "fonts")
        for s in car["slides"]:
            for k in ("imagem", "recorte"):
                if s.get(k):
                    shutil.copy2(pasta / s[k], proj / s[k])
        if (pasta / "motion").exists():
            shutil.copytree(pasta / "motion", proj / "motion")
        (proj / "index.html").write_text(montar(car, pasta), encoding="utf-8")
        if "--so-html" in sys.argv:
            shutil.copytree(proj, pasta / "_motion", dirs_exist_ok=True)
            print("projeto em", pasta / "_motion")
            return
        subprocess.run(["npx", "-y", HF, "check"], cwd=proj, check=False)
        subprocess.run(["npx", "-y", HF, "render", "--quality", "looks", "--output", "completo.mp4"], cwd=proj, check=True)
        saida = pasta / "png"
        saida.mkdir(exist_ok=True)
        shutil.copy2(proj / "completo.mp4", saida / "completo.mp4")
        for i in range(1, len(car["slides"]) + 1):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str((i - 1) * S), "-t", str(S), "-i", str(proj / "completo.mp4"),
                            "-c:v", "libx264", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                            str(saida / f"slide-{i:02d}.mp4")], check=True)
    meta_path = pasta / "png" / "metadata.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
        for i, s in enumerate(sorted(meta["slides"], key=lambda s: s["ordem"]), 1):
            s["video"] = f"slide-{i:02d}.mp4"
        meta["formato_motion"] = {"fps": 30, "segundos_por_slide": S, "motor": HF, "fonte": "carrossel.json"}
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print("ok:", pasta.name)


if __name__ == "__main__":
    main()
