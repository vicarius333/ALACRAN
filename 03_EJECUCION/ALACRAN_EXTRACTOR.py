#!/usr/bin/env python3
"""ALACRAN - extractor estructural V1.

Extrae datos observables de un corpus JSON/JSONL sin interpretar su contenido.
No genera hipotesis.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

REQUIRED = {"book_id", "book", "chapter", "verse", "text"}
TOKEN_RE = re.compile(r"\S+", re.UNICODE)


def load_records(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open(encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("records"), list):
        return data["records"]
    raise ValueError("El JSON debe ser una lista de registros o contener 'records'.")


def normalize_text(text):
    return " ".join(str(text).split())


def extract(records):
    output = []
    seen_refs = set()
    errors = []
    for i, rec in enumerate(records):
        missing = REQUIRED - rec.keys()
        if missing:
            errors.append({"registro": i, "tipo": "CAMPOS_FALTANTES", "campos": sorted(missing)})
            continue
        ref = (rec["book_id"], int(rec["chapter"]), int(rec["verse"]))
        duplicate = ref in seen_refs
        seen_refs.add(ref)
        text = normalize_text(rec["text"])
        tokens = TOKEN_RE.findall(text)
        output.append({
            "referencia": {
                "book_id": rec["book_id"],
                "book": rec["book"],
                "chapter": int(rec["chapter"]),
                "verse": int(rec["verse"])
            },
            "source_id": rec.get("source_id"),
            "text_original": rec["text"],
            "text_normalizado": text,
            "tokens": tokens,
            "token_count": len(tokens),
            "duplicate_reference": duplicate
        })
    return output, errors


def main():
    if len(sys.argv) != 3:
        print("Uso: python ALACRAN_EXTRACTOR.py corpus.json salida.json")
        return 2
    records = load_records(Path(sys.argv[1]))
    data, errors = extract(records)
    result = {
        "sistema": "ALACRAN",
        "version": "V1",
        "principio": "EXTRACCION_SIN_INTERPRETACION",
        "registros_entrada": len(records),
        "registros_extraidos": len(data),
        "errores": errors,
        "datos": data
    }
    with Path(sys.argv[2]).open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(data)} registros extraidos; {len(errors)} errores.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
