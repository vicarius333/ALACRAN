#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 03_EJECUCION/ALACRAN_DOWNLOAD_XML.py \
  BIBLIA/FUENTE_XML_MANIFIESTO.json \
  BIBLIA/input/HebrewBible.xml

python3 03_EJECUCION/ALACRAN_XML_INSPECTOR.py \
  BIBLIA/input/HebrewBible.xml \
  BIBLIA/input/XML_STRUCTURE_REPORT.json

echo "ALACRAN: descarga + verificacion SHA + inspeccion estructural completadas."
echo "Siguiente paso: validar el mapeo XML antes de extraer datos."
