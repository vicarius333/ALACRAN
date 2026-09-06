#!/usr/bin/env python3
import json
import sys
from pathlib import Path

INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("BIBLIA/output/ALACRAN_COMPARACION_RESULTADO_V1.json")
AUDIT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("BIBLIA/output/ALACRAN_AUDITORIA_COMPARACION_V1.json")
OUTPUT = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("BIBLIA/output/ALACRAN_GRAFO_RESULTADO_V1.json")

REQUIRED = {
    "id_hallazgo", "referencia_origen", "relacion", "tipo_evidencia",
    "estado_verificacion", "escala_origen", "escalas_objetivo_comparables",
    "resultado"
}

errors = []

def load(path, label):
    if not path.exists():
        errors.append(f"ARCHIVO_NO_ENCONTRADO_{label}: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"JSON_INVALIDO_{label}: {exc}")
        return {}

comparison = load(INPUT, "COMPARACION")
audit = load(AUDIT, "AUDITORIA")

if comparison.get("id") != "ALACRAN_COMPARACION_RESULTADO_V1":
    errors.append("ID_COMPARACION_INVALIDO")
if comparison.get("etapa") != "08_COMPARACION":
    errors.append("ETAPA_COMPARACION_INVALIDA")
if comparison.get("estado") != "COMPARACION_APROBADA":
    errors.append("COMPARACION_NO_APROBADA")
if comparison.get("fractalidad_declarada") is not False:
    errors.append("FRACTALIDAD_COMPARACION_NO_FALSE")

if audit.get("id") != "ALACRAN_AUDITORIA_COMPARACION_V1":
    errors.append("ID_AUDITORIA_INVALIDO")
if audit.get("etapa") != "09_AUDITORIA":
    errors.append("ETAPA_AUDITORIA_INVALIDA")
if audit.get("estado") != "AUDITORIA_APROBADA":
    errors.append("AUDITORIA_NO_APROBADA")
if audit.get("salida") != "AUDITORIA_APROBADA":
    errors.append("SALIDA_AUDITORIA_INVALIDA")
if audit.get("fractalidad_declarada") is not False:
    errors.append("FRACTALIDAD_AUDITORIA_NO_FALSE")

comparaciones = comparison.get("comparaciones", [])
if not isinstance(comparaciones, list) or not comparaciones:
    errors.append("SIN_COMPARACIONES")
    comparaciones = []

nodes = []
edges = []
seen_nodes = set()
seen_edges = set()

def add_node(node_id, node_type, **extra):
    if node_id in seen_nodes:
        return
    seen_nodes.add(node_id)
    node = {"id": node_id, "tipo": node_type}
    node.update(extra)
    nodes.append(node)

def add_edge(edge_id, source, target, relation, evidence):
    if edge_id in seen_edges:
        errors.append(f"ARISTA_DUPLICADA:{edge_id}")
        return
    seen_edges.add(edge_id)
    edges.append({
        "id": edge_id,
        "origen": source,
        "destino": target,
        "relacion": relation,
        "evidencia": evidence
    })

for i, item in enumerate(comparaciones, 1):
    if not isinstance(item, dict):
        errors.append(f"COMPARACION_{i}_NO_OBJETO")
        continue
    missing = REQUIRED - set(item)
    if missing:
        errors.append(f"COMPARACION_{i}_CAMPOS_FALTANTES:{','.join(sorted(missing))}")
        continue
    cid = item["id_hallazgo"]
    if item["resultado"] != "CANDIDATO_SIN_DEMOSTRACION_MULTIESCALA":
        errors.append(f"RESULTADO_INVALIDO:{cid}")
        continue
    if item["tipo_evidencia"] == "HIPOTESIS":
        errors.append(f"HIPOTESIS_RECHAZADA:{cid}")
        continue
    if not isinstance(item["escalas_objetivo_comparables"], list) or not item["escalas_objetivo_comparables"]:
        errors.append(f"ESCALAS_OBJETIVO_INVALIDAS:{cid}")
        continue

    finding = f"HALLAZGO:{cid}"
    scale = f"ESCALA:{item['escala_origen']}"
    relation = f"RELACION:{item['relacion']}"
    reference = f"ORIGEN:{item['referencia_origen']}"

    add_node(finding, "HALLAZGO", id_hallazgo=cid,
             tipo_evidencia=item["tipo_evidencia"],
             estado_verificacion=item["estado_verificacion"],
             resultado=item["resultado"])
    add_node(scale, "ESCALA", valor=item["escala_origen"])
    add_node(relation, "RELACION", valor=item["relacion"])
    add_node(reference, "REFERENCIA_ORIGEN", valor=item["referencia_origen"])

    evidence = {
        "id_hallazgo": cid,
        "referencia_origen": item["referencia_origen"],
        "relacion": item["relacion"],
        "tipo_evidencia": item["tipo_evidencia"],
        "estado_verificacion": item["estado_verificacion"],
        "escala_origen": item["escala_origen"],
        "escalas_objetivo_comparables": item["escalas_objetivo_comparables"],
        "resultado": item["resultado"]
    }
    add_edge(f"{cid}:ESCALA", finding, scale, "TIENE_ESCALA_ORIGEN", evidence)
    add_edge(f"{cid}:RELACION", finding, relation, "EXPRESA_RELACION", evidence)
    add_edge(f"{cid}:ORIGEN", finding, reference, "TIENE_ORIGEN", evidence)

result = {
    "id": "ALACRAN_GRAFO_RESULTADO_V1",
    "etapa": "10_GRAFO",
    "entrada_comparacion": str(INPUT),
    "entrada_auditoria": str(AUDIT),
    "estado": "EJECUTADO" if not errors else "BLOQUEADO",
    "salida": "GRAFO_CONSTRUIDO" if not errors else "BLOQUEADO",
    "nodos": nodes,
    "aristas": edges,
    "errores": errors,
    "fractalidad_declarada": False,
    "regla": "El grafo solo materializa relaciones ya comparadas y auditadas; no crea inferencias, no eleva evidencia y no declara fractalidad."
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if not errors else 1)
