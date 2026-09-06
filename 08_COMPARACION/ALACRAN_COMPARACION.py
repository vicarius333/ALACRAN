#!/usr/bin/env python3
import json
import sys
from pathlib import Path

REQUIRED = {
    "id_hallazgo", "referencia_origen", "relacion", "tipo_evidencia",
    "estado_verificacion", "escala_origen", "elementos", "frecuencia",
    "transformacion", "ausencias_relevantes", "evidencia_fuente", "estado"
}


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Uso: python ALACRAN_COMPARACION.py <RETORNO.json> <SALIDA.json>")

    entrada = Path(sys.argv[1])
    salida = Path(sys.argv[2])
    resultado = {
        "id": "ALACRAN_COMPARACION_RESULTADO_V1",
        "etapa": "08_COMPARACION",
        "estado": "COMPARACION_BLOQUEADA",
        "comparaciones": [],
        "errores": [],
        "fractalidad_declarada": False,
        "regla": "Una relacion solo puede considerarse fractal si la misma relacion queda demostrada independientemente en al menos dos escalas."
    }

    if not entrada.exists():
        resultado["errores"].append("Entrada de retorno inexistente")
        salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
        raise SystemExit(1)

    try:
        data = json.loads(entrada.read_text(encoding="utf-8"))
    except Exception as exc:
        resultado["errores"].append(f"JSON de retorno invalido: {exc}")
        salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
        raise SystemExit(1)

    if data.get("salida") != "CANDIDATO_COMPARABLE":
        resultado["errores"].append("La salida de retorno no es CANDIDATO_COMPARABLE")

    candidatos = data.get("candidatos", [])
    if not isinstance(candidatos, list) or not candidatos:
        resultado["errores"].append("No existen candidatos comparables")
    else:
        vistos = set()
        for c in candidatos:
            if not isinstance(c, dict):
                resultado["errores"].append("Candidato no es objeto JSON")
                continue
            faltantes = sorted(REQUIRED - set(c))
            if faltantes:
                resultado["errores"].append(f"Campos faltantes en {c.get('id_hallazgo')}: {faltantes}")
                continue
            cid = c["id_hallazgo"]
            if cid in vistos:
                resultado["errores"].append(f"ID duplicado: {cid}")
                continue
            vistos.add(cid)
            if c["tipo_evidencia"] == "HIPOTESIS":
                resultado["errores"].append(f"Hipotesis prohibida: {cid}")
                continue
            resultado["comparaciones"].append({
                "id_hallazgo": cid,
                "relacion": c["relacion"],
                "escala_origen": c["escala_origen"],
                "referencia_origen": c["referencia_origen"],
                "tipo_evidencia": c["tipo_evidencia"],
                "estado_verificacion": c["estado_verificacion"],
                "resultado": "CANDIDATO_SIN_DEMOSTRACION_MULTIESCALA"
            })

    if resultado["comparaciones"] and not resultado["errores"]:
        resultado["estado"] = "COMPARACION_APROBADA"

    salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if resultado["estado"] == "COMPARACION_APROBADA" else 1


if __name__ == "__main__":
    main()
