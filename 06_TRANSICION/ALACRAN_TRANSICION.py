#!/usr/bin/env python3
"""ALACRAN - 06_TRANSICION: transferencia controlada entre escalas.

No crea relaciones ni hipotesis. Si no existe un hallazgo relacional validado,
produce un bloqueo explicito en lugar de fabricar un CANDIDATO_COMPARABLE.
"""

import json
import sys
from pathlib import Path

REQUIRED_FINDING_FIELDS = {
    "id",
    "tipo_evidencia",
    "escala",
    "ubicacion",
    "elementos",
    "relacion",
    "frecuencia",
    "transformacion",
    "ausencias_relevantes",
    "evidencia_fuente",
    "estado_verificacion",
}
ALLOWED_SCALES = {
    "BIBLIA", "BLOQUE", "LIBRO", "CAPITULO", "UNIDAD",
    "ELEMENTO", "PALABRA", "RAIZ", "LETRA_OPERADOR"
}
ALLOWED_TYPES = {
    "HECHO", "DATO", "RELACION", "PATRON_OBSERVADO",
    "INFERENCIA", "HIPOTESIS", "NO_VERIFICADO"
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def transition(closure_path, findings_path, output_path):
    closure = load_json(closure_path)
    findings_file = Path(findings_path)

    result = {
        "id": "ALACRAN_TRANSICION_RESULTADO_V1",
        "etapa": "06_TRANSICION",
        "entrada_cierre": closure_path,
        "estado_cierre": closure.get("estado"),
        "regla": "Una relacion solo puede transferirse conservando identidad, origen, tipo de evidencia y estado de verificacion.",
        "prohibiciones": [
            "CAMBIAR_IDENTIDAD_DE_LA_RELACION",
            "OCULTAR_AUSENCIAS",
            "ELEVAR_INFERENCIA_A_HECHO"
        ],
    }

    if closure.get("estado") != "CIERRE_APROBADO":
        result.update({
            "estado": "BLOQUEADO",
            "salida": "BLOQUEADO",
            "motivo": "El 05_CIERRE no esta aprobado."
        })
        Path(output_path).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if not findings_file.is_file():
        result.update({
            "estado": "BLOQUEADO",
            "salida": "BLOQUEADO",
            "motivo": "No existe un registro de hallazgos para transferir; no se fabrica una relacion."
        })
        Path(output_path).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    candidates = []
    errors = []
    for line_no, line in enumerate(findings_file.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            finding = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append({"linea": line_no, "error": f"JSON invalido: {exc}"})
            continue

        missing = sorted(REQUIRED_FINDING_FIELDS - finding.keys())
        if missing:
            errors.append({"linea": line_no, "error": "campos_faltantes", "campos": missing})
            continue
        if finding["escala"] not in ALLOWED_SCALES:
            errors.append({"linea": line_no, "error": "escala_no_permitida", "escala": finding["escala"]})
            continue
        if finding["tipo_evidencia"] not in ALLOWED_TYPES:
            errors.append({"linea": line_no, "error": "tipo_evidencia_no_permitido", "tipo": finding["tipo_evidencia"]})
            continue

        candidates.append({
            "id_hallazgo": finding["id"],
            "referencia_origen": finding["ubicacion"],
            "relacion": finding["relacion"],
            "tipo_evidencia": finding["tipo_evidencia"],
            "estado_verificacion": finding["estado_verificacion"],
            "escala_origen": finding["escala"],
            "elementos": finding["elementos"],
            "frecuencia": finding["frecuencia"],
            "transformacion": finding["transformacion"],
            "ausencias_relevantes": finding["ausencias_relevantes"],
            "evidencia_fuente": finding["evidencia_fuente"],
            "estado": "CANDIDATO_COMPARABLE"
        })

    result.update({
        "estado": "EJECUTADO" if candidates and not errors else "BLOQUEADO",
        "salida": "CANDIDATO_COMPARABLE" if candidates and not errors else "BLOQUEADO",
        "candidatos": candidates,
        "errores": errors,
        "regla_fractal": "No se declara fractalidad en esta etapa; requiere la misma relacion demostrada en al menos dos escalas."
    })

    Path(output_path).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python ALACRAN_TRANSICION.py <cierre.json> <hallazgos.jsonl> <resultado.json>")
        sys.exit(2)
    sys.exit(transition(*sys.argv[1:]))
