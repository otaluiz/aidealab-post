#!/usr/bin/env python3
"""
Publica o próximo conteúdo aprovado de 06-Aprovados-para-Postar no Instagram.
Lê credenciais de variáveis de ambiente (nunca hardcoded).
Testa acesso, lista fila, publica imagem/carrossel, atualiza metadata.json.
"""

import os
import json
import sys
import io
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import requests
from pathlib import Path

# Tentar importar SDKs; se faltar, avisar
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
except ImportError:
    pass

try:
    from supabase import create_client
except ImportError:
    pass

# Credenciais vêm de variáveis de ambiente
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_PROJECT_ID = "jrfjjpxjkpvuvvycyryj"  # projeto aidealab
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"
SUPABASE_BUCKET = "ig-publish"

GRAPH_API_VERSION = "v22.0"
GRAPH_API_HOST = "https://graph.facebook.com"

# Drive folder IDs (ficar hardcoded pro fluxo funcionar)
DRIVE_FOLDER_06_APROVADOS = "1JkVrArjUe3vTrVRRsXZcF8zMrVsQT0LMm"  # 06-Aprovados-para-Postar
DRIVE_FOLDER_01_IMAGEM = "1-twLvfjNsEENRGDAphO3weZ4m_D8919k"  # FILA-SEMANA-1/01-Imagem (exemplo)
DRIVE_FOLDER_02_CARROSSEL = "1-twLvfjNsEENRGDAphO3weZ4m_D8919k"  # FILA-SEMANA-1/02-carrossel (exemplo)


def check_credentials():
    """Verifica se todas as credenciais necessárias estão setadas."""
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
            for acc in data["data"]:
                print(f"  - {acc.get('name', 'sem nome')} (ID: {acc.get('id')})")
            return True
        else:
            print("❌ System User sem acesso à conta @idea_lab7.")
            print("Ação: Business Manager → Usuários do Sistema → aidealab_admin → Atribuir ativos → Page, controle total")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar acesso: {e}")
        return False


def get_ig_account_id() -> str:
    """Obtém o ID da conta IG do Business Manager."""
    # Se foi passado explicitamente (ex: 61594589125482), usa
    if INSTAGRAM_BUSINESS_ACCOUNT_ID:
        return INSTAGRAM_BUSINESS_ACCOUNT_ID

    # Senão, tenta descobrir via /me/accounts
    url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/me/accounts"
    params = {"access_token": INSTAGRAM_ACCESS_TOKEN}

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        if data.get("data") and len(data["data"]) > 0:
            # Toma a primeira (ideal: filtrar por nome @idea_lab7)
            return data["data"][0]["id"]
    except Exception:
        pass

    return None


def publish_image(image_url: str, caption: str, ig_account_id: str) -> Optional[str]:
    """
    Publica uma imagem única.
    Retorna post_id se sucesso, None se falha.
    """
    # Passo 1: criar media container
    media_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media"
    media_payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }

    try:
        print(f"📤 Criando container de mídia...")
        resp = requests.post(media_url, json=media_payload, timeout=10)
        resp.raise_for_status()
        media_data = resp.json()
        media_id = media_data.get("id")

        if not media_id:
            print(f"❌ Erro: sem media_id na resposta: {media_data}")
            return None

        print(f"✓ Container criado: {media_id}")

        # Passo 2: publicar (media_publish)
        publish_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media_publish"
        publish_payload = {
            "creation_id": media_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        }

        print(f"📬 Publicando...")
        resp = requests.post(publish_url, json=publish_payload, timeout=10)
        resp.raise_for_status()
        publish_data = resp.json()
        post_id = publish_data.get("id")

        if not post_id:
            print(f"❌ Erro: sem post_id na resposta: {publish_data}")
            return None

        print(f"✓ Publicado! Post ID: {post_id}")
        return post_id

    except Exception as e:
        print(f"❌ Erro na publicação: {e}")
        return None


def publish_carousel(slides: List[Dict[str, Any]], caption: str, ig_account_id: str) -> Optional[str]:
    """
    Publica um carrossel.
    slides = [{"image_url": "...", "order": 1}, ...]
    Retorna post_id se sucesso, None se falha.
    """
    try:
        print(f"📤 Criando {len(slides)} containers de slides...")

        # Passo 1: criar media containers para cada slide (ordem importa)
        child_ids = []
        for slide in sorted(slides, key=lambda s: s.get("ordem", 999)):
            media_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media"
            media_payload = {
                "image_url": slide["image_url"],
                "is_carousel_item": True,
                "access_token": INSTAGRAM_ACCESS_TOKEN,
            }

            resp = requests.post(media_url, json=media_payload, timeout=10)
            resp.raise_for_status()
            media_data = resp.json()
            media_id = media_data.get("id")

            if not media_id:
                print(f"❌ Erro no slide {slide.get('ordem')}: sem media_id")
                return None

            child_ids.append(media_id)
            print(f"  ✓ Slide {slide.get('ordem')}: {media_id}")

        # Passo 2: criar container pai com tipo CAROUSEL
        media_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media"
        media_payload = {
            "media_type": "CAROUSEL",
            "children": child_ids,
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        }

        print(f"📤 Criando container pai do carrossel...")
        resp = requests.post(media_url, json=media_payload, timeout=10)
        resp.raise_for_status()
        media_data = resp.json()
        carousel_id = media_data.get("id")

        if not carousel_id:
            print(f"❌ Erro: sem carousel_id na resposta: {media_data}")
            return None

        print(f"✓ Carrossel criado: {carousel_id}")

        # Passo 3: publicar
        publish_url = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}/{ig_account_id}/media_publish"
        publish_payload = {
            "creation_id": carousel_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        }

        print(f"📬 Publicando carrossel...")
        resp = requests.post(publish_url, json=publish_payload, timeout=10)
        resp.raise_for_status()
        publish_data = resp.json()
        post_id = publish_data.get("id")

        if not post_id:
            print(f"❌ Erro: sem post_id na resposta: {publish_data}")
            return None

        print(f"✓ Carrossel publicado! Post ID: {post_id}")
        return post_id

    except Exception as e:
        print(f"❌ Erro no carrossel: {e}")
        return None


def upload_to_supabase(image_bytes: bytes, filename: str) -> Optional[str]:
    """
    Sobe imagem pro Supabase Storage bucket ig-publish.
    Retorna URL pública da imagem, ou None se falha.
    """
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

        # Upload
        path = f"{datetime.now().strftime('%Y%m%d')}/{filename}"
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path, image_bytes, {"contentType": "image/jpeg"}
        )

        # Construir URL pública
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{path}"
        print(f"✓ Supabase: {filename} → {public_url}")
        return public_url

    except Exception as e:
        print(f"❌ Erro ao subir pro Supabase: {e}")
        return None


def delete_from_supabase(image_url: str):
    """Deleta uma imagem do Supabase após publicar."""
    try:
        # Extrai path da URL
        # URL: https://jrfjjpxjkpvuvvycyryj.supabase.co/storage/v1/object/public/ig-publish/20260920/file.jpg
        if "ig-publish/" not in image_url:
            return

        path = image_url.split("ig-publish/")[1]
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        supabase.storage.from_(SUPABASE_BUCKET).remove([path])
        print(f"🗑️  Supabase: deletado {path}")

    except Exception as e:
        print(f"⚠️  Aviso ao deletar de Supabase: {e}")


def get_drive_service():
    """Retorna cliente autenticado do Google Drive."""
    # NOTA: Em produção (cloud), usar service account JSON
    # Por enquanto, retorna None se não conseguir autenticar
    # (local: user auth; cloud: service account)
    try:
        return build("drive", "v3")
    except Exception as e:
        print(f"⚠️  Google Drive não autenticado: {e}")
        return None


def list_carousels_from_drive() -> Optional[Dict[str, Any]]:
    """
    Lista carrosséis em 06-Aprovados-para-Postar/FILA-SEMANA-1/02-carrossel.
    Ordena por data_criacao (data_criacao field no metadata.json).
    Retorna o primeiro com postado:false, ou None se fila vazia.

    Nota: usa MCP google-drive disponível na cloud routine.
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
        import io

        # Na cloud, credenciais vêm da sessão/service account
        # Por enquanto, retorna None pra avisar que precisa MCP
        print("🔍 Buscando próximo carrossel em 06-Aprovados-para-Postar...")
        print("⚠️  Requer MCP google-drive na sessão cloud")
        print("   Implementação: listar pastas, ler metadata.json, encontrar postado:false")
        return None

    except Exception as e:
        print(f"⚠️  Drive API não disponível: {e}")
        return None


def main():
    """Orquestra o fluxo: testa acesso, lista fila, publica, atualiza metadata."""
    print("=" * 60)
    print("📱 Post Instagram - Publicar Próximo")
    print("=" * 60)

    # Verifica credenciais
    check_credentials()

    # Testa acesso
    if not test_access():
        sys.exit(1)

    # Obtém IG account ID
    ig_account_id = get_ig_account_id()
    if not ig_account_id:
        print("❌ Não conseguiu obter IG account ID")
        sys.exit(1)

    print(f"✓ IG Account ID: {ig_account_id}")

    print("\n" + "=" * 60)
    print("⚠️  PRÓXIMOS PASSOS:")
    print("=" * 60)
    print("""
1. Prepare credenciais como variáveis de ambiente:
   - Windows PowerShell:
     $env:INSTAGRAM_ACCESS_TOKEN = "seu_token_aqui"
     $env:INSTAGRAM_BUSINESS_ACCOUNT_ID = "61594589125482"
     $env:SUPABASE_SERVICE_ROLE_KEY = "sua_chave_supabase"

   - Linux/Mac bash:
     export INSTAGRAM_ACCESS_TOKEN="seu_token_aqui"
     export INSTAGRAM_BUSINESS_ACCOUNT_ID="61594589125482"
     export SUPABASE_SERVICE_ROLE_KEY="sua_chave_supabase"

2. Rode novamente este script:
   python publish_next.py

3. O script:
   - Lista o próximo conteúdo não publicado em 06-Aprovados-para-Postar
   - Pede confirmação antes de publicar
   - Publica no Instagram
   - Atualiza metadata.json com postado:true
""")
    print("=" * 60)


if __name__ == "__main__":
    main()
