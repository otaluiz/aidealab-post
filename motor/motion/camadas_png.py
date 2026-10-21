"""Separa a arte aprovada (slide-NN.png, texto já impresso na foto) em camadas para o motion:
linhas de texto (RGBA recortado, com folga para acento), moldura (topo/rodapé), foto sem texto (inpaint),
recorte do elemento principal (rembg) e placa = foto sem texto e sem o elemento (para o parallax não deixar
"fantasma"). Tudo em cache em <pasta>/motion/<stem>_*.

O texto do tema é branco puro ou ciano #6EC9F7 puro; a foto tem textura e quase nunca bate nessas cores
exatas, então a máscara sai da cor e os pontos soltos da foto caem pelo filtro de densidade do bloco.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

FOLGA = 14  # px acima/abaixo de cada linha (acento e cauda da serifada não cortam)


def _cv():
    import cv2
    return cv2


def mascara_texto(rgb):
    """-> (mascara uint8 0/255 do texto, lista de blocos (x, y, w, h, pilula))."""
    cv2 = _cv()
    a = rgb.astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    branco = (r >= 244) & (g >= 244) & (b >= 244)
    ciano = (abs(r - 0x6E) < 22) & (abs(g - 0xC9) < 22) & (abs(b - 0xF7) < 22)
    core = ((branco | ciano) * 255).astype(np.uint8)
    core0 = core.copy()
    core[:128] = 0  # topo e rodapé saem por faixa (moldura), não pela cor
    core[-130:] = 0
    # texto pontilhado pela textura: pontos colados viram traço; ponto solto da foto (meio-tom) some
    fech = cv2.morphologyEx(core, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fech)
    grande = np.isin(lab, np.nonzero(st[:, 4] >= 40)[0][1:])
    core = np.where(grande, core, 0).astype(np.uint8)
    ciano &= grande
    # botão / marca-texto: caixa ciano cheia; sai antes do agrupamento (o texto ink de dentro vai junto)
    pilulas = []
    cia8 = cv2.morphologyEx((ciano * 255).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(cia8)
    for k in range(1, n):
        x, y, w, h, area = st[k]
        if 45 <= h <= 170 and w >= 120 and area / (w * h) > 0.55:
            hull = cv2.convexHull(np.argwhere(lab[y:y + h, x:x + w] == k)[:, ::-1].astype(np.int32))
            m = np.zeros((h, w), np.uint8)
            cv2.fillConvexPoly(m, hull, 255)
            pilulas.append((int(x), int(y), int(w), int(h), True, m))
            core[y:y + h, x:x + w][m > 0] = 0
    grupo = cv2.dilate(core, cv2.getStructuringElement(cv2.MORPH_RECT, (17, 31)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(grupo)
    final = np.zeros_like(core)
    blocos = []
    for k in range(1, n):
        x, y, w, h, area = st[k]
        sel = lab[y:y + h, x:x + w] == k
        pts = core[y:y + h, x:x + w][sel] > 0
        dens = pts.mean() if pts.size else 0
        if w < 30 or h < 16 or pts.sum() < 120 or dens < 0.16:
            continue
        sub = (core[y:y + h, x:x + w] > 0) & sel
        # texto pontilhado pela textura vira traço cheio; letras continuam abertas (sem fechar o miolo do O)
        m = cv2.morphologyEx((sub * 255).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        blocos.append((int(x), int(y), int(w), int(h), False, m))
    blocos += pilulas
    # bloco pequeno só vale colado num bloco grande ("?", ponto, marca-texto); solto é brilho da foto
    grandes = [b for b in blocos if b[3] >= 40 and b[2] >= 150]
    def gap(a, b):
        dx = max(b[0] - (a[0] + a[2]), a[0] - (b[0] + b[2]), 0)
        dy = max(b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]), 0)
        return max(dx, dy)
    blocos = [b for b in blocos if any(b is g for g in grandes) or any(gap(b, g) < 25 for g in grandes)]
    for x, y, w, h, _, m in blocos:
        final[y:y + h, x:x + w] |= m
    # título colado no topo: o acento (Ê, Ã) cai na faixa zerada da moldura; devolve ele ao bloco
    for k, (x, y, w, h, pil, m) in enumerate(blocos):
        if not pil and y < 170:
            y0 = max(0, y - 45)
            acento = core0[y0:y, x:x + w] & final_moldura_livre(rgb)[y0:y, x:x + w]
            if acento.any():
                final[y0:y, x:x + w] |= acento
                blocos[k] = (x, y0, w, h + (y - y0), pil, m)
    # frase de apoio do CTA (cinza claro, pequena) logo abaixo do botão, alinhada à esquerda com ele
    mn, mx = a.min(2), a.max(2)
    for x, y, w, h, pil, _ in list(blocos):
        if not pil:
            continue
        y0, y1 = y + h + 4, min(rgb.shape[0] - 130, y + h + 110)
        x1 = min(rgb.shape[1] - 50, x + 760)
        claro = ((mn > 140) & (mx - mn < 45))[y0:y1, x:x1]
        tem = claro.sum(1) >= 4
        corridas, k = [], 0  # faixas contínuas de linhas (tolera 2 px de vão); a frase é a primeira com 10-50 px
        while k < len(tem):
            if tem[k]:
                j = k
                while j + 1 < len(tem) and (tem[j + 1] or (j + 2 < len(tem) and tem[j + 2])):
                    j += 1
                corridas.append((k, j))
                k = j + 1
            else:
                k += 1
        corridas = [c for c in corridas if 10 <= c[1] - c[0] + 1 <= 50]
        if not corridas:
            continue
        r0, r1 = corridas[0]
        linhas_c = [r0]
        faixa = claro[r0:r1 + 1]
        cols = np.nonzero(faixa.any(0))[0]
        # corta no primeiro vão largo (o que vem depois é foto, não frase)
        vaos = np.nonzero(np.diff(cols) > 60)[0]
        cfim = cols[vaos[0]] if len(vaos) else cols[-1]
        ay, ax = y0 + int(linhas_c[0]), x + int(cols[0])
        sub = faixa[:, cols[0]:cfim + 1]
        final[ay:ay + sub.shape[0], ax:ax + sub.shape[1]][sub] = 255
        blocos.append((ax, ay, sub.shape[1], sub.shape[0], False, None))
    return final, [b[:5] for b in blocos]


def final_moldura_livre(rgb):
    """255 fora dos cantos onde ficam os textos da moldura (o acento do título nunca está ali)."""
    livre = np.full(rgb.shape[:2], 255, np.uint8)
    livre[85:128, 60:340] = 0
    livre[85:128, 730:1020] = 0
    return livre


def mascara_moldura(rgb):
    """Topo (AIDEA LAB / MARKETING & IA) e rodapé (@handle + pontos) em cinza claro: faixas fixas do motor."""
    cv2 = _cv()
    H = rgb.shape[0]
    a = rgb.astype(int)
    mn, mx = a.min(2), a.max(2)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    claro = (mn > 135) & (mx - mn < 45)
    ciano = (abs(r - 0x6E) < 30) & (abs(g - 0xC9) < 30) & (abs(b - 0xF7) < 30)
    m = np.zeros(rgb.shape[:2], np.uint8)
    faixas = [(85, 128), (H - 130, H - 88)]
    for y0, y1 in faixas:
        for x0, x1 in ((60, 340), (730, 1020)):  # textos da moldura ficam nos cantos
            m[y0:y1, x0:x1] = ((claro | ciano)[y0:y1, x0:x1] * 255).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    ok = [k for k in range(1, n) if st[k, 4] >= 10 and 4 <= st[k, 3] <= 40]
    m = (np.isin(lab, ok) * 255).astype(np.uint8)
    return m, faixas


def linhas_do_bloco(mask, x, y, w, h):
    """Corta um bloco em linhas pelo perfil horizontal (mínimos abaixo de 12% do pico)."""
    prof = (mask[y:y + h, x:x + w] > 0).sum(1).astype(float)
    if prof.max() == 0:
        return []
    suave = np.convolve(prof, np.ones(5) / 5, mode="same")
    limiar = 0.12 * suave.max()
    cortes, k = [0], 0
    while k < h:
        if suave[k] < limiar:
            j = k
            while j < h and suave[j] < limiar:
                j += 1
            meio = k + int(np.argmin(suave[k:j]))
            if meio - cortes[-1] > 18:
                cortes.append(meio)
            k = j
        else:
            k += 1
    cortes.append(h)
    out = []
    for a, b in zip(cortes, cortes[1:]):
        seg = prof[a:b]
        if seg.sum() < 60:
            continue
        nz = np.nonzero(seg)[0]
        out.append([y + a + int(nz[0]), y + a + int(nz[-1]) + 1])
    # faixa baixinha (acento de ÃÊÇ, til) é da linha de baixo: junta, para entrar com as letras
    if len(out) > 1:
        alt = sorted(b - a for a, b in out)[len(out) // 2]
        k = 0
        while k < len(out) - 1:
            if out[k][1] - out[k][0] < 0.35 * alt:
                out[k + 1][0] = out[k][0]
                del out[k]
            else:
                k += 1
    return [tuple(f) for f in out]


def inpaint(rgb, mask):
    """LaMa quando instalado (simple-lama-inpainting); senão OpenCV Telea."""
    try:
        from simple_lama_inpainting import SimpleLama
        global _LAMA
        if "_LAMA" not in globals():
            _LAMA = SimpleLama()
        out = np.array(_LAMA(Image.fromarray(rgb), Image.fromarray(mask).convert("L")))
        return out[: rgb.shape[0], : rgb.shape[1]]
    except Exception:
        cv2 = _cv()
        return cv2.cvtColor(cv2.inpaint(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), mask, 9, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)


def separar(pasta, arquivo):
    """-> dict com caminhos relativos à pasta: placa, recorte, linhas[{src,x,y,w,h}], moldura[{...}]."""
    cv2 = _cv()
    pasta = Path(pasta)
    cache = pasta / "motion"
    cache.mkdir(exist_ok=True)
    stem = Path(arquivo).stem
    idx = cache / f"{stem}_camadas.json"
    if idx.exists():
        return json.loads(idx.read_text(encoding="utf-8"))
    rgb = np.array(Image.open(pasta / arquivo).convert("RGB"))
    H, W = rgb.shape[:2]
    mask, blocos = mascara_texto(rgb)
    mold, faixas_mold = mascara_moldura(rgb)
    # letra com textura por cima não é branco puro: o quase-branco dentro da caixa do bloco também é texto
    a_ = rgb.astype(int)
    quase = ((a_.min(2) > 195) & (a_.max(2) - a_.min(2) < 60)) | ((abs(a_[..., 0] - 0x6E) < 45) & (abs(a_[..., 1] - 0xC9) < 45) & (abs(a_[..., 2] - 0xF7) < 45))
    caixas = np.zeros(mask.shape, bool)
    for x, y, w, h, _ in blocos:
        caixas[max(0, y - 6):y + h + 6, max(0, x - 6):x + w + 6] = True
    texto = mask | ((quase & caixas) * 255).astype(np.uint8)
    alfa = cv2.GaussianBlur(cv2.dilate(texto | mold, np.ones((3, 3), np.uint8)), (3, 3), 0)
    rgba = np.dstack([rgb, alfa])

    def recortar(x, y, w, h, a, b, nome):
        y0, y1 = max(0, a - FOLGA), min(H, b + FOLGA)
        x0, x1 = max(0, x - FOLGA), min(W, x + w + FOLGA)
        parte = rgba[y0:y1, x0:x1].copy()
        sel = np.zeros((H, W), bool)
        sel[max(0, a - 2):b + 2, max(0, x - 2):x + w + 2] = True
        parte[..., 3] = np.where(sel[y0:y1, x0:x1], parte[..., 3], 0)
        Image.fromarray(parte, "RGBA").save(cache / nome)
        return {"src": f"motion/{nome}", "x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}

    linhas, moldura = [], []
    for x, y, w, h, pil in blocos:
        for a, b in ([(y, y + h)] if pil else linhas_do_bloco(mask, x, y, w, h)):
            linhas.append({**recortar(x, y, w, h, a, b, f"{stem}_txt{len(linhas):02d}.png"), "pilula": pil, "y_txt": a, "h_txt": b - a})
    for k, (y0, y1) in enumerate(faixas_mold):
        if mold[y0:y1].any():
            moldura.append(recortar(0, y0, W, y1 - y0, y0, y1, f"{stem}_moldura{k}.png"))
    # palavras na mesma altura formam uma linha e entram juntas (ordem = linha visual, de cima pra baixo)
    linhas.sort(key=lambda d: (d["y_txt"], d["x"]))
    ordem, ref = -1, None
    for d in linhas:
        meio = d["y_txt"] + d["h_txt"] / 2
        if ref is None or abs(meio - ref) > 0.5 * d["h_txt"]:
            ordem, ref = ordem + 1, meio
        d["ordem"] = ordem
    buraco = texto | mold
    limpa = inpaint(rgb, cv2.dilate(buraco, np.ones((13, 13), np.uint8)))
    # recorte: saliência na foto já sem o texto (com texto, o título vira "objeto" grudado na cabeça); elemento que ocupa a tela inteira (ou nada)
    # não tem o que recortar e o slide fica só com o parallax da placa
    from rembg import new_session, remove
    # gente: u2net_human_seg (corpo inteiro, sem a mancha do inpaint do título); sem gente: u2net (objeto)
    a = np.array(remove(Image.fromarray(limpa), session=new_session("u2net_human_seg"), only_mask=True))
    tipo = "gente"
    if (a > 128).mean() < 0.04:
        a, tipo = np.array(remove(Image.fromarray(limpa), session=new_session("u2net"), only_mask=True)), "objeto"
    # a mancha do inpaint do texto atrai a saliência: tudo que caiu no buraco do texto fica na placa
    a[cv2.dilate(buraco, np.ones((31, 31), np.uint8)) > 0] = 0
    # sobra da saliência entre as letras (miolo do O, acento) vira caco solto: fica só o que é corpo
    n, lab, st, _ = cv2.connectedComponentsWithStats((a > 128).astype(np.uint8))
    if n > 1:
        maior = st[1:, 4].max()
        a[~np.isin(lab, [k for k in range(1, n) if st[k, 4] >= 0.15 * maior])] = 0
    dados = {"placa": f"motion/{stem}_placa.jpg", "recorte": None, "linhas": linhas, "moldura": moldura}
    if 0.05 <= (a > 128).mean() <= 0.6:
        Image.fromarray(np.dstack([limpa, a]), "RGBA").save(cache / f"{stem}_recorte.png")
        dados["recorte"] = f"motion/{stem}_recorte.png"
        dados["recorte_tipo"] = tipo
        limpa = inpaint(limpa, cv2.dilate((a > 24).astype(np.uint8) * 255, np.ones((45, 45), np.uint8)))
    Image.fromarray(limpa).save(cache / f"{stem}_placa.jpg", quality=92)
    idx.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return dados


if __name__ == "__main__":  # diagnóstico: python camadas_png.py <pasta> slide-01.png
    import sys
    print(json.dumps(separar(sys.argv[1], sys.argv[2]), indent=1))
