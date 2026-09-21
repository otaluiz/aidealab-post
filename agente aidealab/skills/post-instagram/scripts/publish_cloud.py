#!/usr/bin/env python3
"""
Publica próximo carrossel do Instagram - versão cloud.
Usa Google Drive MCP (disponível em cloud routines).
Não depende de caminho local (C:\Users\...).

Em cloud, a rotina injeta:
- INSTAGRAM_ACCESS_TOKEN
- INSTAGRAM_BUSINESS_ACCOUNT_ID
- SUPABASE_SERVICE_ROLE_KEY
- GOOGLE_DRIVE_MCP_ENABLED (True se MCP disponível)

Fluxo:
1. Lista pastas em 06-Aprovados-para-Postar/FILA-SEMANA-1/02-carrossel
2. Lê metadata.json de cada pasta, ordena por data_criacao
3. Pega primeiro com postado:false
4. Baixa imagens do Drive → Supabase
5. Publica no Instagram
6. Atualiza metadata.json postado:true
"""

import os
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
import requests

# Credenciais via variáveis de ambiente (injetadas pela rotina cloud)
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
DRIVE_FOLDER_CARROSSEL = "1-twLvfjNsEENRGDAphO3weZ4m_D8919k"  # FILA-SEMANA-1/02-carrossel


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


def list_carousel_folders() -> List[Dict[str, Any]]:
    """
    Lista pastas em DRIVE_FOLDER_CARROSSEL (02-carrossel).
    Retorna: [{"name": "Dia2-01-A-ordem", "id": "...", "metadata_id": "..."}, ...]
    Em cloud, usa google-drive MCP; local usa glob.
    """
    try:
        # Em cloud routine, google-drive MCP tools estão disponíveis
        # Importar dinamicamente pra não quebrar se rodar local sem MCP
        from google.auth.transport.requests import Request
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build

        # Em cloud, credenciais vêm da ambiente/service account
        # Por enquanto, tenta detectar se MCP tá disponível
        print(f"🔍 Listando carrosséis em {DRIVE_FOLDER_CARROSSEL}...")

        # NOTA: Implementação real depende de google-drive MCP estar
        # conectado na cloud routine. Por enquanto, retorna lista vazia
        # e aviso. Próxima etapa: integrar MCP API calls aqui.
        print("⚠️  google-drive MCP não integrado ainda")
        return []

    except Exception as e:
        print(f"⚠️  Erro ao listar carrosséis: {e}")
        return []


def download_drive_file(file_id: str, filename: str) -> Optional[bytes]:
    """
    Baixa arquivo do Drive pelo ID.
    Retorna bytes ou None se falha.
    Em cloud, usa google-drive MCP.
    """
    try:
        print(f"📥 Baixando {filename}...")
        # MCP: download_file_content(file_id) → bytes
        # Por enquanto, placeholder
        print("⚠️  google-drive MCP não integrado ainda")
        return None
    except Exception as e:
        print(f"❌ Erro ao baixar {filename}: {e}")
        return None


def update_metadata_drive(folder_id: str, metadata: Dict[str, Any]) -> bool:
    """
    Atualiza metadata.json no Drive após publicar.
    Em cloud, usa google-drive MCP upload.
    """
    try:
        print(f"📤 Atualizando metadata.json...")
        # MCP: update_file(metadata_file_id, json.dumps(metadata, ensure_ascii=False))
        print("⚠️  google-drive MCP não integrado ainda")
        return False
    except Exception as e:
        print(f"❌ Erro ao atualizar metadata: {e}")
        return False


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

    print(f"\n✓ IG Account ID: {INSTAGRAM_BUSINESS_ACCOUNT_ID}")

    # Passo 1: listar pastas em 02-carrossel
    print("\n📂 Etapa 1: Buscar próximo carrossel...")
    carousels = list_carousel_folders()

    if not carousels:
        print("ℹ️  Fila vazia ou MCP não disponível. Próxima tentativa amanhã.")
        sys.exit(0)

    # Passo 2: filtrar postado:false, ordenar por data_criacao
    print(f"\n📊 Etapa 2: Filtrar fila ({len(carousels)} carrosséis)...")
    next_carousel = None
    for carousel in carousels:
        # Em cloud, aqui lê metadata.json via MCP
        # Por enquanto, placeholder
        pass

    if not next_carousel:
        print("ℹ️  Todos carrosséis já postados!")
        sys.exit(0)

    print(f"✓ Próximo: {next_carousel.get('name', '?')}")

    # Passo 3: baixar slides do Drive
    print(f"\n📥 Etapa 3: Baixar slides...")
    slides = next_carousel.get("slides", [])
    for slide in slides:
        file_id = slide.get("drive_file_id")
        filename = slide.get("arquivo", f"slide_{slide.get('ordem')}")
        image_bytes = download_drive_file(file_id, filename)

        if not image_bytes:
            print(f"❌ Falha ao baixar slide {slide.get('ordem')}")
            sys.exit(1)

        # Passo 4: subir pro Supabase
        image_url = upload_to_supabase(image_bytes, filename)
        if not image_url:
            print(f"❌ Falha ao subir slide {slide.get('ordem')} pro Supabase")
            sys.exit(1)

        slide["image_url"] = image_url

    # Passo 5: publicar no Instagram
    print(f"\n📱 Etapa 5: Publicar no Instagram...")
    caption = next_carousel.get("legenda", "") + "\n\n" + " ".join(
        next_carousel.get("hashtags", [])
    )
    post_id = publish_carousel(slides, caption)

    if not post_id:
        print("❌ Falha ao publicar")
        sys.exit(1)

    # Passo 6: atualizar metadata.json
    print(f"\n💾 Etapa 6: Atualizar metadata...")
    next_carousel["postado"] = True
    next_carousel["postado_em"] = datetime.now().isoformat()
    next_carousel["post_id"] = post_id

    if not update_metadata_drive(next_carousel.get("folder_id"), next_carousel):
        print("⚠️  Aviso: post publicado mas metadata não atualizado")
        print(f"   Post ID: {post_id}")
        print(f"   Atualize manualmente metadata.json: postado=true, post_id={post_id}")
        sys.exit(1)

    print(f"\n✅ SUCESSO!")
    print(f"   Carousel: {next_carousel.get('name')}")
    print(f"   Post ID: {post_id}")
    print(f"   Link: https://instagram.com/p/{post_id}")


if __name__ == "__main__":
    main()
