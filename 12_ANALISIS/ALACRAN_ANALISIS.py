#!/usr/bin/env python3
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("BIBLIA/output/ALACRAN_GRAFO_RESULTADO_V1.json")
AUDIT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("BIBLIA/output/ALACRAN_AUDITORIA_GRAFO_V1.json")
OUTPUT = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("BIBLIA/output/ALACRAN_ANALISIS_RESULTADO_V1.json")

errors = []

def load(path, label):
    if not path.exists():
        errors.append(f"ARCHIVO_NO_ENCONTRADO_{label}:{path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"JSON_INVALIDO_{label}:{exc}")
        return {}

graph = load(INPUT, "GRAFO")
audit = load(AUDIT, "AUDITORIA")

checks_graph = {
    "id": "ALACRAN_GRAFO_RESULTADO_V1",
    "etapa": "10_GRAFO",
    "estado": "EJECUTADO",
    "salida": "GRAFO_CONSTRUIDO"
}
for key, expected in checks_graph.items():
    if graph.get(key) != expected:
        errors.append(f"GRAFO_{key.upper()}_INVALIDO")
if graph.get("fractalidad_declarada") is not False:
    errors.append("GRAFO_FRACTALIDAD_NO_FALSE")

checks_audit = {
    "id": "ALACRAN_AUDITORIA_GRAFO_V1",
    "etapa": "11_AUDITORIA_GRAFO",
    "estado": "AUDITORIA_APROBADA",
    "salida": "AUDITORIA_APROBADA"
}
for key, expected in checks_audit.items():
    if audit.get(key) != expected:
        errors.append(f"AUDITORIA_{key.upper()}_INVALIDO")
if audit.get("fractalidad_declarada") is not False:
    errors.append("AUDITORIA_FRACTALIDAD_NO_FALSE")

nodes = graph.get("nodos", [])
edges = graph.get("aristas", [])
if not isinstance(nodes, list) or not nodes:
    errors.append("SIN_NODOS")
    nodes = []
if not isinstance(edges, list) or not edges:
    errors.append("SIN_ARISTAS")
    edges = []

node_ids = {n.get("id") for n in nodes if isinstance(n, dict)}
node_types = Counter(n.get("tipo") for n in nodes if isinstance(n, dict))
edge_relations = Counter(e.get("relacion") for e in edges if isinstance(e, dict))
scales = Counter()
findings = set()
degrees = Counter()

for n in nodes:
    if not isinstance(n, dict):
        errors.append("NODO_NO_OBJETO")
        continue
    if not n.get("id") or not n.get("tipo"):
        errors.append("NODO_CAMPOS_INVALIDOS")

for e in edges:
    if not isinstance(e, dict):
        errors.append("ARISTA_NO_OBJETO")
        continue
    required = {"id", "origen", "destino", "relacion", "evidencia"}
    missing = required - set(e)
    if missing:
        errors.append(f"ARISTA_CAMPOS_FALTANTES:{','.join(sorted(missing))}")
        continue
    if e["origen"] not in node_ids or e["destino"] not in node_ids:
        errors.append(f"ARISTA_REFERENCIA_NODO_INEXISTENTE:{e['id']}")
    degrees[e["origen"]] += 1
    degrees[e["destino"]] += 1
    ev = e.get("evidencia", {})
    if not isinstance(ev, dict):
        errors.append(f"EVIDENCIA_INVALIDA:{e['id']}")
        continue
    if ev.get("tipo_evidencia") == "HIPOTESIS":
        errors.append(f"HIPOTESIS_RECHAZADA:{e['id']}")
    if ev.get("resultado") != "CANDIDATO_SIN_DEMOSTRACION_MULTIESCALA":
        errors.append(f"RESULTADO_NO_DESCRIPTIVO:{e['id']}")
    scale = ev.get("escala_origen")
    if scale:
        scales[scale] += 1
    if ev.get("id_hallazgo"):
        findings.add(ev["id_hallazgo"])

# Componentes conexos: solo propiedad topologica, sin interpretacion semantica.
adj = defaultdict(set)
for e in edges:
    if isinstance(e, dict) and e.get("origen") in node_ids and e.get("destino") in node_ids:
        a, b = e["origen"], e["destino"]
        adj[a].add(b); adj[b].add(a)
visited = set()
components = 0
for nid in node_ids:
    if nid in visited:
        continue
    components += 1
    stack = [nid]
    visited.add(nid)
    while stack:
        cur = stack.pop()
        for nxt in adj[cur]:
            if nxt not in visited:
                visited.add(nxt)
                stack.append(nxt)

result = {
    "id": "ALACRAN_ANALISIS_RESULTADO_V1",
    "etapa": "12_ANALISIS",
    "entrada_grafo": str(INPUT),
    "entrada_auditoria": str(AUDIT),
    "estado": "ANALISIS_APROBADO" if not errors else "ANALISIS_BLOQUEADO",
    "salida": "RESULTADOS_DESCRIPTIVOS" if not errors else "BLOQUEADO",
    "tipo_analisis": "DESCRIPTIVO_ESTRUCTURAL",
    "metricas": {
        "numero_nodos": len(nodes),
        "numero_aristas": len(edges),
        "numero_hallazgos": len(findings),
        "tipos_nodo": dict(sorted(node_types.items(), key=lambda x: str(x[0]))),
        "relaciones_por_tipo": dict(sorted(edge_relations.items())),
        "escalas_por_hallazgo": dict(sorted(scales.items())),
        "componentes_conectados": components,
        "grado_por_nodo": dict(sorted(degrees.items()))
    },
    "observaciones": [
        "Las metricas describen exclusivamente la estructura presente en el grafo auditado.",
        "No se generan inferencias causales, semanticas ni hipotesis.",
        "La presencia de una relacion en una sola escala no demuestra fractalidad.",
        "La fractalidad permanece sin declarar hasta evidencia independiente en al menos dos escalas."
    ],
    "errores": errors,
    "fractalidad_declarada": False,
    "regla": "12_ANALISIS solo cuantifica y describe propiedades estructurales ya auditadas; no crea relaciones, inferencias ni hipotesis."
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if not errors else 1)
