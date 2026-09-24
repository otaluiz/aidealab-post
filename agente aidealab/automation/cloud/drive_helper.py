#!/usr/bin/env python3
"""
Helper de Google Drive para a rotina de automação em nuvem (GitHub Actions).

Por que este script existe, e não o MCP do Google-Drive: o MCP usado nas
sessões interativas do Claude devolve o conteúdo binário como base64 dentro
do resultado da ferramenta -- isso significa que o LLM "lê" e "escreve" cada
byte como texto, e no tokenizer desta stack isso custa perto de 1 token por
caractere de base64 (medido em produção: 254.000 caracteres -> 242.567
tokens). Uma imagem de 300-700KB vira uma chamada de meio milhão de tokens.
Além disso o MCP do Google-Drive usado em claude.ai é um conector OAuth da
própria conta logada -- não existe um jeito portátil de levar essa sessão
pra dentro de um runner do GitHub Actions.

Este script contorna os dois problemas: fala direto com a Google Drive API
v3 usando `google-api-python-client`, sobe/baixa arquivo por CAMINHO no
disco (nunca por texto/base64 em memória do agente) e usa um refresh_token
OAuth de "installed app" gerado uma vez com `get_drive_refresh_token.py`
(ver README.md desta pasta) -- não uma Service Account, porque Service
Account não tem cota própria de armazenamento numa conta Gmail pessoal
(erro `storageQuotaExceeded`).

Uso (CLI, chamado via Bash pelo agente Claude dentro do prompt da rotina):

    python drive_helper.py find-folder --name "04-Carrosseis" --parent-id <id>
    python drive_helper.py list --parent-id <id> [--folders-only]
    python drive_helper.py download --file-id <id> --out <caminho-local>
    python drive_helper.py upload --parent-id <id> --file <caminho-local> [--title <nome>]
    python drive_helper.py mkdir --parent-id <id> --title <nome>
    python drive_helper.py move --file-id <id> --new-parent-id <id>
    python drive_helper.py read-text --file-id <id>   # p/ ler metadata.json como texto

Credenciais via variáveis de ambiente (secrets do GitHub Actions):
    GOOGLE_DRIVE_CLIENT_ID
    GOOGLE_DRIVE_CLIENT_SECRET
    GOOGLE_DRIVE_REFRESH_TOKEN
"""
import argparse
import json
import os
import sys

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_MIME = "application/vnd.google-apps.folder"


def get_service():
    client_id = os.environ.get("GOOGLE_DRIVE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_DRIVE_CLIENT_SECRET")
    refresh_token = os.environ.get("GOOGLE_DRIVE_REFRESH_TOKEN")
    missing = [n for n, v in [
        ("GOOGLE_DRIVE_CLIENT_ID", client_id),
        ("GOOGLE_DRIVE_CLIENT_SECRET", client_secret),
        ("GOOGLE_DRIVE_REFRESH_TOKEN", refresh_token),
    ] if not v]
    if missing:
        print(f"ERRO: variaveis de ambiente faltando: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def cmd_find_folder(svc, args):
    query = f"mimeType = '{FOLDER_MIME}' and name = '{args.name}'"
    if args.parent_id:
        query += f" and '{args.parent_id}' in parents"
    query += " and trashed = false"
    resp = svc.files().list(q=query, fields="files(id,name)", pageSize=10).execute()
    print(json.dumps(resp.get("files", []), ensure_ascii=False))


def cmd_list(svc, args):
    query = f"'{args.parent_id}' in parents and trashed = false"
    if args.folders_only:
        query += f" and mimeType = '{FOLDER_MIME}'"
    files = []
    page_token = None
    while True:
        resp = svc.files().list(
            q=query, fields="nextPageToken, files(id,name,mimeType,size,modifiedTime)",
            pageSize=200, pageToken=page_token,
        ).execute()
        files.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    print(json.dumps(files, ensure_ascii=False))


def cmd_download(svc, args):
    request = svc.files().get_media(fileId=args.file_id)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    print(json.dumps({"saved": args.out}))


def cmd_read_text(svc, args):
    request = svc.files().get_media(fileId=args.file_id)
    import io
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    sys.stdout.write(buf.getvalue().decode("utf-8-sig"))


def cmd_upload(svc, args):
    if not os.path.isfile(args.file):
        print(f"ERRO: arquivo local nao encontrado: {args.file}", file=sys.stderr)
        sys.exit(1)
    title = args.title or os.path.basename(args.file)
    media = MediaFileUpload(args.file, resumable=True)
    metadata = {"name": title, "parents": [args.parent_id]}
    f = svc.files().create(body=metadata, media_body=media, fields="id,name,webViewLink").execute()
    print(json.dumps(f, ensure_ascii=False))


def cmd_mkdir(svc, args):
    metadata = {"name": args.title, "mimeType": FOLDER_MIME, "parents": [args.parent_id]}
    f = svc.files().create(body=metadata, fields="id,name").execute()
    print(json.dumps(f, ensure_ascii=False))


def cmd_move(svc, args):
    f = svc.files().get(fileId=args.file_id, fields="parents").execute()
    prev_parents = ",".join(f.get("parents", []))
    updated = svc.files().update(
        fileId=args.file_id, addParents=args.new_parent_id,
        removeParents=prev_parents, fields="id,parents",
    ).execute()
    print(json.dumps(updated, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("find-folder")
    sp.add_argument("--name", required=True)
    sp.add_argument("--parent-id", default=None)
    sp.set_defaults(func=cmd_find_folder)

    sp = sub.add_parser("list")
    sp.add_argument("--parent-id", required=True)
    sp.add_argument("--folders-only", action="store_true")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("download")
    sp.add_argument("--file-id", required=True)
    sp.add_argument("--out", required=True)
    sp.set_defaults(func=cmd_download)

    sp = sub.add_parser("read-text")
    sp.add_argument("--file-id", required=True)
    sp.set_defaults(func=cmd_read_text)

    sp = sub.add_parser("upload")
    sp.add_argument("--parent-id", required=True)
    sp.add_argument("--file", required=True)
    sp.add_argument("--title", default=None)
    sp.set_defaults(func=cmd_upload)

    sp = sub.add_parser("mkdir")
    sp.add_argument("--parent-id", required=True)
    sp.add_argument("--title", required=True)
    sp.set_defaults(func=cmd_mkdir)

    sp = sub.add_parser("move")
    sp.add_argument("--file-id", required=True)
    sp.add_argument("--new-parent-id", required=True)
    sp.set_defaults(func=cmd_move)

    args = p.parse_args()
    svc = get_service()
    args.func(svc, args)


if __name__ == "__main__":
    main()
