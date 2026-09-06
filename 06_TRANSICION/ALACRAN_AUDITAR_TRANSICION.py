#!/usr/bin/env python3
"""ALACRAN - Auditoria de 06_TRANSICION V1.

Verifica preservacion de identidad, origen, relacion y estado.
No declara fractalidad.
"""
import json
import sys
from pathlib import Path

REQUIRED = {
    "id_hallazgo", "referencia_origen", "relacion", "tipo_evidencia",
    "estado_verificacion", "escala_origen", "elementos", "frecuencia",
    "transformacion", "ausencias_relevantes", "evidencia_fuente", "estado"
}


def main(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = []
    candidates = data.get("candidatos", [])

    if data.get("id") != "ALACRAN_TRANSICION_RESULTADO_V1":
        errors.append("ID_RESULTADO_INVALIDO")
    if data.get("salida") != "CANDIDATO_COMPARABLE":
        errors.append("SALIDA_NO_COMPARABLE")
    if not candidates:
        errors.append("SIN_CANDIDATOS")

    ids = set()
    for i, c in enumerate(candidates, 1):
        missing = sorted(REQUIRED - c.keys())
        if missing:
            errors.append({"candidato": i, "error": "CAMPOS_FALTANTES", "campos": missing})
            continue
        if c["id_hallazgo"] in ids:
            errors.append({"candidato": i, "error": "ID_DUPLICADO", "id": c["id_hallazgo"]})
        ids.add(c["id_hallazgo"])
        if c["estado"] != "CANDIDATO_COMPARABLE":
            errors.append({"candidato": i, "error": "ESTADO_CANDIDATO_INVALIDO"})
        if c["tipo_evidencia"] == "HIPOTESIS":
            errors.append({"candidato": i, "error": "HIPOTESIS_NO_PERMITIDA"})
        if not isinstance(c["ausencias_relevantes"], list):
            errors.append({"candidato": i, "error": "AUSENCIAS_NO_LISTA"})
        if not c["evidencia_fuente"]:
            errors.append({"candidato": i, "error": "EVIDENCIA_FUENTE_VACIA"})

    result = {
        "id": "ALACRAN_AUDITORIA_TRANSICION_V1",
        "etapa": "06_TRANSICION",
        "estado": "AUDITORIA_APROBADA" if not errors else "AUDITORIA_FALLIDA",
        "candidatos_auditados": len(candidates),
        "errores": errors,
        "fractalidad_declarada": False,
        "regla": "La transicion conserva la relacion; la fractalidad requiere demostracion independiente en al menos dos escalas."
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ALACRAN_AUDITAR_TRANSICION.py <resultado.json>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
