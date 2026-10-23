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



def _cv():
    import cv2
    return cv2


def mascara_texto(rgb, dica=None):
    """-> (mascara uint8 0/255 do texto, lista de blocos (x, y, w, h, pilula))."""
    cv2 = _cv()
    a = rgb.astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    branco = (r >= 244) & (g >= 244) & (b >= 244)
    ciano = (abs(r - 0x6E) < 22) & (abs(g - 0xC9) < 22) & (abs(b - 0xF7) < 22)
    if dica is not None:  # texto achado pela diferença com a foto limpa (pega letra com textura, que não é branco puro)
        branco = branco | dica
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
        if w < 30 or h < 16 or pts.sum() < 120 or dens < 0.07:
            continue
        sub = (core[y:y + h, x:x + w] > 0) & sel
        # texto pontilhado pela textura vira traço cheio; letras continuam abertas (sem fechar o miolo do O)
        m = cv2.morphologyEx((sub * 255).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        blocos.append((int(x), int(y), int(w), int(h), False, m, dens))
    # traço fino (serifada cursiva) tem pouca densidade: só vale colado num bloco denso (título)
    densos = [b for b in blocos if b[6] >= 0.16]
    def perto(a, b):
        dx = max(b[0] - (a[0] + a[2]), a[0] - (b[0] + b[2]), 0)
        dy = max(b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]), 0)
        return max(dx, dy) < 70
    blocos = [b[:6] for b in blocos if b[6] >= 0.16 or (b[2] >= 150 and any(perto(b, d) for d in densos))]
    # foto branca (roupa, tênis) passa pela cor: texto tem linhas altas; mancha de foto vira muitas faixas baixas
    def linhas_ok(b):
        r = linhas_do_bloco(b[5], 0, 0, b[2], b[3])
        return bool(r) and sorted(z - a for a, z in r)[len(r) // 2] >= 32
    blocos = [b for b in blocos if linhas_ok(b)]
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
        corridas = [c for c in corridas if 8 <= c[1] - c[0] + 1 <= 50]
        if not corridas:
            continue
        r0, r1 = corridas[0]
        for c0, c1 in corridas[1:]:  # frase de apoio quebrada em 2-3 linhas
            if c0 - r1 <= 20 and (c1 - c0) <= 1.6 * (corridas[0][1] - corridas[0][0] + 1):
                r1 = c1
            else:
                break
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
    """Linhas de um bloco pelo perfil horizontal: o miolo de cada linha é onde a tinta passa de 12% do pico;
    acento logo acima (faixa baixinha colada) entra na linha de baixo; a borda se estende pela tinta contínua
    (descendente, cauda da serifada). Tinta fraca solta (pedaço de foto branca) fica de fora."""
    prof = (mask[y:y + h, x:x + w] > 0).sum(1).astype(float)
    if prof.max() == 0:
        return []
    suave = np.convolve(prof, np.ones(3) / 3, mode="same")
    forte = suave >= 0.12 * suave.max()
    runs, k = [], 0
    while k < h:
        if forte[k]:
            j = k
            while j + 1 < h and (forte[j + 1] or (j + 3 < h and forte[j + 2:j + 4].any())):
                j += 1
            runs.append([k, j + 1])
            k = j + 1
        else:
            k += 1
    if not runs:
        return []
    alt = sorted(b - a for a, b in runs)[len(runs) // 2]
    k = 0
    while k < len(runs) - 1:  # acento: faixa curta colada na de baixo
        if runs[k][1] - runs[k][0] < 0.45 * alt and runs[k + 1][0] - runs[k][1] <= 10:
            runs[k + 1][0] = runs[k][0]
            del runs[k]
        else:
            k += 1
    runs = [r for r in runs if r[1] - r[0] >= 0.3 * alt]  # sobra curta e solta não é linha
    out = []
    for n_, (a, b) in enumerate(runs):
        lim_a = (runs[n_ - 1][1] + a) // 2 if n_ else 0
        lim_b = (b + runs[n_ + 1][0]) // 2 if n_ + 1 < len(runs) else h
        while a > lim_a and prof[a - 1] > 0:
            a -= 1
        while b < lim_b and prof[b] > 0:
            b += 1
        out.append((y + a, y + b))
    return out


def inpaint(rgb, mask):
    """FSR do opencv-contrib (reconstrói a textura/retícula da foto); sem contrib, Telea (deixa mancha)."""
    cv2 = _cv()
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    if hasattr(cv2, "xphoto"):
        out = bgr.copy()
        cv2.xphoto.inpaint(bgr, (255 - mask).astype(np.uint8), out, cv2.xphoto.INPAINT_FSR_FAST)
    else:
        out = cv2.inpaint(bgr, mask, 5, cv2.INPAINT_TELEA)
    return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)


def separar(pasta, arquivo, limpa=None):
    """-> placa e recorte (caminhos relativos à pasta) + geometria do texto impresso: linhas[{x,y,w,h,hot,mt}],
    botao{x,y,w,h,dentro} e apoio{x,y,w,h,cor}. O texto é refeito em HTML por cima, nessas caixas."""
    cv2 = _cv()
    pasta = Path(pasta)
    cache = pasta / "motion"
    cache.mkdir(exist_ok=True)
    stem = Path(arquivo).stem
    idx = cache / f"{stem}_camadas{'_limpa' if limpa else ''}.json"
    if idx.exists():
        return json.loads(idx.read_text(encoding="utf-8"))
    rgb = np.array(Image.open(pasta / arquivo).convert("RGB"))
    H, W = rgb.shape[:2]
    dica = None
    if limpa is not None:
        lp = np.array(Image.open(pasta / limpa).convert("RGB")).astype(int)
        lum = lambda z: z @ [0.2126, 0.7152, 0.0722]
        dif = np.abs(rgb.astype(int) - lp).max(2)
        # letra é bem mais clara que a foto atrás e neutra (branco/cinza com textura) ou ciano
        neutro = (rgb.astype(int).max(2) - rgb.astype(int).min(2)) < 70
        dica = (dif > 55) & (lum(rgb.astype(float)) > lum(lp.astype(float)) + 35) & neutro & (rgb.min(2) > 150)
    mask, blocos = mascara_texto(rgb, dica)
    mold, faixas_mold = mascara_moldura(rgb)
    # letra com textura por cima não é branco puro: o quase-branco dentro da caixa do bloco também é texto
    a_ = rgb.astype(int)
    quase = ((a_.min(2) > 195) & (a_.max(2) - a_.min(2) < 60)) | ((abs(a_[..., 0] - 0x6E) < 45) & (abs(a_[..., 1] - 0xC9) < 45) & (abs(a_[..., 2] - 0xF7) < 45))
    # a letra do motor estático tem degradê (branco em cima, cinza embaixo) e retícula por cima: a máscara de cor
    # pura pega só o topo. Cresce a partir dela por pixel claro e neutro (ou ciano) conectado, dentro da caixa do
    # bloco; o resto da caixa é foto e não pode virar buraco
    caixas = np.zeros(mask.shape, np.uint8)
    for x, y, w, h, _ in blocos:
        caixas[max(0, y - 12):y + h + 12, max(0, x - 12):x + w + 12] = 1
    claro = ((a_.min(2) > 105) & (a_.max(2) - a_.min(2) < 55)) | ((abs(a_[..., 0] - 0x6E) < 60) & (abs(a_[..., 1] - 0xC9) < 60) & (abs(a_[..., 2] - 0xF7) < 60))
    # só embaixo da parte branca da letra (o degradê escurece para baixo) e colado nela, nunca a foto em volta
    k = np.zeros((91, 5), np.uint8)
    k[:46, :] = 1  # dilate com a metade de cima do kernel = cada pixel branco se estende 45 px para baixo
    abaixo = cv2.dilate(mask, k)
    # letra inteira com retícula por cima não tem pixel branco puro: vale também o vizinho de lado na mesma linha
    abaixo |= cv2.dilate(mask, np.ones((3, 121), np.uint8))
    cand = (claro & (caixas > 0) & (abaixo > 0)).astype(np.uint8)
    n, lab = cv2.connectedComponents(cv2.dilate(cand, np.ones((3, 3), np.uint8)))
    ok = np.unique(lab[(mask > 0) & (lab > 0)])
    texto = mask | ((np.isin(lab, ok) & (cand > 0)) * 255).astype(np.uint8)
    a_i = rgb.astype(int)
    ciano = (abs(a_i[..., 0] - 0x6E) < 40) & (abs(a_i[..., 1] - 0xC9) < 40) & (abs(a_i[..., 2] - 0xF7) < 40)

    def intervalos(sel):
        """colunas marcadas -> [[x0, x1], ...] (vão < 25 px junta)."""
        cols = np.nonzero(sel.sum(0) >= 2)[0]
        out = []
        for c in cols:
            if out and c - out[-1][1] < 25:
                out[-1][1] = int(c)
            else:
                out.append([int(c), int(c)])
        return [iv for iv in out if iv[1] - iv[0] > 24]

    # caixas de cada linha (palavras na mesma altura viram uma linha); o texto volta em HTML (vetor, nítido)
    itens = []
    for x, y, w, h, pil in blocos:
        for a, b in ([(y, y + h)] if pil else linhas_do_bloco(mask, x, y, w, h)):
            sub = mask[a:b, x:x + w] > 0  # só a cor pura do texto (o quase-branco pega brilho da foto)
            lx, lw = x, w
            if not pil and sub.any():  # aperta a caixa nos pixels de texto
                cs, rs = np.nonzero(sub.any(0))[0], np.nonzero(sub.any(1))[0]
                lx, lw, a, b = x + int(cs[0]), int(cs[-1] - cs[0] + 1), a + int(rs[0]), a + int(rs[-1]) + 1
            itens.append({"x": int(lx), "y": int(a), "w": int(lw), "h": int(b - a), "pil": pil})
    itens.sort(key=lambda d: (d["y"] + d["h"] / 2, d["x"]))
    linhas = []
    for d in itens:
        meio = d["y"] + d["h"] / 2
        ult = linhas[-1] if linhas else None
        if ult and abs(meio - (ult["y"] + ult["h"] / 2)) < 0.45 * max(d["h"], ult["h"]) and not (d["pil"] and not ult["partes"][0]["pil"] and False):
            ult["partes"].append(d)
            x0, y0 = min(ult["x"], d["x"]), min(ult["y"], d["y"])
            ult["w"] = max(ult["x"] + ult["w"], d["x"] + d["w"]) - x0
            ult["h"] = max(ult["y"] + ult["h"], d["y"] + d["h"]) - y0
            ult["x"], ult["y"] = x0, y0
        else:
            linhas.append({**d, "partes": [d]})
    saida, botao, apoio = [], None, None
    for k, ln in enumerate(linhas):
        caixas_mt = [[p["x"], p["x"] + p["w"]] for p in ln["partes"] if p["pil"]]
        if caixas_mt and len(ln["partes"]) == 1:
            # botão do CTA: caixa ciano sozinha na linha; o texto escuro de dentro dá o tamanho da letra
            bx, by, bw, bh = ln["x"], ln["y"], ln["w"], ln["h"]
            mx, my = int(bh * 0.35), int(bh * 0.18)  # longe das bordas arredondadas (fora delas é fundo escuro)
            esc = a_i[by + my:by + bh - my, bx + mx:bx + bw - mx].max(2) < 120
            cs, rs = np.nonzero(esc.sum(0) >= 2)[0], np.nonzero(esc.sum(1) >= 2)[0]
            dentro = ([bx + mx + int(cs[0]), by + my + int(rs[0]), int(cs[-1] - cs[0] + 1), int(rs[-1] - rs[0] + 1)]
                      if len(cs) else None)
            botao = {"x": bx, "y": by, "w": bw, "h": bh, "dentro": dentro}
            j, fim = k + 1, by + bh
            rows = []
            while j < len(linhas) and not linhas[j]["pil"] and linhas[j]["y"] - fim < (120 if not rows else 30) and linhas[j]["h"] < 50:
                rows.append(linhas[j]); fim = linhas[j]["y"] + linhas[j]["h"]; j += 1
            if rows:
                ax, ay = min(r["x"] for r in rows), rows[0]["y"]
                cor = np.concatenate([rgb[r["y"]:r["y"] + r["h"], r["x"]:r["x"] + r["w"]][texto[r["y"]:r["y"] + r["h"], r["x"]:r["x"] + r["w"]] > 0] for r in rows])
                apoio = {"x": ax, "y": ay, "w": max(r["x"] + r["w"] for r in rows) - ax, "h": rows[0]["h"], "linhas": len(rows),
                         "passo": (rows[1]["y"] - rows[0]["y"]) if len(rows) > 1 else 0, "ids": [id(r) for r in rows],
                         "cor": "#%02x%02x%02x" % tuple(int(v) for v in (np.median(cor, 0) if len(cor) else (200, 200, 200)))}
            continue
        if apoio and id(ln) in apoio["ids"]:
            continue
        hot = intervalos(ciano[ln["y"]:ln["y"] + ln["h"], ln["x"]:ln["x"] + ln["w"]] & (texto[ln["y"]:ln["y"] + ln["h"], ln["x"]:ln["x"] + ln["w"]] > 0))
        hot = [[ln["x"] + a, ln["x"] + b] for a, b in hot if not any(a + ln["x"] >= c0 - 5 and b + ln["x"] <= c1 + 5 for c0, c1 in caixas_mt)]
        # faixa da versal (topo da letra até a linha de base): onde quase toda coluna tem tinta; acento e sobra da
        # linha vizinha são poucos pixels e ficam fora. É dela que sai o corpo do título (a caixa pode vir torta)
        y0, y1 = max(0, ln["y"] - 30), ln["y"] + ln["h"] + 30
        prof = (mask[y0:y1, ln["x"]:ln["x"] + ln["w"]] > 0).sum(1).astype(float)
        meio = ln["y"] + ln["h"] // 2 - y0
        forte = prof >= 0.3 * prof[max(0, meio - ln["h"] // 3):meio + ln["h"] // 3].max()
        a_, b_ = meio, meio
        while a_ > 0 and (forte[a_ - 1] or (a_ > 1 and forte[a_ - 2])):
            a_ -= 1
        while b_ < len(forte) - 1 and (forte[b_ + 1] or (b_ < len(forte) - 2 and forte[b_ + 2])):
            b_ += 1
        saida.append({"x": ln["x"], "y": ln["y"], "w": ln["w"], "h": ln["h"], "hot": hot, "mt": caixas_mt,
                      "cap": [int(y0 + a_), int(y0 + b_ + 1)]})
    buraco = texto | mold
    usa_limpa = limpa is not None
    if usa_limpa:  # foto limpa do banco (banco_match.py): nada é apagado da arte
        limpa = np.array(Image.open(pasta / limpa).convert("RGB"))
    else:
        limpa = inpaint(rgb, cv2.dilate(buraco, np.ones((7, 7), np.uint8)))

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
    if apoio:
        apoio.pop("ids")
    dados = {"placa": f"motion/{stem}_placa.jpg", "recorte": None, "linhas": saida, "botao": botao, "apoio": apoio}
    if 0.05 <= (a > 128).mean() <= 0.6:
        Image.fromarray(np.dstack([limpa, a]), "RGBA").save(cache / f"{stem}_recorte.png")
        dados["recorte"] = f"motion/{stem}_recorte.png"
        dados["recorte_tipo"] = tipo
        if tipo == "gente":  # gente descola mais: o buraco atrás dela (não o texto) é preenchido
            limpa = inpaint(limpa, cv2.dilate((a > 24).astype(np.uint8) * 255, np.ones((31, 31), np.uint8)))
        # objeto anda quase junto com a placa: o original fica atrás (sem mancha de inpaint aparecendo)
    Image.fromarray(limpa).save(cache / f"{stem}_placa.jpg", quality=92)
    idx.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return dados


if __name__ == "__main__":  # diagnóstico: python camadas_png.py <pasta> slide-01.png
    import sys
    print(json.dumps(separar(sys.argv[1], sys.argv[2]), indent=1))
