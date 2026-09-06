#!/usr/bin/env python3
import json
import sys
from pathlib import Path

INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("BIBLIA/output/ALACRAN_COMPARACION_RESULTADO_V1.json")
OUTPUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("BIBLIA/output/ALACRAN_AUDITORIA_COMPARACION_V1.json")

REQUIRED = {
    "id_hallazgo", "referencia_origen", "relacion", "tipo_evidencia",
    "estado_verificacion", "escala_origen", "escalas_objetivo_comparables",
    "resultado"
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
if data.get("estado") != "COMPARACION_APROBADA":
    errors.append("COMPARACION_NO_APROBADA")
if data.get("fractalidad_declarada") is not False:
    errors.append("FRACTALIDAD_NO_DECLARADA_FALSE")
if not isinstance(data.get("regla"), str) or not data.get("regla"):
    errors.append("REGLA_AUSENTE")

comparaciones = data.get("comparaciones", [])
if not isinstance(comparaciones, list) or not comparaciones:
    errors.append("SIN_COMPARACIONES")
    comparaciones = []

seen = set()
for i, item in enumerate(comparaciones, 1):
    if not isinstance(item, dict):
        errors.append(f"COMPARACION_{i}_NO_OBJETO")
        continue
    missing = REQUIRED - set(item)
    if missing:
        errors.append(f"COMPARACION_{i}_CAMPOS_FALTANTES:{','.join(sorted(missing))}")
        continue
    cid = item.get("id_hallazgo")
    if cid in seen:
        errors.append(f"DUPLICADO_ID_HALLAZGO:{cid}")
    seen.add(cid)
    if item.get("tipo_evidencia") == "HIPOTESIS":
        errors.append(f"HIPOTESIS_RECHAZADA:{cid}")
    if item.get("resultado") != "CANDIDATO_SIN_DEMOSTRACION_MULTIESCALA":
        errors.append(f"RESULTADO_INVALIDO:{cid}")
    if not isinstance(item.get("escalas_objetivo_comparables"), list) or not item.get("escalas_objetivo_comparables"):
        errors.append(f"ESCALAS_OBJETIVO_INVALIDAS:{cid}")

result = {
    "id": "ALACRAN_AUDITORIA_COMPARACION_V1",
    "etapa": "09_AUDITORIA",
    "entrada": str(INPUT),
    "estado": "AUDITORIA_APROBADA" if not errors else "AUDITORIA_FALLIDA",
    "salida": "AUDITORIA_APROBADA" if not errors else "BLOQUEADO",
    "comparaciones_auditadas": len(comparaciones),
    "errores": errors,
    "fractalidad_declarada": False,
    "regla": "La fractalidad solo puede declararse cuando la misma relacion estructural queda demostrada independientemente en al menos dos escalas."
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if not errors else 1)
