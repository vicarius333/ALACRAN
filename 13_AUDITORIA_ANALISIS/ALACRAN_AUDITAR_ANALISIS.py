#!/usr/bin/env python3
import json
import sys
from pathlib import Path

INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("BIBLIA/output/ALACRAN_ANALISIS_RESULTADO_V1.json")
OUTPUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("BIBLIA/output/ALACRAN_AUDITORIA_ANALISIS_V1.json")

errors = []

def load(path):
    if not path.exists():
        errors.append(f"ARCHIVO_NO_ENCONTRADO:{path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"JSON_INVALIDO:{exc}")
        return {}

analysis = load(INPUT)

checks = {
    "id": "ALACRAN_ANALISIS_RESULTADO_V1",
    "etapa": "12_ANALISIS",
    "estado": "ANALISIS_APROBADO",
    "salida": "RESULTADOS_DESCRIPTIVOS",
    "tipo_analisis": "DESCRIPTIVO_ESTRUCTURAL"
}
for key, expected in checks.items():
    if analysis.get(key) != expected:
        errors.append(f"{key.upper()}_INVALIDO")

if analysis.get("fractalidad_declarada") is not False:
    errors.append("FRACTALIDAD_NO_FALSE")

metrics = analysis.get("metricas")
if not isinstance(metrics, dict):
    errors.append("METRICAS_INVALIDAS")
else:
    for key in ("numero_nodos", "numero_aristas", "numero_hallazgos", "tipos_nodo", "relaciones_por_tipo", "escalas_por_hallazgo", "componentes_conectados", "grado_por_nodo"):
        if key not in metrics:
            errors.append(f"METRICA_AUSENTE:{key}")
    for key in ("numero_nodos", "numero_aristas", "numero_hallazgos", "componentes_conectados"):
        if key in metrics and (not isinstance(metrics[key], int) or metrics[key] < 0):
            errors.append(f"METRICA_NO_ENTERO_NO_NEGATIVO:{key}")

observations = analysis.get("observaciones")
if not isinstance(observations, list) or not observations:
    errors.append("OBSERVACIONES_AUSENTES")
else:
    joined = " ".join(str(x) for x in observations).lower()
    if "no se generan inferencias" not in joined:
        errors.append("REGLA_ANTI_INFERENCIA_AUSENTE")
    if "fractalidad" not in joined:
        errors.append("REGLA_FRACTALIDAD_AUSENTE")

if analysis.get("errores") != []:
    errors.append("ANALISIS_CONTIENE_ERRORES")

rule = analysis.get("regla")
if not isinstance(rule, str) or not rule.strip():
    errors.append("REGLA_AUSENTE")

result = {
    "id": "ALACRAN_AUDITORIA_ANALISIS_V1",
    "etapa": "13_AUDITORIA_ANALISIS",
    "entrada": str(INPUT),
    "estado": "AUDITORIA_APROBADA" if not errors else "AUDITORIA_FALLIDA",
    "salida": "AUDITORIA_APROBADA" if not errors else "BLOQUEADO",
    "analisis_auditado": analysis.get("id"),
    "metricas_auditadas": list(metrics.keys()) if isinstance(metrics, dict) else [],
    "errores": errors,
    "fractalidad_declarada": False,
    "regla": "13_AUDITORIA_ANALISIS verifica trazabilidad, consistencia y límites epistemológicos del análisis descriptivo; no crea nuevas relaciones, inferencias ni hipótesis."
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if not errors else 1)
