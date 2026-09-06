#!/usr/bin/env python3
import json
import sys
from pathlib import Path

INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("BIBLIA/output/ALACRAN_GRAFO_RESULTADO_V1.json")
OUTPUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("BIBLIA/output/ALACRAN_AUDITORIA_GRAFO_V1.json")

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

data = load(INPUT)

checks = {
    "id": "ALACRAN_GRAFO_RESULTADO_V1",
    "etapa": "10_GRAFO",
    "estado": "EJECUTADO",
    "salida": "GRAFO_CONSTRUIDO"
}
for key, expected in checks.items():
    if data.get(key) != expected:
        errors.append(f"{key.upper()}_INVALIDO")
if data.get("fractalidad_declarada") is not False:
    errors.append("FRACTALIDAD_NO_FALSE")
if not isinstance(data.get("regla"), str) or not data.get("regla"):
    errors.append("REGLA_AUSENTE")

nodes = data.get("nodos", [])
edges = data.get("aristas", [])
if not isinstance(nodes, list) or not nodes:
    errors.append("SIN_NODOS")
    nodes = []
if not isinstance(edges, list) or not edges:
    errors.append("SIN_ARISTAS")
    edges = []

node_ids = set()
for i, node in enumerate(nodes, 1):
    if not isinstance(node, dict):
        errors.append(f"NODO_{i}_NO_OBJETO")
        continue
    if not node.get("id") or not node.get("tipo"):
        errors.append(f"NODO_{i}_CAMPOS_INVALIDOS")
    nid = node.get("id")
    if nid in node_ids:
        errors.append(f"NODO_DUPLICADO:{nid}")
    node_ids.add(nid)

edge_ids = set()
for i, edge in enumerate(edges, 1):
    if not isinstance(edge, dict):
        errors.append(f"ARISTA_{i}_NO_OBJETO")
        continue
    required = {"id", "origen", "destino", "relacion", "evidencia"}
    missing = required - set(edge)
    if missing:
        errors.append(f"ARISTA_{i}_CAMPOS_FALTANTES:{','.join(sorted(missing))}")
        continue
    eid = edge["id"]
    if eid in edge_ids:
        errors.append(f"ARISTA_DUPLICADA:{eid}")
    edge_ids.add(eid)
    if edge["origen"] not in node_ids or edge["destino"] not in node_ids:
        errors.append(f"ARISTA_REFERENCIA_NODO_INEXISTENTE:{eid}")
    ev = edge["evidencia"]
    if not isinstance(ev, dict):
        errors.append(f"EVIDENCIA_INVALIDA:{eid}")
        continue
    if ev.get("resultado") != "CANDIDATO_SIN_DEMOSTRACION_MULTIESCALA":
        errors.append(f"RESULTADO_EVIDENCIA_INVALIDO:{eid}")
    if ev.get("tipo_evidencia") == "HIPOTESIS":
        errors.append(f"HIPOTESIS_RECHAZADA:{eid}")

result = {
    "id": "ALACRAN_AUDITORIA_GRAFO_V1",
    "etapa": "11_AUDITORIA_GRAFO",
    "entrada": str(INPUT),
    "estado": "AUDITORIA_APROBADA" if not errors else "AUDITORIA_FALLIDA",
    "salida": "AUDITORIA_APROBADA" if not errors else "BLOQUEADO",
    "nodos_auditados": len(nodes),
    "aristas_auditadas": len(edges),
    "errores": errors,
    "fractalidad_declarada": False,
    "regla": "La auditoria verifica integridad referencial y fidelidad del grafo respecto de relaciones ya comparadas; no permite inferencias nuevas ni declaracion de fractalidad."
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if not errors else 1)
