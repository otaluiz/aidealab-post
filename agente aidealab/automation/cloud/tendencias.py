"""Coleta o que está em alta no nicho (últimas 48h) e grava estado-tendencias.json.

Roda no GitHub Actions (entregar.yml) todo dia antes da rotina de carrossel das 8h.
Fontes gratuitas, sem chave: Google News RSS (buscas do nicho) e Google Trends RSS (Brasil).
Só stdlib. Falha de uma fonte não derruba as outras.
"""
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).with_name("estado-tendencias.json")
BUSCAS = [
    "inteligência artificial pequenas empresas",
    "WhatsApp Business IA",
    "Instagram novidade recurso",
    "Google Perfil da Empresa OR \"Modo IA\" Google",
    "marketing digital pequenos negócios",
    "ChatGPT OR Gemini OR Claude novidade",
    "Meta IA anúncios empresas",
]
UA = {"User-Agent": "Mozilla/5.0 (aidealab-tendencias)"}


def rss(url, limite):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    itens = []
    for it in root.iter("item"):
        itens.append({
            "titulo": (it.findtext("title") or "").strip(),
            "fonte": (it.findtext("source") or "").strip(),
            "data": (it.findtext("pubDate") or "")[:16],
            "link": it.findtext("link"),
        })
        if len(itens) >= limite:
            break
    return itens


def main():
    estado = {"atualizado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "noticias": {}, "erros": []}
    for q in BUSCAS:
        url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
            {"q": f"{q} when:2d", "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"})
        try:
            estado["noticias"][q] = rss(url, 6)
        except Exception as e:  # noqa: BLE001
            estado["erros"].append(f"{q}: {e}")
    try:
        estado["google_trends_br"] = [i["titulo"] for i in rss("https://trends.google.com/trending/rss?geo=BR", 20)]
    except Exception as e:  # noqa: BLE001
        estado["erros"].append(f"google trends: {e}")
    OUT.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"estado-tendencias.json: {sum(len(v) for v in estado['noticias'].values())} notícias, {len(estado['erros'])} erros")


if __name__ == "__main__":
    sys.exit(main())
