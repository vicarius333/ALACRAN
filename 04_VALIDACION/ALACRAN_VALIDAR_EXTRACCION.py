#!/usr/bin/env python3
"""ALACRAN - Validacion estructural de extraccion XML."""
import json
import sys
from pathlib import Path

EXPECTED = 31103
REQUIRED = {"book_id", "book", "chapter", "verse", "text", "source_id"}
DEFAULT_OUTPUT = Path("BIBLIA/output/ALACRAN_VALIDACION_EXTRACCION_V1.json")


def validate(path, output_path):
    count = 0
    missing = 0
    empty_text = 0
    duplicates = set()
    duplicate_count = 0
    json_errors = 0

    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                json_errors += 1
                continue
            count += 1
            if not REQUIRED.issubset(rec):
                missing += 1
            if not rec.get("text", "").strip():
                empty_text += 1
            key = (rec.get("book_id"), rec.get("chapter"), rec.get("verse"))
            if key in duplicates:
                duplicate_count += 1
            duplicates.add(key)

    ok = (
        count == EXPECTED and
        missing == 0 and
        empty_text == 0 and
        duplicate_count == 0 and
        json_errors == 0
    )
    result = {
        "id": "ALACRAN_VALIDACION_EXTRACCION_V1",
        "etapa": "04_VALIDACION",
        "estado": "VALIDACION_APROBADA" if ok else "VALIDACION_FALLIDA",
        "registros": count,
        "esperados": EXPECTED,
        "campos_requeridos_faltantes": missing,
        "textos_vacios": empty_text,
        "duplicados": duplicate_count,
        "errores_json": json_errors
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) == 2:
        input_path = Path(sys.argv[1])
        output_path = DEFAULT_OUTPUT
    elif len(sys.argv) == 3:
        input_path = Path(sys.argv[1])
        output_path = Path(sys.argv[2])
    else:
        print("Uso: python ALACRAN_VALIDAR_EXTRACCION.py <DATOS_BIBLICOS_NORMALIZADOS.jsonl> [SALIDA.json]")
        sys.exit(2)
    sys.exit(validate(input_path, output_path))
