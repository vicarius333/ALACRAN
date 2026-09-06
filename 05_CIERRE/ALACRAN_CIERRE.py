#!/usr/bin/env python3
"""ALACRAN - Cierre formal de la extracción validada."""
import json
import sys
from datetime import datetime, timezone


def close(validation_path, output_path):
    with open(validation_path, "r", encoding="utf-8") as f:
        validation = json.load(f)

    approved = validation.get("estado") == "VALIDACION_APROBADA"
    cierre = {
        "id": "ALACRAN_CIERRE_EXTRACCION_V1",
        "estado": "CIERRE_APROBADO" if approved else "CIERRE_BLOQUEADO",
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "etapa": "05_CIERRE",
        "validacion": validation,
        "fuentes": [
            "BIBLIA/FUENTE_XML_MANIFIESTO.json",
            "BIBLIA/input/XML_MAPPING.json"
        ],
        "salida_validada": "BIBLIA/output/DATOS_BIBLICOS_NORMALIZADOS.jsonl",
        "regla": "No se interpreta el contenido en esta etapa; solo se registra el cierre del dato validado."
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cierre, f, ensure_ascii=False, indent=2)
    print(json.dumps(cierre, ensure_ascii=False, indent=2))
    return 0 if approved else 1

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python ALACRAN_CIERRE.py <validacion.json> <cierre.json>")
        sys.exit(2)
    sys.exit(close(sys.argv[1], sys.argv[2]))
