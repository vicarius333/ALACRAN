#!/usr/bin/env python3
"""ALACRAN - 05_CIERRE: cierre formal del dato extraido y validado."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_RECORDS = 31103
VALIDATION_STATE = "VALIDACION_APROBADA"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def close(validation_path, extracted_path, mapping_path, manifest_path, output_path):
    validation = json.loads(Path(validation_path).read_text(encoding="utf-8"))

    checks = {
        "estado_validacion": validation.get("estado") == VALIDATION_STATE,
        "registros": validation.get("registros") == EXPECTED_RECORDS,
        "campos_requeridos_faltantes": validation.get("campos_requeridos_faltantes") == 0,
        "textos_vacios": validation.get("textos_vacios") == 0,
        "duplicados": validation.get("duplicados") == 0,
        "salida_extraida_existe": Path(extracted_path).is_file(),
        "mapping_existe": Path(mapping_path).is_file(),
        "manifiesto_existe": Path(manifest_path).is_file(),
    }

    approved = all(checks.values())

    cierre = {
        "id": "ALACRAN_CIERRE_EXTRACCION_V1",
        "etapa": "05_CIERRE",
        "estado": "CIERRE_APROBADO" if approved else "CIERRE_BLOQUEADO",
        "estado_verificacion": "VERIFICADO" if approved else "PENDIENTE",
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "validacion_origen": validation,
        "proveniencia": {
            "manifiesto_fuente": manifest_path,
            "mapping": mapping_path,
            "dato_extraido": extracted_path,
        },
        "sha256": {
            "dato_extraido": sha256_file(extracted_path) if Path(extracted_path).is_file() else None,
            "mapping": sha256_file(mapping_path) if Path(mapping_path).is_file() else None,
            "manifiesto": sha256_file(manifest_path) if Path(manifest_path).is_file() else None,
        },
        "regla_cierre": "05_CIERRE no interpreta el contenido; solo certifica que el dato extraido satisface la validacion estructural y conserva su proveniencia.",
        "prohibiciones": [
            "No inferir significado semantico.",
            "No formular hipotesis.",
            "No alterar el dato extraido.",
            "No ocultar fallos o ausencias de validacion.",
        ],
        "salida": "CANDIDATO_TRANSICION" if approved else "BLOQUEADO",
    }

    Path(output_path).write_text(
        json.dumps(cierre, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(cierre, ensure_ascii=False, indent=2))
    return 0 if approved else 1


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(
            "Uso: python ALACRAN_CIERRE.py "
            "<validacion.json> <extraccion.jsonl> <mapping.json> "
            "<manifiesto.json> <cierre.json>"
        )
        sys.exit(2)

    sys.exit(close(*sys.argv[1:]))
