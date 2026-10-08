"""Lê o perfil @idea_lab7 e os posts recentes pela Graph API e grava estado-instagram.json.

Roda no GitHub Actions (entregar.yml) antes da rotina de carrossel das 8h. A rotina e qualquer
sessão do Claude leem o JSON para saber o que performa sem precisar do token.
Só stdlib. Nunca grava o token. Se a API falhar, grava o erro no JSON e sai com 0.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://graph.facebook.com/v22.0"
OUT = Path(__file__).with_name("estado-instagram.json")
TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
IG_ID = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
# Métricas por post, da mais completa para a mínima (a API recusa o pedido inteiro se uma não existir).
MEDIA_METRICS = ["reach,saved,shares,views,total_interactions,follows,profile_visits", "reach,saved,shares,total_interactions", "reach,saved"]


def get(path, **params):
    params["access_token"] = TOKEN
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")[:300].replace(TOKEN, "***") if TOKEN else ""
        raise RuntimeError(f"HTTP {e.code} em {path}: {msg}") from None


def insights(media_id):
    for metrics in MEDIA_METRICS:
        try:
            data = get(f"{media_id}/insights", metric=metrics)["data"]
            return {m["name"]: m["values"][0]["value"] for m in data}
        except RuntimeError:
            continue
    return {}


def score(p):
    """Peso por sinal que o algoritmo valoriza: envio > salvamento > comentário > curtida, por alcance."""
    i = p["insights"]
    reach = i.get("reach") or 0
    if not reach:
        return None
    pts = 3 * i.get("shares", 0) + 2 * i.get("saved", 0) + 2 * p["comments"] + p["likes"] + 4 * i.get("follows", 0)
    return round(100 * pts / reach, 2)


def main():
    estado = {"atualizado_em": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    if not TOKEN or not IG_ID:
        estado["erro"] = "INSTAGRAM_ACCESS_TOKEN ou INSTAGRAM_BUSINESS_ACCOUNT_ID ausente"
    else:
        try:
            estado["perfil"] = get(IG_ID, fields="username,name,biography,website,followers_count,follows_count,media_count")
            try:
                conta = get(f"{IG_ID}/insights", metric="reach,profile_views,website_clicks,follows_and_unfollows,accounts_engaged",
                            period="day", metric_type="total_value", since=int(datetime.now().timestamp()) - 28 * 86400)
                estado["conta_28d"] = {m["name"]: m.get("total_value", {}).get("value") for m in conta["data"]}
            except RuntimeError as e:
                estado["conta_28d_erro"] = str(e)
            media = get(f"{IG_ID}/media", fields="id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count", limit=40)["data"]
            posts = []
            for m in media:
                p = {
                    "data": m.get("timestamp", "")[:10],
                    "tipo": m.get("media_product_type") if m.get("media_product_type") == "REELS" else m.get("media_type"),
                    "gancho": (m.get("caption") or "").split("\n")[0][:140],
                    "link": m.get("permalink"),
                    "likes": m.get("like_count", 0),
                    "comments": m.get("comments_count", 0),
                    "insights": insights(m["id"]),
                }
                p["score"] = score(p)
                posts.append(p)
            estado["posts"] = posts
            ranqueados = sorted((p for p in posts if p["score"] is not None), key=lambda p: p["score"], reverse=True)
            estado["top5"] = [{k: p[k] for k in ("data", "tipo", "gancho", "score")} for p in ranqueados[:5]]
            estado["piores5"] = [{k: p[k] for k in ("data", "tipo", "gancho", "score")} for p in ranqueados[-5:]]
        except Exception as e:  # noqa: BLE001 — o workflow não pode quebrar por isso
            estado["erro"] = str(e)
    OUT.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"estado-instagram.json: {len(estado.get('posts', []))} posts" + (f", erro: {estado['erro']}" if "erro" in estado else ""))


if __name__ == "__main__":
    sys.exit(main())
