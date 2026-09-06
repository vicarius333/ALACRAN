#!/usr/bin/env python3
"""ALACRAN - 07_RETORNO: retorno controlado a escalas comparables.

Solo reubica candidatos ya transferidos. No crea relaciones ni declara fractalidad.
"""
import json
import sys
from pathlib import Path

ALLOWED_TARGETS = {"LIBRO", "CAPITULO", "UNIDAD", "ELEMENTO"}


def main(input_path, output_path):
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    candidates = data.get("candidatos", [])
    errors = []
    returned = []

    if data.get("salida") != "CANDIDATO_COMPARABLE":
        errors.append("TRANSICION_NO_COMPARABLE")

    for c in candidates:
        if c.get("estado") != "CANDIDATO_COMPARABLE":
            errors.append({"id_hallazgo": c.get("id_hallazgo"), "error": "ESTADO_INVALIDO"})
            continue
        returned.append({
            "id_hallazgo": c["id_hallazgo"],
            "referencia_origen": c["referencia_origen"],
            "relacion": c["relacion"],
            "tipo_evidencia": c["tipo_evidencia"],
            "estado_verificacion": c["estado_verificacion"],
            "escala_origen": c["escala_origen"],
            "escalas_objetivo_comparables": sorted(ALLOWED_TARGETS),
            "elementos": c["elementos"],
            "frecuencia": c["frecuencia"],
            "transformacion": c["transformacion"],
            "ausencias_relevantes": c["ausencias_relevantes"],
            "evidencia_fuente": c["evidencia_fuente"],
            "estado": "CANDIDATO_RETORNO"
        })

    result = {
        "id": "ALACRAN_RETORNO_RESULTADO_V1",
        "etapa": "07_RETORNO",
        "estado": "EJECUTADO" if returned and not errors else "BLOQUEADO",
        "salida": "CANDIDATO_RETORNO" if returned and not errors else "BLOQUEADO",
        "candidatos_retorno": returned,
        "errores": errors,
        "regla": "El retorno conserva identidad, origen, relacion, evidencia y estado; solo prepara comparacion entre escalas.",
        "fractalidad_declarada": False
    }
    Path(output_path).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python ALACRAN_RETORNO.py <transicion.json> <resultado.json>")
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
