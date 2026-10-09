"""Envia a campanha, os pontos de melhoria e os roteiros de Reels do repo para o Drive, como Google Docs.

Etapa do workflow entregar.yml. Mapeamento (sob Clientes/aidealab):
  clientes/aidealab/campanha/**/*.md   -> 05-Campanhas/  (subpastas preservadas, ex. semanas/)
  clientes/aidealab/estrategia/melhorias.md -> 05-Campanhas/
  clientes/aidealab/roteiro/**/*.md    -> 03-Roteiros/   (uma subpasta por semana, ex. 2026-W42/)
Cada .md vira um Google Docs com o nome do arquivo (sem .md). O sha256 do conteúdo fica em appProperties.sha:
só atualiza quando o arquivo mudou. Nunca apaga nada no Drive.
"""
import hashlib
import io
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from drive_helper import get_service  # noqa: E402
from googleapiclient.errors import HttpError  # noqa: E402
from googleapiclient.http import MediaIoBaseUpload  # noqa: E402
from upload_carrosseis import PASTA, achar, filhos  # noqa: E402

CLI = AQUI.parents[1] / "clientes" / "aidealab"
DOC = "application/vnd.google-apps.document"


def pasta(svc, pai, partes, cache):
    """Id da subpasta pai/partes..., criando o que faltar."""
    atual = pai
    for nome in partes:
        chave = (atual, nome)
        if chave not in cache:
            cache[chave] = filhos(svc, atual).get(nome) or svc.files().create(
                body={"name": nome, "mimeType": PASTA, "parents": [atual]}, fields="id").execute()["id"]
        atual = cache[chave]
    return atual


def docs_na_pasta(svc, pid):
    r = svc.files().list(q=f"'{pid}' in parents and trashed = false and mimeType = '{DOC}'",
                         fields="files(id,name,appProperties)", pageSize=1000).execute()
    return {f["name"]: f for f in r["files"]}


def enviar(svc, f, pid, existentes):
    texto = f.read_bytes(); sha = hashlib.sha256(texto).hexdigest(); nome = f.stem
    atual = existentes.get(nome)
    if atual and (atual.get("appProperties") or {}).get("sha") == sha:
        return None
    for tipo in ("text/markdown", "text/plain"):  # markdown vira Docs formatado; texto puro como reserva
        media = MediaIoBaseUpload(io.BytesIO(texto), mimetype=tipo, resumable=False)
        try:
            if atual:
                svc.files().update(fileId=atual["id"], body={"appProperties": {"sha": sha}}, media_body=media).execute()
                return "atualizado"
            svc.files().create(body={"name": nome, "mimeType": DOC, "parents": [pid], "appProperties": {"sha": sha}},
                               media_body=media, fields="id").execute()
            return "criado"
        except HttpError as e:
            if tipo == "text/plain":
                raise
            print(f"aviso: markdown recusado em {f.name} ({getattr(e, 'status_code', e.resp.status)}), enviando como texto")


def main():
    svc = get_service()
    raiz = achar(svc, "Clientes/aidealab")
    destinos = filhos(svc, raiz)
    grupos = [(CLI / "campanha", destinos["05-Campanhas"], sorted((CLI / "campanha").rglob("*.md"))),
              (CLI / "estrategia", destinos["05-Campanhas"], [CLI / "estrategia" / "melhorias.md"]),
              (CLI / "roteiro", destinos["03-Roteiros"], sorted((CLI / "roteiro").rglob("*.md")))]
    cache, mudou = {}, 0
    for base, pai, arquivos in grupos:
        for f in arquivos:
            if not f.exists():
                continue
            pid = pasta(svc, pai, f.relative_to(base).parts[:-1], cache)
            if pid not in cache:
                cache[pid] = docs_na_pasta(svc, pid)
            acao = enviar(svc, f, pid, cache[pid])
            if acao:
                mudou += 1
                print(f"{acao}: {f.relative_to(CLI)}")
    print(f"documentos enviados/atualizados: {mudou}")


if __name__ == "__main__":
    main()
