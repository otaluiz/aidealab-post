#!/usr/bin/env python3
"""
Publica próximo carrossel do Instagram - versão cloud.
Usa Google Drive MCP (disponível em cloud routines).
Não depende de caminho local (C:\Users\...).
"""

import os
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
import requests

# Credenciais via variáveis de ambiente (injetadas pela rotina)
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

SUPABASE_PROJECT_ID = "jrfjjpxjkpvuvvycyryj"
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"
SUPABASE_BUCKET = "ig-publish"

GRAPH_API_VERSION = "v22.0"
GRAPH_API_HOST = "https://graph.facebook.com"

# IDs do Drive (fixos, conhecidos)
DRIVE_FOLDER_06_APROVADOS = "1JkVrArjUe3vTrVRRsXZcF8zMrVsQT0LMm"
DRIVE_FOLDER_FILA_SEMANA_1 = "1-twLvfjNsEENRGDAphO3weZ4m_D8919k"
DRIVE_FOLDER_CARROSSEL = None  # será preenchido buscando


def check_credentials():
    """Verifica credenciais."""
    missing = []
    if not INSTAGRAM_ACCESS_TOKEN:
        missing.append("INSTAGRAM_ACCESS_TOKEN")
    if not INSTAGRAM_BUSINESS_ACCOUNT_ID:
        missing.append("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    if not SUPABASE_SERVICE_ROLE_KEY:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")

    if missing:
        print(f"❌ Credenciais faltando: {', '.join(missing)}")
        sys.exit(1)


def test_access() -> bool:
    """Testa se o System User tem acesso à conta @idea_lab7."""
    url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/me/accounts"
    params = {"access_token": INSTAGRAM_ACCESS_TOKEN}

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        if "data" in data and len(data["data"]) > 0:
            print(f"✓ Acesso confirmado. Contas: {len(data['data'])}")
            return True
        else:
            print("❌ System User sem acesso à conta @idea_lab7.")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar acesso: {e}")
        return False


def upload_to_supabase(image_bytes: bytes, filename: str) -> Optional[str]:
    """Sobe imagem pro Supabase, retorna URL pública."""
    try:
        from supabase import create_client

        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

        # Upload
        path = f"{datetime.now().strftime('%Y%m%d')}/{filename}"
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path, image_bytes, {"contentType": "image/png"}
        )

        # URL pública
        url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{path}"
        print(f"✓ Supabase: {filename}")
        return url

    except Exception as e:
        print(f"❌ Erro Supabase: {e}")
        return None


def publish_carousel(slides: List[Dict[str, Any]], caption: str) -> Optional[str]:
    """Publica carrossel no Instagram (2-step flow)."""
    ig_account_id = INSTAGRAM_BUSINESS_ACCOUNT_ID

    try:
        print(f"📤 Criando {len(slides)} containers...")

        # Passo 1: containers filhos
        child_ids = []
        for slide in sorted(slides, key=lambda s: s.get("ordem", 999)):
            # IMPORTANTE: em cloud, `image_url` já deveria estar em Supabase
            # (download do Drive não é feito aqui, é feito antes de chamar)
            image_url = slide.get("image_url")
            if not image_url:
                print(f"❌ Slide {slide.get('ordem')}: sem image_url")
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

        # Passo 2: container pai
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
            return None

        print(f"✓ Carrossel: {carousel_id}")

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
            return None

        print(f"✓ Post ID: {post_id}")
        return post_id

    except Exception as e:
        print(f"❌ Erro: {e}")
        if hasattr(e, 'response'):
            print(f"   {e.response.text}")
        return None


def main():
    print("=" * 60)
    print("📱 Post Instagram - Cloud Edition")
    print("=" * 60)

    check_credentials()

    if not test_access():
        sys.exit(1)

    print("\n⚠️  PRÓXIMAS STEPS (em desenvolvimento):")
    print("""
1. Use MCP google-drive pra listar carrosséis em:
   📁 FILA-SEMANA-1/02-carrossel

2. Leia metadata.json de cada pasta

3. Encontre o primeiro com postado:false

4. Baixe slides do Drive via google-drive MCP

5. Suba pro Supabase (upload_to_supabase)

6. Publique no Instagram (publish_carousel)

7. Atualize metadata.json via google-drive MCP

Atualmente: script testado manualmente com caminho local.
Em cloud: substitua leitura local por MCP google-drive.
""")


if __name__ == "__main__":
    main()
