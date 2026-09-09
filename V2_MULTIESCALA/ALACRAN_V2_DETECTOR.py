#!/usr/bin/env python3
"""ALACRAN V2: deteccion multiescala conservadora.

Solo mide relaciones estructurales observables en el corpus normalizado.
No asigna significado semantico ni declara fractalidad.
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

SCALES = ("S1_palabra", "S2_verso", "S3_bloque", "S4_capitulo", "S5_bloque_mayor", "S6_libro")


def toks(text):
    return re.findall(r"[^\W_]+(?:['’-][^\W_]+)*", text or "", flags=re.UNICODE)


def load(path):
    rows=[]
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip(): rows.append(json.loads(line))
    return rows


def detect(rows, block_size=5, major_size=5):
    by_book=defaultdict(list)
    for r in rows:
        by_book[str(r["book_id"])].append(r)
    for k in by_book: by_book[k].sort(key=lambda r:(int(r["chapter"]), int(r["verse"])))

    detections=[]
    def add(scale, unit, rel, a, b, pos):
        detections.append({"id_relacion": f"R{len(detections)+1:08d}", "escala":scale,
            "unidad":unit,"elemento_a":a,"operacion":rel,"elemento_b":b,
            "posicion":pos,"frecuencia":1,"distancia":1,"direccion":"A→B",
            "patron":f"{a}|{rel}|{b}","estado":"RELACION_DETECTADA"})

    # S1: lexical adjacency. It is deliberately lexical, not semantic.
    for r in rows:
        ts=toks(r.get("text",""))
        for i in range(len(ts)-1):
            add("S1_palabra", f'{r["book_id"]}:{r["chapter"]}:{r["verse"]}', "SIGUE", ts[i].lower(), ts[i+1].lower(), i+1)

    # S2: verse order within chapter.
    chapters=defaultdict(list)
    for r in rows: chapters[(str(r["book_id"]),str(r["chapter"]))].append(r)
    for key, vs in chapters.items():
        vs.sort(key=lambda r:int(r["verse"]))
        for a,b in zip(vs,vs[1:]): add("S2_verso", f"{key[0]}:{key[1]}", "SIGUE", f"V{a['verse']}", f"V{b['verse']}", int(a['verse']))

    # S3/S5: ordered containment of blocks.
    for book, rs in by_book.items():
        chapters_sorted=sorted({int(r["chapter"]) for r in rs})
        for i in range(0,len(rs),block_size):
            block=rs[i:i+block_size]
            if block: add("S3_bloque", book, "CONTIENE", f"V{block[0]['chapter']}:{block[0]['verse']}", f"V{block[-1]['chapter']}:{block[-1]['verse']}", i)
        for i in range(0,len(chapters_sorted),major_size):
            b=chapters_sorted[i:i+major_size]
            if b: add("S5_bloque_mayor", book, "CONTIENE", f"C{b[0]}", f"C{b[-1]}", i)
        for a,b in zip(chapters_sorted,chapters_sorted[1:]): add("S6_libro", book, "SIGUE", f"C{a}", f"C{b}", a)

    # S4: chapter contains its verses.
    for (book,ch),vs in chapters.items():
        vs.sort(key=lambda r:int(r["verse"]))
        if vs: add("S4_capitulo", f"{book}:{ch}", "CONTIENE", f"V{vs[0]['verse']}", f"V{vs[-1]['verse']}", 1)

    return detections


def compare(dets):
    groups=defaultdict(list)
    for d in dets:
        # Relation identity is structural only: operation + direction + arity.
        key=(d["operacion"],d["direccion"],2)
        groups[key].append(d)
    out=[]
    for key,items in groups.items():
        scales=sorted({x["escala"] for x in items}, key=SCALES.index)
        status="RELACION_MULTIESCALA" if len(scales)>=2 else ("RELACION_REPETIDA" if len(items)>1 else "RELACION_DETECTADA")
        out.append({"id_relacion":f"P{len(out)+1:06d}","patron_estructural":{"operacion":key[0],"direccion":key[1],"aridad":2},
                    "escalas_detectadas":scales,"numero_escalas":len(scales),"frecuencia_total":len(items),
                    "estado":status,"interpretacion_semantica":False,"es_fractal":False,
                    "evidencias":items[:20]})
    return out


def main(inp,out):
    rows=load(inp); dets=detect(rows); pats=compare(dets)
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    payload={"version":"V2","fase":"DETECCION_MEDICION","interpretacion":False,"fractalidad_declarada":False,
             "registros_fuente":len(rows),"detecciones":len(dets),"patrones":len(pats),"escalas":list(SCALES),
             "resultados":pats}
    Path(out).write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"estado":"V2_DETECCION_COMPLETADA","registros_fuente":len(rows),"detecciones":len(dets),"patrones":len(pats),"salida":out},ensure_ascii=False,indent=2))

if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('Uso: python ALACRAN_V2_DETECTOR.py <entrada.jsonl> <salida.json>')
    main(*sys.argv[1:])
