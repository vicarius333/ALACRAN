#!/usr/bin/env python3
"""ALACRAN - Validación estructural de extracción XML."""
import json
import sys

EXPECTED = 31103
REQUIRED = {"book_id", "book", "chapter", "verse", "text", "source_id"}

def validate(path):
    count = 0
    missing = 0
    empty_text = 0
    duplicates = set()
    duplicate_count = 0

    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            rec = json.loads(line)
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
        duplicate_count == 0
    )
    result = {
        "estado": "VALIDACION_APROBADA" if ok else "VALIDACION_FALLIDA",
        "registros": count,
        "esperados": EXPECTED,
        "campos_requeridos_faltantes": missing,
        "textos_vacios": empty_text,
        "duplicados": duplicate_count
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ALACRAN_VALIDAR_EXTRACCION.py <DATOS_BIBLICOS_NORMALIZADOS.jsonl>")
        sys.exit(2)
    sys.exit(validate(sys.argv[1]))
