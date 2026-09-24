#!/usr/bin/env python3
"""
Testa a rotina cloud manualmente.
Tenta o Google Drive local primeiro (LOCAL_DRIVE_PATH, só existe no PC do
Windows); se a pasta não existir -- como em qualquer ambiente que não seja
esse PC específico -- cai pra fila versionada no repo (mesma fonte que
publish_next.py e o cron do GitHub Actions usam), via load_queue().

IMPORTANTE: mesmo com o fallback, este script só publica de verdade num
ambiente com saída de rede liberada pra graph.facebook.com e supabase.co.
Uma sessão de nuvem Claude Code roda atrás de um proxy que bloqueia os dois
por política da organização -- o teste de acesso abaixo vai falhar aí com
connect_rejected, não por bug de código. O publicador autônomo real é o
cron `.github/workflows/post-instagram-daily.yml` (runner do GitHub Actions
tem saída de rede normal); use este script só pra depuração local.
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
import requests

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import publish_next as pn  # reaproveita load_queue/build_caption/repair_mojibake já testados

# Credenciais (mesmo do .env.local)
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

SUPABASE_PROJECT_ID = "jrfjjpxjkpvuvvycyryj"
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"
SUPABASE_BUCKET = "ig-publish"

GRAPH_API_VERSION = "v22.0"
GRAPH_API_HOST = "https://graph.facebook.com"

# Path local pro teste (em cloud, viria do MCP)
LOCAL_DRIVE_PATH = Path(r"C:\Users\luizr\Meu Drive (aidealabbr@gmail.com)\Clientes\aidealab\06-Aprovados-para-Postar\FILA-SEMANA-1\02-carrossel")


def check_credentials():
    """Verifica credenciais."""
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ACCOUNT_ID or not SUPABASE_SERVICE_ROLE_KEY:
        print("[ERROR] Missing credentials in .env.local")
        sys.exit(1)


def test_access() -> bool:
    """Testa acesso Instagram."""
    url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/me/accounts"
    params = {"access_token": INSTAGRAM_ACCESS_TOKEN}

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        if "data" in data and len(data["data"]) > 0:
            print(f"[OK] Access confirmed. Accounts: {len(data['data'])}")
            return True
        else:
            print("[ERROR] System User no access to @idea_lab7")
            return False
    except Exception as e:
        print(f"[ERROR] Access test failed: {e}")
        return False


def find_next_carousel_from_repo_queue() -> dict:
    """Fallback: usa a fila versionada no repo (skills/post-instagram/queue/),
    a mesma fonte que publish_next.py e o GitHub Actions leem."""
    print(f"[SEARCH] Local Drive path unavailable -- falling back to repo queue ({pn.QUEUE_ROOT})...")

    items = [it for it in pn.load_queue() if it["kind"] == "carrossel"]
    if pn.already_posted_today(items):
        print("[STOP] 1-post-per-day guard active.")
        return None

    nxt = next((it for it in items if not it["metadata"].get("postado", False)), None)
    if not nxt:
        print("[INFO] Queue empty")
        return None

    meta = dict(nxt["metadata"])
    meta["folder_path"] = str(nxt["folder"])
    meta["folder_id"] = nxt["label"]
    meta["_meta_path"] = str(nxt["meta_path"])
    print(f"[OK] Next: {meta.get('carousel_id', 'no-id')} ({meta['folder_id']})")
    return meta


def find_next_carousel() -> dict:
    """Busca proximo carrossel com postado:false."""
    print(f"[SEARCH] Looking for next carousel...")

    if not LOCAL_DRIVE_PATH.exists():
        print(f"[ERROR] Folder not found: {LOCAL_DRIVE_PATH}")
        return find_next_carousel_from_repo_queue()

    candidates = []
    for folder in sorted(LOCAL_DRIVE_PATH.iterdir()):
        if not folder.is_dir() or folder.name.startswith('.'):
            continue

        metadata_file = folder / "metadata.json"
        if not metadata_file.exists():
            continue

        try:
            with open(metadata_file, encoding='utf-8-sig') as f:
                metadata = json.load(f)

            if metadata.get("postado") != True:
                metadata["folder_path"] = str(folder)
                metadata["folder_id"] = folder.name
                candidates.append((metadata.get("data_criacao", ""), metadata))
        except Exception as e:
            print(f"[WARN] Error reading {folder.name}: {e}")

    if not candidates:
        print("[INFO] Queue empty")
        return None

    candidates.sort()
    _, next_carousel = candidates[0]
    print(f"[OK] Next: {next_carousel.get('carousel_id', 'no-id')} ({next_carousel['folder_id']})")
    return next_carousel


def upload_to_supabase(image_path: str) -> str:
    """Sobe imagem pro Supabase."""
    try:
        from supabase import create_client

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

        filename = f"{datetime.now().strftime('%Y%m%d')}/{Path(image_path).stem}_{datetime.now().strftime('%H%M%S')}.png"
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            filename, image_bytes, {"contentType": "image/png"}
        )

        url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        print(f"  [OK] {Path(image_path).name} -> Supabase")
        return url

    except Exception as e:
        print(f"[ERROR] Supabase error: {e}")
        return None


def publish_carousel(slides: list, caption: str) -> str:
    """Publica carrossel no Instagram."""
    ig_account_id = INSTAGRAM_BUSINESS_ACCOUNT_ID

    try:
        print(f"[PUBLISH] Creating {len(slides)} slide containers...")

        # Passo 1: criar media containers pra cada slide
        child_ids = []
        for slide in sorted(slides, key=lambda s: s.get("ordem", 999)):
            image_url = slide.get("image_url")
            if not image_url:
                print(f"[ERROR] Slide {slide.get('ordem')}: no image_url")
                return None

            media_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media"
            media_payload = {
                "image_url": image_url,
                "is_carousel_item": True,
                "access_token": INSTAGRAM_ACCESS_TOKEN,
            }

            resp = requests.post(media_url, json=media_payload, timeout=30)
            resp.raise_for_status()
            media_data = resp.json()
            media_id = media_data.get("id")

            if not media_id:
                print(f"[ERROR] Slide {slide.get('ordem')} failed")
                return None

            child_ids.append(media_id)
            print(f"  [OK] Slide {slide.get('ordem')}: {media_id}")

        # Passo 2: criar container pai
        media_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media"
        media_payload = {
            "media_type": "CAROUSEL",
            "children": child_ids,
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        }

        print(f"[PUBLISH] Creating parent container...")
        resp = requests.post(media_url, json=media_payload, timeout=30)
        resp.raise_for_status()
        media_data = resp.json()
        carousel_id = media_data.get("id")

        if not carousel_id:
            print(f"[ERROR] No carousel_id")
            return None

        print(f"[OK] Carousel: {carousel_id}")

        # Passo 3: publicar
        publish_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media_publish"
        publish_payload = {
            "creation_id": carousel_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        }

        print(f"[PUBLISH] Publishing...")
        resp = requests.post(publish_url, json=publish_payload, timeout=30)
        resp.raise_for_status()
        publish_data = resp.json()
        post_id = publish_data.get("id")

        if not post_id:
            print(f"[ERROR] No post_id")
            return None

        print(f"[OK] Post ID: {post_id}")
        return post_id

    except Exception as e:
        print(f"[ERROR] {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   {e.response.text}")
        return None


def main():
    print("=" * 60)
    print("TEST: Cloud Routine Simulation")
    print("=" * 60)

    check_credentials()

    if not test_access():
        sys.exit(1)

    print(f"\n[OK] IG Account ID: {INSTAGRAM_BUSINESS_ACCOUNT_ID}")

    # Buscar proximo carrossel
    print("\n[STAGE 1] Find next carousel...")
    next_carousel = find_next_carousel()

    if not next_carousel:
        sys.exit(1)

    # Preparar slides
    print("\n[STAGE 2] Prepare slides (upload to Supabase)...")
    folder_path = next_carousel.get("folder_path")
    slides = next_carousel.get("slides", [])

    for slide in sorted(slides, key=lambda s: s.get("ordem", 999)):
        arquivo = slide.get("arquivo") or slide.get("nome")
        image_path = str(Path(folder_path) / arquivo)

        if not Path(image_path).exists():
            print(f"[ERROR] File not found: {image_path}")
            sys.exit(1)

        image_url = upload_to_supabase(image_path)
        if not image_url:
            sys.exit(1)

        slide["image_url"] = image_url

    # Publicar
    print("\n[STAGE 3] Publish to Instagram...")
    try:
        caption = pn.build_caption(next_carousel)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    post_id = publish_carousel(slides, caption)

    if not post_id:
        sys.exit(1)

    # Atualizar metadata
    print("\n[STAGE 4] Update metadata...")
    next_carousel["postado"] = True
    next_carousel["postado_em"] = datetime.now().isoformat()
    next_carousel["post_id"] = post_id

    metadata_file = Path(next_carousel.get("folder_path")) / "metadata.json"
    try:
        with open(metadata_file, "w", encoding='utf-8') as f:
            json.dump(next_carousel, f, indent=2, ensure_ascii=False)
        print(f"[OK] Metadata updated")
    except Exception as e:
        print(f"[WARN] Error updating metadata: {e}")
        sys.exit(1)

    print(f"\n[SUCCESS]")
    print(f"  Carousel: {next_carousel.get('carousel_id', '?')}")
    print(f"  Post ID: {post_id}")
    print(f"  Link: https://instagram.com/p/{post_id}")


if __name__ == "__main__":
    main()
