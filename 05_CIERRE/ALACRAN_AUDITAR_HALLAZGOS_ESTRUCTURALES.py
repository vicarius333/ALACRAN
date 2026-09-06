#!/usr/bin/env python3
"""ALACRAN - Auditoría formal de hallazgos estructurales V1.

Valida estructura y restricciones epistemicas. No interpreta semántica
ni declara fractalidad.
"""
import json
import sys
from pathlib import Path

REQUIRED = {
    "id", "tipo_evidencia", "escala", "ubicacion", "elementos",
    "relacion", "frecuencia", "transformacion", "ausencias_relevantes",
    "evidencia_fuente", "estado_verificacion"
}
ALLOWED_TYPES = {"HECHO", "DATO", "RELACION", "PATRON_OBSERVADO", "INFERENCIA", "HIPOTESIS", "NO_VERIFICADO"}
ALLOWED_SCALES = {"BIBLIA", "BLOQUE", "LIBRO", "CAPITULO", "UNIDAD", "ELEMENTO", "PALABRA", "RAIZ", "LETRA_OPERADOR"}
EXPECTED_IDS = {"ALACRAN-H-EST-001", "ALACRAN-H-EST-002"}
EXPECTED_RELATIONS = {"LIBRO_CONTIENE_CAPITULO", "CAPITULO_CONTIENE_VERSO"}


def auditar(path):
    errors = []
    findings = []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"linea {n}: JSON invalido: {exc}")
                continue
            findings.append(obj)
            missing = REQUIRED - set(obj)
            if missing:
                errors.append(f"{obj.get('id','SIN_ID')}: campos faltantes {sorted(missing)}")
            if obj.get("tipo_evidencia") not in ALLOWED_TYPES:
                errors.append(f"{obj.get('id','SIN_ID')}: tipo_evidencia no permitido")
            if obj.get("escala") not in ALLOWED_SCALES:
                errors.append(f"{obj.get('id','SIN_ID')}: escala no permitida")
            if obj.get("estado_verificacion") != "VERIFICADO":
                errors.append(f"{obj.get('id','SIN_ID')}: estado no VERIFICADO")
            if obj.get("tipo_evidencia") == "HIPOTESIS":
                errors.append(f"{obj.get('id','SIN_ID')}: hipótesis no permitida en esta fase")
            if obj.get("relacion") not in EXPECTED_RELATIONS:
                errors.append(f"{obj.get('id','SIN_ID')}: relación no autorizada en V1")
            if not isinstance(obj.get("ausencias_relevantes"), list):
                errors.append(f"{obj.get('id','SIN_ID')}: ausencias_relevantes debe ser lista")
            if not isinstance(obj.get("evidencia_fuente"), list) or not obj.get("evidencia_fuente"):
                errors.append(f"{obj.get('id','SIN_ID')}: evidencia_fuente vacía o inválida")

    ids = [x.get("id") for x in findings]
    if len(findings) != 2:
        errors.append(f"cantidad de hallazgos inesperada: {len(findings)}; esperados 2")
    if len(ids) != len(set(ids)):
        errors.append("IDs duplicados")
    if set(ids) != EXPECTED_IDS:
        errors.append(f"IDs inesperados: {sorted(set(ids) ^ EXPECTED_IDS)}")
    relations = [x.get("relacion") for x in findings]
    if len(relations) != len(set(relations)):
        errors.append("relaciones duplicadas")
    if set(relations) != EXPECTED_RELATIONS:
        errors.append(f"relaciones inesperadas: {sorted(set(relations) ^ EXPECTED_RELATIONS)}")

    result = {
        "estado": "AUDITORIA_APROBADA" if not errors else "AUDITORIA_FALLIDA",
        "hallazgos": len(findings),
        "errores": errors,
        "fractalidad_declarada": False,
        "regla": "Una relación no se considera fractal hasta demostrarse en al menos dos escalas."
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ALACRAN_AUDITAR_HALLAZGOS_ESTRUCTURALES.py <hallazgos.jsonl>")
        sys.exit(2)
    sys.exit(auditar(sys.argv[1]))
