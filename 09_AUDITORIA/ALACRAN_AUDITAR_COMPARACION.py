#!/usr/bin/env python3
import json
import sys
from pathlib import Path

INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("BIBLIA/output/ALACRAN_COMPARACION_RESULTADO_V1.json")
OUTPUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("BIBLIA/output/ALACRAN_AUDITORIA_COMPARACION_V1.json")

REQUIRED = {
    "id_hallazgo", "referencia_origen", "relacion", "tipo_evidencia",
    "estado_verificacion", "escala_origen", "elementos", "frecuencia",
    "transformacion", "ausencias_relevantes", "evidencia_fuente", "estado"
}

errors = []

if not INPUT.exists():
    errors.append(f"ARCHIVO_NO_ENCONTRADO: {INPUT}")
    data = {}
else:
    try:
        data = json.loads(INPUT.read_text(encoding="utf-8"))
    except Exception as exc:
        data = {}
        errors.append(f"JSON_INVALIDO: {exc}")

if data.get("id") != "ALACRAN_COMPARACION_RESULTADO_V1":
    errors.append("ID_RESULTADO_INVALIDO")
if data.get("etapa") != "08_COMPARACION":
    errors.append("ETAPA_INVALIDA")
if data.get("salida") != "CANDIDATO_SIN_DEMOSTRACION_MULTIESCALA":
    errors.append("SALIDA_INVALIDA_O_FRACTALIDAD_INDEBIDA")
if data.get("fractalidad_declarada") is not False:
    errors.append("FRACTALIDAD_NO_DECLARADA_FALSE")

candidates = data.get("candidatos_comparacion", [])
if not isinstance(candidates, list) or not candidates:
    errors.append("SIN_CANDIDATOS_COMPARABLES")
    candidates = []

seen = set()
for i, candidate in enumerate(candidates, 1):
    if not isinstance(candidate, dict):
        errors.append(f"CANDIDATO_{i}_NO_OBJETO")
        continue
    missing = REQUIRED - set(candidate)
    if missing:
        errors.append(f"CANDIDATO_{i}_CAMPOS_FALTANTES:{','.join(sorted(missing))}")
    cid = candidate.get("id_hallazgo")
    if cid in seen:
        errors.append(f"DUPLICADO_ID_HALLAZGO:{cid}")
    if cid is not None:
        seen.add(cid)
    if candidate.get("tipo_evidencia") == "HIPOTESIS":
        errors.append(f"HIPOTESIS_RECHAZADA:{cid}")
    if candidate.get("estado") != "CANDIDATO_SIN_DEMOSTRACION_MULTIESCALA":
        errors.append(f"ESTADO_CANDIDATO_INVALIDO:{cid}")
    if not isinstance(candidate.get("ausencias_relevantes"), list):
        errors.append(f"AUSENCIAS_NO_LISTA:{cid}")
    if not candidate.get("evidencia_fuente"):
        errors.append(f"SIN_EVIDENCIA_FUENTE:{cid}")

result = {
    "id": "ALACRAN_AUDITORIA_COMPARACION_V1",
    "etapa": "09_AUDITORIA",
    "entrada": str(INPUT),
    "estado": "AUDITORIA_APROBADA" if not errors else "AUDITORIA_FALLIDA",
    "salida": "AUDITORIA_APROBADA" if not errors else "BLOQUEADO",
    "candidatos_auditados": len(candidates),
    "errores": errors,
    "fractalidad_declarada": False,
    "regla": "La fractalidad solo puede declararse cuando la misma relacion estructural queda demostrada independientemente en al menos dos escalas.",
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if not errors else 1)
