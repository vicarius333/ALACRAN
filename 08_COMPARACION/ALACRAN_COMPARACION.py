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
    entrada, salida = map(Path, sys.argv[1:])
    resultado = {
        "id": "ALACRAN_COMPARACION_RESULTADO_V1",
        "etapa": "08_COMPARACION",
        "estado": "COMPARACION_BLOQUEADA",
        "comparaciones": [], "errores": [],
        "fractalidad_declarada": False,
        "regla": "La fractalidad solo puede demostrarse cuando la misma relacion aparece independientemente en al menos dos escalas."
    }
    if not entrada.exists():
        resultado["errores"].append("Entrada de retorno inexistente")
    else:
        try:
            data = json.loads(entrada.read_text(encoding="utf-8"))
        except Exception as exc:
            data = {}
            resultado["errores"].append(f"JSON de retorno invalido: {exc}")
        if data.get("salida") != "CANDIDATO_RETORNO":
            resultado["errores"].append("La salida de retorno no es CANDIDATO_RETORNO")
        candidatos = data.get("candidatos_retorno", [])
        if not isinstance(candidatos, list) or not candidatos:
            resultado["errores"].append("No existen candidatos de retorno comparables")
        else:
            vistos = set()
            for c in candidatos:
                faltantes = sorted(REQUIRED - set(c)) if isinstance(c, dict) else list(REQUIRED)
                if faltantes:
                    resultado["errores"].append(f"Campos faltantes en {c.get('id_hallazgo') if isinstance(c, dict) else 'NO_OBJETO'}: {faltantes}")
                    continue
                cid = c["id_hallazgo"]
                if cid in vistos:
                    resultado["errores"].append(f"ID duplicado: {cid}")
                    continue
                vistos.add(cid)
                if c["tipo_evidencia"] == "HIPOTESIS":
                    resultado["errores"].append(f"Hipotesis prohibida: {cid}")
                    continue
                if c["estado"] != "CANDIDATO_RETORNO":
                    resultado["errores"].append(f"Estado invalido: {cid}")
                    continue
                resultado["comparaciones"].append({
                    "id_hallazgo": cid, "relacion": c["relacion"],
                    "escala_origen": c["escala_origen"],
                    "escalas_objetivo_comparables": c.get("escalas_objetivo_comparables", []),
                    "referencia_origen": c["referencia_origen"],
                    "tipo_evidencia": c["tipo_evidencia"],
                    "estado_verificacion": c["estado_verificacion"],
                    "resultado": "CANDIDATO_SIN_DEMOSTRACION_MULTIESCALA"
                })
    if resultado["comparaciones"] and not resultado["errores"]:
        resultado["estado"] = "COMPARACION_APROBADA"
    salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if resultado["estado"] == "COMPARACION_APROBADA" else 1

if __name__ == "__main__":
    sys.exit(main())
