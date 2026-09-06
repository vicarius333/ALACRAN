#!/usr/bin/env python3
"""ALACRAN - validacion estructural V1."""
import json
import sys
from pathlib import Path


def validate(path):
    with Path(path).open(encoding="utf-8") as f:
        data = json.load(f)
    findings = data.get("datos", [])
    refs = []
    errors = []
    for item in findings:
        r = item.get("referencia", {})
        key = (r.get("book_id"), r.get("chapter"), r.get("verse"))
        if key in refs:
            errors.append({"tipo": "REFERENCIA_DUPLICADA", "referencia": key})
        refs.append(key)
        if not r.get("book_id") or not r.get("book"):
            errors.append({"tipo": "REFERENCIA_INCOMPLETA", "referencia": key})
        if not isinstance(item.get("tokens"), list):
            errors.append({"tipo": "TOKENS_INVALIDOS", "referencia": key})
    return {
        "sistema": "ALACRAN",
        "version": "V1",
        "registros": len(findings),
        "referencias_unicas": len(set(refs)),
        "errores": errors,
        "estado": "VALIDO" if not errors else "NO_VALIDO"
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ALACRAN_VALIDATOR.py datos_extraidos.json")
        raise SystemExit(2)
    print(json.dumps(validate(sys.argv[1]), ensure_ascii=False, indent=2))
