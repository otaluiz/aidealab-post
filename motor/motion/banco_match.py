"""Acha no banco de imagens (Drive img-ref) a foto limpa, sem texto, de cada slide com imagem da fila.

O motor estático faz cover + corte central da foto para 1080x1440 e aplica um filtro (halftone, LED, pano).
Aqui cada foto do banco passa pelo mesmo cover e é comparada (luminância borrada, fora do texto) com o slide
aprovado; a melhor acima do limiar vira <carrossel>/limpas/slide-NN.png, já com o filtro que mais reproduz a arte.
O motion usa essa foto limpa (texto em HTML por cima) e não precisa apagar nada da arte.

Uso (GitHub Actions, com os secrets do Drive): python motor/motion/banco_match.py <pasta da fila> [--todos]
Gera também <pasta da fila>/limpas-relatorio.md.
"""
import io
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))
W, H = 1080, 1440
LIMIAR = 0.80
DRIVE = AQUI.parents[1] / "agente aidealab" / "automation" / "cloud" / "drive_helper.py"
CACHE = Path.home() / ".cache" / "aidealab-banco"
# pastas além das img-ref: fotos geradas dos personagens (Higgsfield Soul) usadas nas capas/CTAs
EXTRA = ["1ekpwC3z2QDSsmwe-YqdxRTD7vZ75qgtg"]


def drive(*args):
    return json.loads(subprocess.run([sys.executable, str(DRIVE), *args], capture_output=True, text=True, check=True).stdout)


def baixar_banco():
    """Todas as imagens das pastas img-ref (banco bruto e as já usadas em peça)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    fotos = []
    for pid in [p["id"] for p in drive("find-folder", "--name", "img-ref")] + EXTRA:
        for f in drive("list", "--parent-id", pid):
            if not f.get("mimeType", "").startswith("image/"):
                continue
            dest = CACHE / f"{f['id']}{Path(f['name']).suffix.lower() or '.png'}"
            if not dest.exists():
                drive("download", "--file-id", f["id"], "--out", str(dest))
            fotos.append((dest, f["name"]))
    return fotos


def cover(im):
    im = im.convert("RGB")
    k = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    l, t = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((l, t, l + W, t + H))


def assinatura(im, mascara=None):
    """luminância borrada 72x96, normalizada; pixels de texto (mascara) ficam fora da comparação."""
    a = np.asarray(im.convert("L").filter(ImageFilter.GaussianBlur(6)).resize((72, 96), Image.BILINEAR)).astype(float)
    ok = np.ones_like(a, bool)
    if mascara is not None:
        ok = np.asarray(Image.fromarray(mascara).resize((72, 96), Image.BILINEAR)) < 20
    v = a[ok]
    return (a - v.mean()) / max(v.std(), 1e-6), ok


def ncc(a, b, ok):
    return float((a[ok] * b[ok]).mean())


def filtros():
    from filtro_halftone import halftone
    from filtro_led import hex2rgb, led
    from textura_foto import cloth, cloth_letras
    cores = [hex2rgb(c) for c in "#05081A,#1B2BD1,#3D6BFF,#6EC9F7,#F4FBFF".split(",")]
    return {
        "nenhum": lambda im: im,
        "halftone": halftone,
        "led": lambda im: led(im, cores),
        "cloth_letras": cloth_letras,
        "halftone+cloth_letras": lambda im: cloth_letras(halftone(im)),
        "led+cloth_letras": lambda im: cloth_letras(led(im, cores)),
    }


def erro(a, b, ok):
    """diferença média de cor (borrada, para a retícula não pesar) fora do texto."""
    x = np.asarray(a.filter(ImageFilter.GaussianBlur(3)).resize((270, 360))).astype(float)
    y = np.asarray(b.filter(ImageFilter.GaussianBlur(3)).resize((270, 360))).astype(float)
    m = np.asarray(Image.fromarray(ok.astype("uint8") * 255).resize((270, 360))) > 128
    return float(np.abs(x - y)[m].mean())


def gradua(foto, arte, ok, sigma=48):
    """Leva a cor/luz local da arte (degradê atrás do texto, vinheta, tom do filtro) para a foto limpa:
    média e desvio por canal numa janela grande, medidos só fora do texto (convolução normalizada)."""
    import cv2
    f = np.asarray(foto.convert("RGB")).astype(np.float32)
    a = np.asarray(arte.convert("RGB")).astype(np.float32)
    w = ok.astype(np.float32)
    def est(x):
        sw = cv2.GaussianBlur(w, (0, 0), sigma) + 1e-4
        m = cv2.GaussianBlur(x * w[..., None], (0, 0), sigma) / sw[..., None]
        v = cv2.GaussianBlur((x - m) ** 2 * w[..., None], (0, 0), sigma) / sw[..., None]
        return m, np.sqrt(np.maximum(v, 1.0))
    mf, sf = est(f)
    ma, sa = est(a)
    out = (f - mf) / sf * np.minimum(sa, sf * 2.5) + ma
    return Image.fromarray(out.clip(0, 255).astype("uint8"))


def main():
    from camadas_png import mascara_moldura, mascara_texto
    import cv2
    fila = Path(sys.argv[1])
    todos = "--todos" in sys.argv
    banco = [(p, n, cover(Image.open(p))) for p, n in baixar_banco()]
    sig = [(p, n, c, assinatura(c)[0]) for p, n, c in banco]
    print(f"banco: {len(sig)} fotos")
    fx = filtros()
    rel = ["# Fotos limpas da fila (banco img-ref)", "", "| carrossel | slide | foto do banco | semelhança | filtro |", "|---|---|---|---|---|"]
    for meta_p in sorted(fila.glob("*/metadata.json")):
        pasta = meta_p.parent
        meta = json.loads(meta_p.read_text(encoding="utf-8-sig"))
        if meta.get("postado") and not todos:
            continue
        n = len(meta["slides"])
        fonte = {}
        for i in sorted({1, 2, n}):
            png = pasta / f"slide-{i:02d}.png"
            if not png.exists():
                continue
            arte = Image.open(png).convert("RGB")
            rgb = np.asarray(arte)
            mt, _ = mascara_texto(rgb)
            mm, _ = mascara_moldura(rgb)
            mask = cv2.dilate(mt | mm, np.ones((25, 25), np.uint8))
            a, ok = assinatura(arte, mask)
            nota, melhor = max(((ncc(a, s, ok), (p, nome, c)) for p, nome, c, s in sig), key=lambda z: z[0])
            linha = f"| {pasta.name} | {i} | {melhor[1]} | {nota:.2f} |"
            if nota < LIMIAR:
                rel.append(linha + " — (abaixo do limiar, sem foto limpa) |")
                continue
            ok_full = mask == 0
            # filtro escolhido já com a cor local da arte aplicada (o que sobra de diferença é textura)
            nome_f, foto = min(((k, gradua(f(melhor[2]), arte, ok_full)) for k, f in fx.items()),
                               key=lambda z: erro(z[1], arte, ok_full))
            dest = pasta / "limpas" / f"slide-{i:02d}.png"
            dest.parent.mkdir(exist_ok=True)
            foto.convert("RGB").save(dest, optimize=True)
            fonte[f"slide-{i:02d}"] = {"banco": melhor[1], "semelhanca": round(nota, 3), "filtro": nome_f}
            rel.append(linha + f" {nome_f} |")
        if fonte:
            (pasta / "limpas" / "fonte.json").write_text(json.dumps(fonte, indent=2, ensure_ascii=False), encoding="utf-8")
    (fila / "limpas-relatorio.md").write_text("\n".join(rel) + "\n", encoding="utf-8")
    print("\n".join(rel))


if __name__ == "__main__":
    main()
