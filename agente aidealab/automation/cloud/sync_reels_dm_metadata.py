#!/usr/bin/env python3
"""Atualiza apenas metadata.json de Reels aprovados nas duas filas do Google Drive.

Conserta a antiga configuração dm.link, que continha URLs de PDFs apagados.
A URL do PDF permanece SOMENTE no catálogo privado public.ig_dm_catalog
(Supabase, service_role). O webhook oficial verifica que a pessoa segue o
Instagram e consulta esse catálogo para distribuir o PDF.

Nunca altera vídeos, legendas, datas, status ou posts já publicados.
O conjunto de 13 Reels deve ser especificado por iscas/reels-2026-11-map.json.
"""
from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

QUEUE_FOLDERS = {
    "aidealab": "1u8FlKUuMT9hKfXz4rcj7kFRyioGC8TB1",  # 06/FILA
    "otalogia": "13GZEPJrWJaf9rWB4RFQXf5Hh0wRp27D6",  # 06 root
}
MIME_FOLDER = "application/vnd.google-apps.folder"
MANIFEST = json.loads(Path("iscas/reels-2026-11-map.json").read_text(encoding="utf-8"))
POSTS = MANIFEST["reels"]

def drive():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_DRIVE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_DRIVE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_DRIVE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds, cache_discovery=False)

def children(svc, parent):
    result, token = [], None
    while True:
        rsp = svc.files().list(
            q=f"'{parent}' in parents and trashed = false",
            fields="nextPageToken, files(id,name,mimeType)",
            pageSize=1000,
            pageToken=token,
        ).execute()
        result.extend(rsp.get("files", []))
        token = rsp.get("nextPageToken")
        if not token:
            return result

def read_meta(svc, file_id):
    raw = svc.files().get_media(fileId=file_id).execute()
    return json.loads(raw.decode("utf-8-sig"))

def save_meta(svc, file_id, obj):
    raw = (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    upload = MediaIoBaseUpload(io.BytesIO(raw), mimetype="application/json")
    svc.files().update(fileId=file_id, media_body=upload, fields="id").execute()

def main(apply):
    svc = drive()
    count = 0
    skipped = 0
    errors = []
    for brand, parent in QUEUE_FOLDERS.items():
        folder_list = {x["name"]: x for x in children(svc, parent) if x.get("mimeType") == MIME_FOLDER}
        for post in POSTS:
            # Prefix in each Drive folder is 2026-11-09, Reel ID in metadata
            rid = post["reel_id"]
            prefix = "reel-"
            if not rid.startswith(prefix):
                raise RuntimeError(f"Invalid reel id: {rid}")
            folder_name = "2026-11-09-" + rid[len(prefix):]
            directory = folder_list.get(folder_name)
            if directory is None:
                errors.append(f"{brand}/{folder_name}: pasta não localizada")
                continue
            file_list = {x["name"]: x for x in children(svc, directory["id"])}
            item = file_list.get("metadata.json")
            if not item:
                errors.append(f"{brand}/{folder_name}: sem metadata.json")
                continue
            data = read_meta(svc, item["id"])
            # Don't modify any publication which is already posted.
            if data.get("postado") is True or data.get("postado_em") or data.get("post_id"):
                skipped += 1
                print(f"SKIP published {brand}/{folder_name}")
                continue
            if data.get("carousel_id") != rid or data.get("tipo") != "reel":
                errors.append(f"{brand}/{folder_name}: id/tipo inesperados")
                continue
            dm = data.get("dm") or {}
            if not isinstance(dm, dict):
                errors.append(f"{brand}/{folder_name}: dm inválido")
                continue
            word = str(post["palavra"]).upper()
            if str(dm.get("palavra", "")).upper() != word:
                errors.append(f"{brand}/{folder_name}: palavra divergente {dm.get('palavra')} != {word}")
                continue
            # Never expose the public Drive link in metadata. The secure
            # catalog has the approved URL and validates Instagram follower.
            old_link = dm.pop("link", None)
            dm["catalogo"] = {
                "provedor": "supabase/ig_dm_catalog",
                "perfil": brand,
                "palavra": word,
                "categoria": post["categoria"],
            }
            dm["material_pdf"] = post["pdf"]
            dm["entrega"] = "apenas_se_seguidor_confirmado_pela_meta"
            data["dm"] = dm
            if apply:
                save_meta(svc, item["id"], data)
            count += 1
            print(f"{'UPDATED' if apply else 'DRY RUN'} {brand}/{folder_name} -> {word} "
                  f"(stale link {'removed' if old_link else 'already absent'})")
    print(f"SUMMARY modified_or_validated={count} published_skipped={skipped} errors={len(errors)}")
    if errors:
        raise RuntimeError("Inconsistências na fila: " + "; ".join(errors))
    # Expected 26 Reels across both brands.
    if count + skipped != len(POSTS) * len(QUEUE_FOLDERS):
        raise RuntimeError(f"Expected {len(POSTS) * len(QUEUE_FOLDERS)} posts, got {count + skipped}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="persist metadata updates")
    args = ap.parse_args()
    main(apply=args.apply)
