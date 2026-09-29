#!/usr/bin/env bash
# Instala as fontes da marca no runner (Inter, Manrope, Tempting) e valida.
# Tempting vem de: (1) arquivo em ./fonts/ (commitado), ou (2) secret
# TEMPTING_FONT_B64 (base64 do .ttf/.otf). Sem ela o job FALHA -- o padrao da
# casa e Inter 900 + Tempting, nao ha substituta silenciosa.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.local/share/fonts/aidealab"
mkdir -p "$DEST"

sudo apt-get install -y fonts-inter >/dev/null 2>&1 || true
GF="https://github.com/google/fonts/raw/main/ofl"
curl -fsSL --retry 3 -o "$DEST/Manrope.ttf" "$GF/manrope/Manrope%5Bwght%5D.ttf"
if ! fc-list | grep -qi "Inter"; then
  curl -fsSL --retry 3 -o "$DEST/Inter.ttf" "$GF/inter/Inter%5Bopsz%2Cwght%5D.ttf"
fi

shopt -s nullglob nocaseglob
tempting=("$HERE"/fonts/tempting*.ttf "$HERE"/fonts/tempting*.otf "$HERE"/fonts/tempting*.woff)
if [ ${#tempting[@]} -gt 0 ]; then
  cp "${tempting[@]}" "$DEST/"
elif [ -n "${TEMPTING_FONT_B64:-}" ]; then
  printf '%s' "$TEMPTING_FONT_B64" | base64 -d > "$DEST/Tempting.ttf"
else
  echo "::error::Fonte Tempting ausente: commite o arquivo em 'agente aidealab/automation/cloud/fonts/' ou crie o secret TEMPTING_FONT_B64 (base64 do .ttf/.otf)."
  exit 1
fi

fc-cache -f "$DEST" >/dev/null
for fam in Inter Manrope Tempting; do
  if ! fc-list | grep -qi "$fam"; then
    echo "::error::Fonte '$fam' nao foi encontrada apos a instalacao (fc-list)."
    exit 1
  fi
  echo "OK  $fam -> $(fc-list | grep -i "$fam" | head -1)"
done
