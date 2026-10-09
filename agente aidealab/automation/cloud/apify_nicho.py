"""Lê o nicho da aidealab no Instagram pela Apify e grava estado-nicho.json.

Roda toda segunda no GitHub Actions (nicho-semanal.yml), antes da rotina de carrossel. Usa o ApifyClient da skill
instagram-skills (actors apify~instagram-hashtag-scraper e apify~instagram-profile-scraper, sem login).
- perfil @idea_lab7 e das contas de referência (clientes/aidealab/campanha/referencias-nicho.json);
- top posts de cada hashtag do nicho;
- engajamento normalizado pelo tamanho da conta (regra da ig-audience-insights: senão só ganha quem é grande);
- descobre contas novas do nicho (donos dos melhores posts) e sugere como referência.
Sem APIFY_TOKEN grava o erro no JSON e sai com 0. Nunca inventa número.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[1]
sys.path.insert(0, str(REPO / ".claude" / "skills" / "instagram-skills"))
OUT = AQUI / "estado-nicho.json"
REFS = REPO / "agente aidealab" / "clientes" / "aidealab" / "campanha" / "referencias-nicho.json"
HASHTAGS = ["iaparanegocios", "pequenosnegocios", "whatsappbusiness", "marketingdigital", "empreendedorismo"]
POR_HASHTAG = 20
PERFIS_MAX = 15  # quantos donos de post buscar para normalizar (custo da Apify)


def engajamento(p):
    return (p.get("likes") or 0) + 3 * (p.get("comments") or 0)


def main():
    estado = {"atualizado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "hashtags": HASHTAGS}
    if not os.environ.get("APIFY_TOKEN"):
        estado["erro"] = "APIFY_TOKEN ausente"
        OUT.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("estado-nicho.json: sem APIFY_TOKEN")
        return 0
    from lib.apify_client import ApifyClient, ApifyError

    api = ApifyClient()
    refs = json.loads(REFS.read_text(encoding="utf-8")) if REFS.exists() else {"contas": []}
    erros, posts = [], []
    for h in HASHTAGS:
        try:
            for p in api.fetch_niche_posts(h, max_items=POR_HASHTAG):
                p["hashtag"] = h
                posts.append(p)
        except ApifyError as e:
            erros.append(f"#{h}: {e}")
    unicos = {p["id"]: p for p in posts if p.get("id")}.values()
    ranqueados = sorted(unicos, key=engajamento, reverse=True)

    perfis = {}
    alvo = ["idea_lab7"] + [c["username"] for c in refs.get("contas", [])]
    alvo += [p["owner"] for p in ranqueados if p.get("owner")]
    for u in dict.fromkeys(alvo):
        if len(perfis) >= PERFIS_MAX + 1 + len(refs.get("contas", [])):
            break
        try:
            perfis[u] = api.fetch_profile(u)
        except ApifyError as e:
            erros.append(f"@{u}: {e}")

    for p in ranqueados:
        seg = (perfis.get(p.get("owner")) or {}).get("followers")
        p["seguidores_dono"] = seg
        p["eng_por_mil"] = round(1000 * engajamento(p) / seg, 2) if seg else None
        p["gancho"] = (p.get("caption") or "").split("\n")[0][:160]
        p.pop("caption", None)
    normalizados = sorted((p for p in ranqueados if p["eng_por_mil"] is not None), key=lambda p: p["eng_por_mil"],
                          reverse=True)
    formatos = {}
    for p in normalizados[:20]:
        formatos[p.get("type") or "?"] = formatos.get(p.get("type") or "?", 0) + 1

    conhecidas = {c["username"] for c in refs.get("contas", [])} | {"idea_lab7"}
    sugeridas = [p["owner"] for p in normalizados[:20] if p.get("owner") and p["owner"] not in conhecidas]
    estado.update(
        perfil=perfis.get("idea_lab7"),
        referencias=[perfis.get(c["username"]) for c in refs.get("contas", []) if perfis.get(c["username"])],
        top_normalizado=normalizados[:15],
        top_absoluto=ranqueados[:10],
        formatos_top20=formatos,
        contas_sugeridas=list(dict.fromkeys(sugeridas))[:10],
        erros=erros,
    )
    OUT.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"estado-nicho.json: {len(ranqueados)} posts, {len(perfis)} perfis, {len(erros)} erros")
    return 0


if __name__ == "__main__":
    sys.exit(main())
