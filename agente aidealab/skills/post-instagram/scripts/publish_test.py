#!/usr/bin/env python3
"""Testa publicação de 1 imagem: Dia1-design.png"""

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
DRIVE_PATH = r"C:\Users\luizr\Meu Drive (aidealabbr@gmail.com)\Clientes\aidealab\06-Aprovados-para-Postar\FILA-SEMANA-1\01-Imagem"
IMAGE_FILE = "Dia1-design.png"


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

        # Upload (timestamp no nome pra evitar duplicata)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = Path(image_path).stem
        filename = f"{datetime.now().strftime('%Y%m%d')}/{name}_{ts}.png"
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            filename, image_bytes, {"contentType": "image/png"}
        )

        # URL pública
        url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        print(f"✓ Supabase: {url}")
        return url

    except Exception as e:
        print(f"❌ Erro Supabase: {e}")
        return None


def publish_image(image_url: str, caption: str) -> str:
    """Publica imagem no Instagram."""
    ig_account_id = INSTAGRAM_BUSINESS_ACCOUNT_ID

    try:
        # Passo 1: criar container
        media_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media"
        media_payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        }

        print("📤 POST /media (criar container)...")
        resp = requests.post(media_url, json=media_payload, timeout=10)
        resp.raise_for_status()
        media_data = resp.json()
        media_id = media_data.get("id")

        if not media_id:
            print(f"❌ Sem media_id: {media_data}")
            return None

        print(f"✓ Media ID: {media_id}")

        # Passo 2: publicar
        publish_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media_publish"
        publish_payload = {
            "creation_id": media_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        }

        print("📬 POST /media_publish (publicar)...")
        resp = requests.post(publish_url, json=publish_payload, timeout=10)
        resp.raise_for_status()
        publish_data = resp.json()
        post_id = publish_data.get("id")

        if not post_id:
            print(f"❌ Sem post_id: {publish_data}")
            return None

        print(f"✓ Post ID: {post_id}")
        print(f"✓ Link: https://instagram.com/p/{post_id}")
        return post_id

    except Exception as e:
        print(f"❌ Erro publicação: {e}")
        if hasattr(e, 'response'):
            print(f"   Resposta: {e.response.text}")
        return None


def main():
    print("=" * 60)
    print("🧪 TESTE DE PUBLICAÇÃO")
    print("=" * 60)

    check_credentials()

    image_path = os.path.join(DRIVE_PATH, IMAGE_FILE)
    if not os.path.exists(image_path):
        print(f"❌ Imagem não encontrada: {image_path}")
        sys.exit(1)

    # Lê metadata
    metadata_path = image_path.replace(".png", ".metadata.json")
    with open(metadata_path) as f:
        metadata = json.load(f)

    legenda = metadata["legenda"] + "\n\n" + " ".join(metadata["hashtags"])

    print(f"\n📸 Imagem: {IMAGE_FILE}")
    print(f"📝 Legenda (preview): {legenda[:100]}...")
    print(f"\n1️⃣  Upload → Supabase")

    image_url = upload_to_supabase(image_path)
    if not image_url:
        sys.exit(1)

    print(f"\n2️⃣  Publicar → Instagram")
    post_id = publish_image(image_url, legenda)

    if post_id:
        print(f"\n✅ SUCESSO!")
        print(f"   Post ID: {post_id}")
        print(f"   Link: https://instagram.com/p/{post_id}")

        # Atualiza metadata
        metadata["postado"] = True
        metadata["postado_em"] = datetime.now().isoformat()
        metadata["post_id"] = post_id

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"   Metadata atualizado ✓")
    else:
        print(f"\n❌ FALHA na publicação")
        sys.exit(1)


if __name__ == "__main__":
    main()
