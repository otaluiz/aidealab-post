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
# OpenCV 4 do motor (motor/.vendor_cv4, instalado pelo setup-motor.sh) traz os cascades Haar da detecção de rosto
if (AQUI.parent / ".vendor_cv4").exists():
    sys.path.insert(0, str(AQUI.parent / ".vendor_cv4"))
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


def camadas_foto(pasta, s):
    """Separa a foto estática em duas camadas para o parallax (sem gerar vídeo, sem crédito):
    recorte = elemento principal com fundo transparente (o do motor ou rembg) e
    placa = a foto sem o elemento (OpenCV inpaint na máscara dilatada), para não aparecer "fantasma"
    quando as camadas andam em velocidades diferentes. Cache em <pasta>/motion/."""
    import numpy as np
    from PIL import Image
    cache = pasta / "motion"
    cache.mkdir(exist_ok=True)
    stem = Path(s["imagem"]).stem
    rec = pasta / s["recorte"] if s.get("recorte") else cache / f"{stem}_recorte.png"
    placa = cache / f"{stem}_placa.jpg"
    foto = Image.open(pasta / s["imagem"]).convert("RGB")
    if not rec.exists():
        from rembg import new_session, remove
        remove(foto, session=new_session("isnet-general-use")).save(rec)
    if not placa.exists():
        import cv2
        alfa = np.array(Image.open(rec).convert("RGBA").resize(foto.size))[:, :, 3]
        mascara = cv2.dilate((alfa > 24).astype("uint8") * 255, np.ones((45, 45), "uint8"))
        bgr = cv2.cvtColor(np.array(foto), cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(placa), cv2.inpaint(bgr, mascara, 21, cv2.INPAINT_TELEA), [cv2.IMWRITE_JPEG_QUALITY, 92])
    return placa.relative_to(pasta).as_posix(), rec.relative_to(pasta).as_posix()


def rostos(pasta, s):
    """Caixas [x1,y1,x2,y2] de rosto/cabeça na foto (1080x1440): as do motor (sujeito.rostos_sujeito e
    sujeito.cabeca) ou detecção Haar do OpenCV quando o carrossel.json não traz o sujeito."""
    suj = s.get("sujeito") or {}
    caixas = [list(c) for c in (suj.get("rostos_sujeito") or [])] + ([list(suj["cabeca"])] if suj.get("cabeca") else [])
    if caixas or not s.get("imagem"):
        return caixas
    try:
        import cv2
        cinza = cv2.cvtColor(cv2.imread(str(pasta / s["imagem"])), cv2.COLOR_BGR2GRAY)
        cls = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        return [[int(x), int(y), int(x + w), int(y + h)] for x, y, w, h in cls.detectMultiScale(cinza, 1.1, 6, minSize=(80, 80))]
    except Exception:  # OpenCV sem cascades (5.x): sem detecção, vale só o que o motor marcou
        return []


def camada(src, kind, i):
    """Imagem na raiz (clip da janela do slide) dentro de wrapper que leva o parallax."""
    resp = '<div class="respira">' if kind.startswith("recorte") else '<div class="fixo">'
    k = kind.split()[0]
    return (f'<div class="raiz-midia {kind.replace(k, k + "-w")}" id="{k}{i}">{resp}<img class="clip {k}" src="{src}" alt="" '
            f'data-start="{(i - 1) * S}" data-duration="{S}" data-track-index="{2 if k == "recorte" else 1}" /></div></div>')


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
        placa, rec = camadas_foto(pasta, s)
        # só personagem (recorte do motor) fica na frente do título; elemento recortado aqui fica atrás do texto
        raiz += [camada(placa, "foto", i), camada(rec, "recorte" if s.get("recorte") else "recorte sob", i)]
    elif fundo == "ink":
        camadas.append('<div class="camada led" data-prof="1"></div>')
    else:
        camadas.append('<div class="camada grade" data-prof="1"></div>')
    dots = "".join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(1, n + 1))
    corpo = (s.get("sujeito") or {}).get("caixa")
    dados = (f" data-rostos='{json.dumps(rostos(pasta, s))}'" + (f" data-corpo='{json.dumps(corpo)}'" if corpo else "")) if foto else ""
    return f'''<section id="s{i}" class="slide {fundo} {tpl.lower()} clip"{dados} data-start="{(i - 1) * S}" data-duration="{S}" data-track-index="0">
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
        html_pronto = montar(car, pasta)  # gera placa/recorte em motion/ antes da cópia
        if (pasta / "motion").exists():
            shutil.copytree(pasta / "motion", proj / "motion")
        (proj / "index.html").write_text(html_pronto, encoding="utf-8")
        if "--so-html" in sys.argv:
            shutil.copytree(proj, pasta / "_motion", dirs_exist_ok=True)
            print("projeto em", pasta / "_motion")
            return
        subprocess.run(["npx", "-y", HF, "check"], cwd=proj, check=False)
        subprocess.run(["npx", "-y", HF, "render", "--quality", "looks", "--output", "completo.mp4"], cwd=proj, check=True)
        saida = pasta / "png"
        saida.mkdir(exist_ok=True)
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
