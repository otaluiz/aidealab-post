#!/usr/bin/env python3
"""Testa publicação de 1 carrossel: Dia2-01-A-ordem"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
import requests

# Credenciais
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_PROJECT_ID = "jrfjjpxjkpvuvvycyryj"
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"
SUPABASE_BUCKET = "ig-publish"

GRAPH_API_VERSION = "v22.0"
GRAPH_API_HOST = "https://graph.facebook.com"

# Drive local
DRIVE_PATH = r"C:\Users\luizr\Meu Drive (aidealabbr@gmail.com)\Clientes\aidealab\06-Aprovados-para-Postar\FILA-SEMANA-1\02-carrossel\Dia2-01-A-ordem"
METADATA_FILE = "metadata.json"


def check_credentials():
    """Verifica credenciais."""
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ACCOUNT_ID or not SUPABASE_SERVICE_ROLE_KEY:
        print("❌ Faltam credenciais em .env.local")
        sys.exit(1)


def upload_to_supabase(image_path: str) -> str:
    """Sobe imagem pro Supabase, retorna URL pública."""
    try:
        from supabase import create_client

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

        # Upload
        filename = f"{datetime.now().strftime('%Y%m%d')}/{Path(image_path).stem}_{datetime.now().strftime('%H%M%S')}.png"
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            filename, image_bytes, {"contentType": "image/png"}
        )

        # URL pública
        url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        return url

    except Exception as e:
        print(f"❌ Erro Supabase: {e}")
        return None


def publish_carousel(slides: list, caption: str) -> str:
    """Publica carrossel no Instagram."""
    ig_account_id = INSTAGRAM_BUSINESS_ACCOUNT_ID

    try:
        print(f"📤 Criando {len(slides)} containers de slides...")

        # Passo 1: criar media containers pra cada slide (ordem importa)
        child_ids = []
        for slide in sorted(slides, key=lambda s: s.get("ordem", 999)):
            image_path = os.path.join(DRIVE_PATH, slide["arquivo"])
            image_url = upload_to_supabase(image_path)

            if not image_url:
                return None

            media_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media"
            media_payload = {
                "image_url": image_url,
                "is_carousel_item": True,
                "access_token": INSTAGRAM_ACCESS_TOKEN,
            }

            resp = requests.post(media_url, json=media_payload, timeout=10)
            resp.raise_for_status()
            media_data = resp.json()
            media_id = media_data.get("id")

            if not media_id:
                print(f"❌ Erro no slide {slide.get('ordem')}")
                return None

            child_ids.append(media_id)
            print(f"  ✓ Slide {slide.get('ordem')}: {media_id}")

        # Passo 2: criar container pai
        media_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media"
        media_payload = {
            "media_type": "CAROUSEL",
            "children": child_ids,
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        }

        print(f"📤 Criando container pai...")
        resp = requests.post(media_url, json=media_payload, timeout=10)
        resp.raise_for_status()
        media_data = resp.json()
        carousel_id = media_data.get("id")

        if not carousel_id:
            print(f"❌ Erro: sem carousel_id")
            return None

        print(f"✓ Carrossel criado: {carousel_id}")

        # Passo 3: publicar
        publish_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media_publish"
        publish_payload = {
            "creation_id": carousel_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        }

        print(f"📬 Publicando...")
        resp = requests.post(publish_url, json=publish_payload, timeout=10)
        resp.raise_for_status()
        publish_data = resp.json()
        post_id = publish_data.get("id")

        if not post_id:
            print(f"❌ Erro: sem post_id")
            return None

        print(f"✓ Post ID: {post_id}")
        print(f"✓ Link: https://instagram.com/p/{post_id}")
        return post_id

    except Exception as e:
        print(f"❌ Erro: {e}")
        if hasattr(e, 'response'):
            print(f"   Resposta: {e.response.text}")
        return None


def main():
    print("=" * 60)
    print("🧪 TESTE DE CARROSSEL")
    print("=" * 60)

    check_credentials()

    # Lê metadata
    metadata_path = os.path.join(DRIVE_PATH, METADATA_FILE)
    with open(metadata_path, encoding='utf-8') as f:
        metadata = json.load(f)

    legenda = metadata["legenda"] + "\n\n" + " ".join(metadata["hashtags"])

    print(f"\n📸 Carrossel: {metadata.get('carousel_id')}")
    print(f"📝 Legenda (preview): {legenda[:100]}...")
    print(f"📊 Slides: {len(metadata['slides'])}")

    print(f"\n1️⃣  Uploadando slides → Supabase")
    print(f"2️⃣  Publicando → Instagram")

    post_id = publish_carousel(metadata["slides"], legenda)

    if post_id:
        print(f"\n✅ SUCESSO!")
        print(f"   Post ID: {post_id}")
        print(f"   Link: https://instagram.com/p/{post_id}")

        # Atualiza metadata
        metadata["postado"] = True
        metadata["postado_em"] = datetime.now().isoformat()
        metadata["post_id"] = post_id

        with open(metadata_path, "w", encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"   Metadata atualizado ✓")
    else:
        print(f"\n❌ FALHA")
        sys.exit(1)


if __name__ == "__main__":
    main()
