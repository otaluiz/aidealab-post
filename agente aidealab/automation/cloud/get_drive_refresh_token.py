#!/usr/bin/env python3
"""
Rode ISSO UMA VEZ, no seu computador local (não no GitHub Actions), pra gerar
o refresh_token que a automação em nuvem vai usar pra sempre (até você
revogar o acesso na conta Google).

Pré-requisito (ver README.md desta pasta pro passo a passo com prints):
1. Crie um projeto no Google Cloud Console, ative a "Google Drive API".
2. Crie uma credencial OAuth Client ID do tipo "Desktop app".
3. Baixe o JSON dessa credencial e aponte CLIENT_SECRETS_FILE pra ele abaixo,
   ou exporte GOOGLE_DRIVE_CLIENT_ID / GOOGLE_DRIVE_CLIENT_SECRET no ambiente.

Rodando `python get_drive_refresh_token.py`, uma aba do navegador abre pra
você logar com a conta aidealabbr@gmail.com e autorizar. No fim, o script
imprime o `refresh_token` -- copie e cole como o secret
`GOOGLE_DRIVE_REFRESH_TOKEN` no GitHub (Settings > Secrets and variables >
Actions) do repositório.
"""
import json
import os
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]
CLIENT_SECRETS_FILE = os.environ.get("GOOGLE_DRIVE_CLIENT_SECRETS_FILE", "client_secret.json")


def main():
    client_id = os.environ.get("GOOGLE_DRIVE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_DRIVE_CLIENT_SECRET")

    if os.path.isfile(CLIENT_SECRETS_FILE):
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    elif client_id and client_secret:
        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    else:
        print(
            "ERRO: forneça o JSON da credencial OAuth (client_secret.json na pasta atual,\n"
            "ou defina GOOGLE_DRIVE_CLIENT_SECRETS_FILE) OU as variáveis\n"
            "GOOGLE_DRIVE_CLIENT_ID e GOOGLE_DRIVE_CLIENT_SECRET.",
            file=sys.stderr,
        )
        sys.exit(1)

    # access_type=offline + prompt=consent garante que o Google devolva um
    # refresh_token mesmo se essa conta já tiver autorizado o app antes.
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    print("\n=== Sucesso ===")
    print(f"GOOGLE_DRIVE_CLIENT_ID={creds.client_id}")
    print(f"GOOGLE_DRIVE_CLIENT_SECRET={creds.client_secret}")
    print(f"GOOGLE_DRIVE_REFRESH_TOKEN={creds.refresh_token}")
    print(
        "\nCopie os 3 valores acima como Secrets do repositório no GitHub\n"
        "(Settings > Secrets and variables > Actions > New repository secret)."
    )

    with open("drive_token_output.json", "w") as f:
        json.dump({
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "refresh_token": creds.refresh_token,
        }, f, indent=2)
    print("\n(também salvo em drive_token_output.json -- NÃO comite esse arquivo)")


if __name__ == "__main__":
    main()
