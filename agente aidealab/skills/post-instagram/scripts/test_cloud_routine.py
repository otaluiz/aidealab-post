#!/usr/bin/env python3
"""
Valida rotina cloud manualmente.
MODO CLOUD:
- Verifica credenciais, nao tenta conectar a graph.facebook.com (bloqueado por proxy)
- Lista proximo item nao publicado da fila versionada no repo
- Reporta o que seria publicado (dry-run)
MODO LOCAL:
- Tenta local Google Drive primeiro
- Fallback para fila do repo se nao encontrar local
- Testa acesso Instagram
- Publica de verdade se tiver acesso
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
import requests
from typing import Optional, Dict, Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import publish_next as pn

# Credenciais
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

SUPABASE_PROJECT_ID = "jrfjjpxjkpvuvvycyryj"
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"
SUPABASE_BUCKET = "ig-publish"

GRAPH_API_VERSION = "v22.0"
GRAPH_API_HOST = "https://graph.facebook.com"

# Path local pro teste (Windows only) - hardcoded, nao existe em cloud
LOCAL_DRIVE_PATH = Path(r"C:\Users\luizr\Meu Drive (aidealabbr@gmail.com)\Clientes\aidealab\06-Aprovados-para-Postar\FILA-SEMANA-1\02-carrossel")


def check_credentials() -> bool:
    """Verifica credenciais. Retorna True se OK."""
    missing = []
    if not INSTAGRAM_ACCESS_TOKEN:
        missing.append("INSTAGRAM_ACCESS_TOKEN")
    if not INSTAGRAM_BUSINESS_ACCOUNT_ID:
        missing.append("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    if not SUPABASE_SERVICE_ROLE_KEY:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")

    if missing:
        print(f"[ERROR] Missing: {', '.join(missing)}")
        return False

    print("[OK] Credentials verified")
    return True


def is_cloud_environment() -> bool:
    """Detecta se esta rodando em cloud (proxy bloqueando graph.facebook.com)."""
    try:
        resp = requests.head(GRAPH_API_HOST, timeout=2)
        return False  # Se conseguiu conectar, nao eh cloud
    except requests.exceptions.ProxyError:
        return True  # Proxy error = cloud environment
    except requests.exceptions.ConnectionError:
        return True  # Connection denied = likely cloud
    except Exception:
        return True  # Default para cloud (mais seguro)


def test_instagram_access() -> bool:
    """Testa acesso Instagram. Retorna False se nao tiver acesso."""
    url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/me/accounts"
    params = {"access_token": INSTAGRAM_ACCESS_TOKEN}

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        if "data" in data and len(data["data"]) > 0:
            print(f"[OK] Instagram access confirmed")
            return True
        else:
            print("[ERROR] No Instagram accounts found")
            return False
    except requests.exceptions.ProxyError:
        print("[INFO] Cloud environment detected (proxy blocks Instagram API)")
        return False
    except Exception as e:
        print(f"[WARN] Cannot reach Instagram API: {e}")
        return False


def find_next_carousel_from_repo_queue() -> Optional[Dict[str, Any]]:
    """Le fila versionada no repo (mesma fonte que publish_next.py)."""
    print(f"[SEARCH] Reading queue from repo ({pn.QUEUE_ROOT})...")

    items = [it for it in pn.load_queue() if it["kind"] == "carrossel"]
    if pn.already_posted_today(items):
        print("[INFO] 1-post-per-day limit reached")
        return None

    nxt = next((it for it in items if not it["metadata"].get("postado", False)), None)
    if not nxt:
        print("[INFO] Queue empty - all items already posted")
        return None

    meta = dict(nxt["metadata"])
    meta["folder_path"] = str(nxt["folder"])
    meta["folder_id"] = nxt["label"]
    meta["_meta_path"] = str(nxt["meta_path"])
    print(f"[OK] Next carousel: {meta.get('carousel_id', 'no-id')} ({meta['folder_id']})")
    return meta


def find_next_carousel() -> Optional[Dict[str, Any]]:
    """Busca proximo carrossel (local first, fallback repo)."""
    print(f"[SEARCH] Looking for next carousel...")

    if not LOCAL_DRIVE_PATH.exists():
        print(f"[SEARCH] Local Drive unavailable: {LOCAL_DRIVE_PATH}")
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
        print("[INFO] Local queue empty, checking repo queue")
        return find_next_carousel_from_repo_queue()

    candidates.sort()
    _, next_carousel = candidates[0]
    print(f"[OK] Next carousel: {next_carousel.get('carousel_id', 'no-id')} ({next_carousel['folder_id']})")
    return next_carousel


def upload_to_supabase(image_path: str, dry_run: bool = False) -> Optional[str]:
    """Sobe imagem pro Supabase (ou valida em dry-run)."""
    path_obj = Path(image_path)
    if not path_obj.exists():
        print(f"  [ERROR] File not found: {image_path}")
        return None

    if dry_run:
        filename = f"{datetime.now().strftime('%Y%m%d')}/{path_obj.stem}.png"
        url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        print(f"  [DRY-RUN] {path_obj.name} -> would upload to {filename}")
        return url

    try:
        from supabase import create_client

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

        filename = f"{datetime.now().strftime('%Y%m%d')}/{path_obj.stem}_{datetime.now().strftime('%H%M%S')}.png"
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            filename, image_bytes, {"contentType": "image/png"}
        )

        url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        print(f"  [OK] {path_obj.name} uploaded to Supabase")
        return url

    except Exception as e:
        print(f"  [ERROR] Supabase: {e}")
        return None


def publish_carousel(slides: list, caption: str, dry_run: bool = False) -> Optional[str]:
    """Publica carrossel no Instagram (ou valida em dry-run)."""
    ig_account_id = INSTAGRAM_BUSINESS_ACCOUNT_ID

    if dry_run:
        print(f"[DRY-RUN] Would publish {len(slides)} slides")
        print(f"[DRY-RUN] Caption preview: {caption[:100]}...")
        return "dry-run-id-12345"

    try:
        print(f"[PUBLISH] Creating {len(slides)} slide containers...")

        # Passo 1: criar media containers pra cada slide
        child_ids = []
        for slide in sorted(slides, key=lambda s: s.get("ordem", 999)):
            image_url = slide.get("image_url")
            if not image_url:
                print(f"  [ERROR] Slide {slide.get('ordem')}: missing image_url")
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
                print(f"  [ERROR] Slide {slide.get('ordem')} failed")
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
            print(f"  [ERROR] No carousel_id returned")
            return None

        print(f"  [OK] Carousel: {carousel_id}")

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
            print(f"  [ERROR] No post_id returned")
            return None

        print(f"  [OK] Post ID: {post_id}")
        return post_id

    except requests.exceptions.ProxyError as e:
        print(f"[ERROR] Proxy error (cloud environment): {e}")
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   {e.response.text}")
        return None


def main():
    print("=" * 70)
    print("INSTAGRAM PUBLISHING VALIDATOR")
    print("=" * 70)

    # 1. Verificar credenciais
    if not check_credentials():
        sys.exit(1)

    # 2. Detectar ambiente
    in_cloud = is_cloud_environment()
    if in_cloud:
        print("[INFO] Cloud environment detected (dry-run mode)")
        dry_run = True
    else:
        print("[INFO] Local environment detected")
        # 3. Tentar testar acesso ao Instagram
        has_ig_access = test_instagram_access()
        dry_run = not has_ig_access
        if dry_run:
            print("[INFO] Instagram unreachable, using dry-run mode")

    print(f"[INFO] Account ID: {INSTAGRAM_BUSINESS_ACCOUNT_ID}")

    # 4. Buscar proximo carrossel
    print("\n[STAGE 1] Find next carousel...")
    next_carousel = find_next_carousel()

    if not next_carousel:
        print("[STOP] No carousel to process")
        sys.exit(0)  # Exit successfully - queue just empty

    # 5. Preparar slides
    print("\n[STAGE 2] Prepare slides...")
    folder_path = next_carousel.get("folder_path")
    slides = next_carousel.get("slides", [])

    if not slides:
        print("[ERROR] Carousel has no slides")
        sys.exit(1)

    for slide in sorted(slides, key=lambda s: s.get("ordem", 999)):
        arquivo = slide.get("arquivo") or slide.get("nome")
        image_path = str(Path(folder_path) / arquivo)

        image_url = upload_to_supabase(image_path, dry_run=dry_run)
        if not image_url:
            sys.exit(1)

        slide["image_url"] = image_url

    # 6. Publicar (ou validar)
    print("\n[STAGE 3] Publish...")
    try:
        caption = pn.build_caption(next_carousel)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    post_id = publish_carousel(slides, caption, dry_run=dry_run)

    if not post_id:
        sys.exit(1)

    # 7. Atualizar metadata (apenas se publicou de verdade)
    if not dry_run:
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
            print(f"[ERROR] Failed to update metadata: {e}")
            sys.exit(1)

    # Success report
    print("\n" + "=" * 70)
    if dry_run:
        print("[OK] VALIDATION SUCCESSFUL (DRY-RUN)")
        print(f"  Carousel: {next_carousel.get('carousel_id', '?')}")
        print(f"  Slides: {len(slides)}")
        print(f"  Status: Ready to publish (when network available)")
    else:
        print("[OK] PUBLISHED SUCCESSFULLY")
        print(f"  Carousel: {next_carousel.get('carousel_id', '?')}")
        print(f"  Post ID: {post_id}")
        print(f"  Link: https://instagram.com/p/{post_id}")
    print("=" * 70)


if __name__ == "__main__":
    main()
