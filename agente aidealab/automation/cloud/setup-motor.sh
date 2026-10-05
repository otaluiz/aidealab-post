#!/usr/bin/env bash
# Prepara o runner (GitHub Actions) para o motor novo (motor/ = carrossel-engine) com o tema aidealab.
set -euo pipefail
cd "$(dirname "$0")/../../.."
python -m pip install -q -r "agente aidealab/automation/cloud/requirements.txt" scipy "rembg[cpu]"
python -m playwright install --with-deps chromium
# compor.py precisa dos cascades Haar do OpenCV 4 (o 5 não traz mais)
[ -d motor/.vendor_cv4/cv2 ] || python -m pip install -q --target motor/.vendor_cv4 opencv-python-headless==4.10.0.84
# modelos do rembg (o workflow guarda ~/.u2net e ~/.rembg em cache)
python -c "from rembg import new_session; new_session('u2net')"
# fontes do tema aidealab instaladas localmente (render não depende do Google Fonts carregar a tempo)
mkdir -p ~/.fonts && R=https://raw.githubusercontent.com/google/fonts/main
for f in "ofl/inter/Inter%5Bopsz,wght%5D.ttf" "ofl/manrope/Manrope%5Bwght%5D.ttf" "apache/yellowtail/Yellowtail-Regular.ttf" "ofl/firacode/FiraCode%5Bwght%5D.ttf"; do
  n="$(basename "$f")"; [ -f ~/.fonts/"$n" ] || curl -sSfL -o ~/.fonts/"$n" "$R/$f"
done
fc-cache -f
echo "setup ok"
