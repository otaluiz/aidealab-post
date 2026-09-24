#!/usr/bin/env python3
"""
Publica o próximo conteúdo aprovado no Instagram.
Fila vive versionada no repo (skills/post-instagram/queue/), commitada pelo
fluxo de aprovação -- assim local e GitHub Actions leem a mesma fonte, sem
depender do Google Drive sincronizado (que só existe nesta máquina).
Lê credenciais de variáveis de ambiente (ou de um .env.local ao lado do script,
pra rodar local sem precisar setar env var na mão).
Fila mistura dois formatos, na mesma ordem Dia1, Dia2, Dia3...:
  - 01-Imagem/DiaN-slug.png + DiaN-slug.metadata.json (sidecar, imagem única)
  - 02-carrossel/DiaN-slug/metadata.json + slides (pasta, carrossel)
Publica no máximo 1 item por execução, nunca duas vezes no mesmo dia.
"""

import os
import re
import sys
import json
import time
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, Any, List

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR.parent.parent.parent / "automation" / ".env.local"

QUEUE_ROOT = SCRIPT_DIR.parent / "queue"

GRAPH_API_VERSION = "v22.0"
GRAPH_API_HOST = "https://graph.facebook.com"
SUPABASE_PROJECT_ID = "jrfjjpxjkpvuvvycyryj"
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"
SUPABASE_BUCKET = "ig-publish"

DIA_RE = re.compile(r"Dia(\d+)([a-z]?)", re.IGNORECASE)


def repair_mojibake(s: str) -> str:
    """Undoes a cp1252<->utf-8 double-encoding round trip (e.g. 'nÃ£o' -> 'não').
    Clean text fails the round trip and is returned unchanged."""
    cur = s
    for _ in range(3):
        try:
            nxt = cur.encode("cp1252").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            break
        if nxt == cur:
            break
        cur = nxt
    return cur


MOJIBAKE_MARKERS = ("Ã", "â€", "Â")


def has_mojibake(s: str) -> bool:
    return any(m in s for m in MOJIBAKE_MARKERS)


def load_env_file(path: Path) -> None:
    """Carrega KEY=VALUE de um .env.local pras env vars do processo, se ainda não setadas."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file(ENV_FILE)

INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def dia_key(name: str):
    m = DIA_RE.search(name)
    if not m:
        return (9999, "")
    return (int(m.group(1)), m.group(2).lower())


def check_credentials():
    missing = [
        n
        for n, v in [
            ("INSTAGRAM_ACCESS_TOKEN", INSTAGRAM_ACCESS_TOKEN),
            ("INSTAGRAM_BUSINESS_ACCOUNT_ID", INSTAGRAM_BUSINESS_ACCOUNT_ID),
            ("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_SERVICE_ROLE_KEY),
        ]
        if not v
    ]
    if missing:
        print(f"[ERROR] Credenciais faltando: {', '.join(missing)}")
        sys.exit(1)


def test_access() -> bool:
    url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/me/accounts"
    try:
        resp = requests.get(url, params={"access_token": INSTAGRAM_ACCESS_TOKEN}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("data"):
            print(f"[OK] Acesso confirmado. Contas: {len(data['data'])}")
            return True
        print("[ERROR] System User sem acesso à conta.")
        return False
    except Exception as e:
        print(f"[ERROR] Erro ao testar acesso: {e}")
        return False


def load_queue() -> List[Dict[str, Any]]:
    """Escaneia 01-Imagem (sidecar) e 02-carrossel (pasta) de todas as FILA-SEMANA-*."""
    items = []
    for fila in sorted(QUEUE_ROOT.glob("FILA-SEMANA-*")):
        imagem_dir = fila / "01-Imagem"
        if imagem_dir.exists():
            for meta_file in imagem_dir.glob("*.metadata.json"):
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8-sig"))
                except Exception as e:
                    print(f"[WARN] {meta_file.name}: {e}")
                    continue
                label = meta_file.name[: -len(".metadata.json")]
                items.append(
                    {
                        "kind": "imagem",
                        "sort_key": dia_key(label),
                        "meta_path": meta_file,
                        "folder": imagem_dir,
                        "metadata": meta,
                        "label": label,
                    }
                )
        carrossel_dir = fila / "02-carrossel"
        if carrossel_dir.exists():
            for post_dir in sorted(p for p in carrossel_dir.iterdir() if p.is_dir()):
                meta_file = post_dir / "metadata.json"
                if not meta_file.exists():
                    continue
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8-sig"))
                except Exception as e:
                    print(f"[WARN] {meta_file.name}: {e}")
                    continue
                items.append(
                    {
                        "kind": "carrossel",
                        "sort_key": dia_key(post_dir.name),
                        "meta_path": meta_file,
                        "folder": post_dir,
                        "metadata": meta,
                        "label": post_dir.name,
                    }
                )
    items.sort(key=lambda it: it["sort_key"])
    return items


def already_posted_today(items: List[Dict[str, Any]]) -> bool:
    today = date.today().isoformat()
    for it in items:
        postado_em = it["metadata"].get("postado_em", "")
        if postado_em.startswith(today):
            print(f"[GUARD] {it['label']} já foi postado hoje ({postado_em}). Só 1 post por dia.")
            return True
    return False


def find_next(items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for it in items:
        if not it["metadata"].get("postado", False):
            return it
    return None


def upload_to_supabase(image_path: Path) -> Optional[str]:
    try:
        from supabase import create_client

        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        image_bytes = image_path.read_bytes()
        remote_path = f"{datetime.now().strftime('%Y%m%d')}/{image_path.stem}_{datetime.now().strftime('%H%M%S')}.png"
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            remote_path, image_bytes, {"contentType": "image/png"}
        )
        url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{remote_path}"
        print(f"  [OK] {image_path.name} -> Supabase")
        return url
    except Exception as e:
        print(f"[ERROR] Supabase upload falhou ({image_path.name}): {e}")
        return None


def raise_checked(resp: requests.Response) -> None:
    """Como resp.raise_for_status(), mas loga o corpo (a Graph API só explica o erro ali)."""
    if resp.ok:
        return
    print(f"[ERROR] {resp.status_code} {resp.request.method} {resp.url}: {resp.text[:500]}")
    resp.raise_for_status()


def wait_for_container_ready(container_id: str, timeout_s: int = 90, poll_s: int = 3) -> bool:
    """Espera um media container chegar em status_code=FINISHED antes do media_publish
    -- a Graph API rejeita a publicação com 400 se o container ainda está processando."""
    url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{container_id}"
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        resp = requests.get(
            url, params={"fields": "status_code", "access_token": INSTAGRAM_ACCESS_TOKEN}, timeout=30
        )
        raise_checked(resp)
        status = resp.json().get("status_code")
        if status == "FINISHED":
            return True
        if status in ("ERROR", "EXPIRED"):
            print(f"[ERROR] Container {container_id} status={status}")
            return False
        time.sleep(poll_s)
    print(f"[ERROR] Container {container_id} não ficou pronto em {timeout_s}s")
    return False


def publish_image(image_url: str, caption: str, ig_account_id: str) -> Optional[str]:
    media_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media"
    resp = requests.post(
        media_url,
        json={"image_url": image_url, "caption": caption, "access_token": INSTAGRAM_ACCESS_TOKEN},
        timeout=30,
    )
    raise_checked(resp)
    media_id = resp.json().get("id")
    if not media_id:
        print(f"[ERROR] Sem media_id: {resp.json()}")
        return None

    if not wait_for_container_ready(media_id):
        return None

    publish_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media_publish"
    resp = requests.post(
        publish_url,
        json={"creation_id": media_id, "access_token": INSTAGRAM_ACCESS_TOKEN},
        timeout=30,
    )
    raise_checked(resp)
    return resp.json().get("id")


def publish_carousel(child_urls: List[str], caption: str, ig_account_id: str) -> Optional[str]:
    media_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media"
    child_ids = []
    for url in child_urls:
        resp = requests.post(
            media_url,
            json={"image_url": url, "is_carousel_item": True, "access_token": INSTAGRAM_ACCESS_TOKEN},
            timeout=30,
        )
        raise_checked(resp)
        media_id = resp.json().get("id")
        if not media_id:
            print(f"[ERROR] Slide sem media_id: {resp.json()}")
            return None
        child_ids.append(media_id)
        print(f"  [OK] slide -> {media_id}")

    for media_id in child_ids:
        if not wait_for_container_ready(media_id):
            return None

    resp = requests.post(
        media_url,
        json={
            "media_type": "CAROUSEL",
            "children": child_ids,
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        },
        timeout=30,
    )
    raise_checked(resp)
    carousel_id = resp.json().get("id")
    if not carousel_id:
        print(f"[ERROR] Sem carousel_id: {resp.json()}")
        return None

    if not wait_for_container_ready(carousel_id):
        return None

    publish_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media_publish"
    resp = requests.post(
        publish_url,
        json={"creation_id": carousel_id, "access_token": INSTAGRAM_ACCESS_TOKEN},
        timeout=30,
    )
    raise_checked(resp)
    return resp.json().get("id")


def build_caption(meta: Dict[str, Any]) -> str:
    legenda = repair_mojibake(meta.get("legenda", ""))
    tags = meta.get("hashtags", [])
    hashtags = repair_mojibake(tags) if isinstance(tags, str) else " ".join(repair_mojibake(t) for t in tags)
    caption = f"{legenda}\n\n{hashtags}".strip()
    if has_mojibake(caption):
        raise ValueError(f"Legenda ainda com caracteres corrompidos após reparo: {caption[:200]!r}")
    return caption


def list_recent_media(limit: int = 5) -> None:
    """Diagnóstico: lista os últimos posts reais da conta (id, timestamp, início da legenda)."""
    url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
    resp = requests.get(
        url,
        params={"fields": "id,caption,timestamp,permalink", "limit": limit, "access_token": INSTAGRAM_ACCESS_TOKEN},
        timeout=30,
    )
    resp.raise_for_status()
    for item in resp.json().get("data", []):
        caption = (item.get("caption") or "").replace("\n", " ")[:80]
        print(f"[RECENT] {item.get('timestamp')}  id={item.get('id')}  {item.get('permalink')}  \"{caption}\"")


def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    print("=" * 60)
    print("Post Instagram - Publicar Próximo" + (" (DRY RUN)" if dry_run else ""))
    print("=" * 60)

    check_credentials()

    if "--list-recent" in sys.argv:
        if not test_access():
            sys.exit(1)
        list_recent_media()
        return

    items = load_queue()
    if not items:
        print("[INFO] Fila vazia (nenhum item encontrado).")
        return

    if not force and already_posted_today(items):
        print("[STOP] Nada publicado — guarda de 1-post-por-dia ativa. Use --force pra ignorar.")
        return

    nxt = find_next(items)
    if not nxt:
        print("[INFO] Fila vazia — tudo já postado.")
        return

    print(f"[NEXT] {nxt['kind']}: {nxt['label']}")

    if not test_access():
        sys.exit(1)
    ig_account_id = INSTAGRAM_BUSINESS_ACCOUNT_ID

    meta = nxt["metadata"]
    try:
        caption = build_caption(meta)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    if dry_run:
        print(f"[DRY-RUN] Publicaria {nxt['kind']} '{nxt['label']}' com legenda:\n{caption}")
        return

    if nxt["kind"] == "imagem":
        image_path = nxt["folder"] / meta["arquivo"]
        if not image_path.exists():
            prefixed = nxt["folder"] / f"{nxt['label']}.png"
            if prefixed.exists():
                image_path = prefixed
            else:
                print(f"[ERROR] Arquivo não encontrado: {image_path} (nem {prefixed})")
                sys.exit(1)
        image_url = upload_to_supabase(image_path)
        if not image_url:
            sys.exit(1)
        post_id = publish_image(image_url, caption, ig_account_id)
    else:
        slides = sorted(meta.get("slides", []), key=lambda s: s.get("ordem", 999))
        child_urls = []
        for slide in slides:
            arquivo = slide.get("arquivo") or slide.get("nome")
            if not arquivo:
                print(f"[ERROR] Slide sem 'arquivo'/'nome': {slide}")
                sys.exit(1)
            image_path = nxt["folder"] / arquivo
            if not image_path.exists():
                print(f"[ERROR] Slide não encontrado: {image_path}")
                sys.exit(1)
            url = upload_to_supabase(image_path)
            if not url:
                sys.exit(1)
            child_urls.append(url)
        post_id = publish_carousel(child_urls, caption, ig_account_id)

    if not post_id:
        print("[FAIL] Publicação não completou.")
        sys.exit(1)

    meta["postado"] = True
    meta["postado_em"] = datetime.now().isoformat()
    meta["post_id"] = post_id
    nxt["meta_path"].write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n[SUCCESS] {nxt['label']} publicado. Post ID: {post_id}")


if __name__ == "__main__":
    main()
