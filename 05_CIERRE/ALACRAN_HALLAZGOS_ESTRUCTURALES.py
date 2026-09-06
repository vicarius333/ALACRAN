#!/usr/bin/env python3
"""ALACRAN - 05_CIERRE: genera hallazgos puramente estructurales.

No interpreta el contenido textual. Solo registra relaciones observables
entre las unidades estructurales presentes en la extracción validada.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def generar(extracted_path, output_path):
    books = defaultdict(set)
    chapters = defaultdict(set)
    verses = 0
    source_ids = set()

    with open(extracted_path, encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            book_id = str(record["book_id"])
            chapter = str(record["chapter"])
            verse = str(record["verse"])
            books[book_id].add(chapter)
            chapters[(book_id, chapter)].add(verse)
            source_ids.add(record["source_id"])
            verses += 1

    findings = []

    findings.append({
        "id": "ALACRAN-H-EST-001",
        "tipo_evidencia": "RELACION",
        "escala": "BIBLIA",
        "ubicacion": "BIBLIA",
        "elementos": {"libros": len(books), "capitulos": len(chapters), "versiculos": verses},
        "relacion": "LIBRO_CONTIENE_CAPITULO",
        "frecuencia": len(chapters),
        "transformacion": "Cada capitulo queda asociado a un unico book_id en el registro extraido.",
        "ausencias_relevantes": [],
        "evidencia_fuente": sorted(source_ids),
        "estado_verificacion": "VERIFICADO"
    })

    findings.append({
        "id": "ALACRAN-H-EST-002",
        "tipo_evidencia": "RELACION",
        "escala": "BIBLIA",
        "ubicacion": "BIBLIA",
        "elementos": {"capitulos": len(chapters), "versiculos": verses},
        "relacion": "CAPITULO_CONTIENE_VERSO",
        "frecuencia": verses,
        "transformacion": "Cada versiculo queda asociado a un unico par (book_id, chapter) en el registro extraido.",
        "ausencias_relevantes": [],
        "evidencia_fuente": sorted(source_ids),
        "estado_verificacion": "VERIFICADO"
    })

    Path(output_path).write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in findings) + "\n",
        encoding="utf-8"
    )
    print(json.dumps({
        "estado": "HALLAZGOS_ESTRUCTURALES_GENERADOS",
        "hallazgos": len(findings),
        "registros": verses,
        "salida": output_path
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python ALACRAN_HALLAZGOS_ESTRUCTURALES.py <extraccion.jsonl> <hallazgos.jsonl>")
        sys.exit(2)
    generar(*sys.argv[1:])
