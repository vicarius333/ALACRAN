#!/usr/bin/env python3
"""ALACRAN V2: deteccion multiescala conservadora.

Solo mide relaciones observables. No asigna significado semantico ni declara
fractalidad. Si no existe una identidad suficiente entre escalas, se reporta
como familia multiescala candidata, pero NO como relacion multiescala.
"""
import json, re, sys
from collections import defaultdict
from pathlib import Path

SCALES=("S1_palabra","S2_verso","S3_bloque","S4_capitulo","S5_bloque_mayor","S6_libro")

def toks(text): return re.findall(r"[^\W_]+(?:['’-][^\W_]+)*", text or "", flags=re.UNICODE)

def load(path):
    with open(path,encoding="utf-8") as f: return [json.loads(x) for x in f if x.strip()]

def detect(rows,block_size=5,major_size=5):
    by_book=defaultdict(list); chapters=defaultdict(list)
    for r in rows:
        b=str(r["book_id"]); by_book[b].append(r); chapters[(b,str(r["chapter"]))].append(r)
    for v in by_book.values(): v.sort(key=lambda r:(int(r["chapter"]),int(r["verse"])))
    for v in chapters.values(): v.sort(key=lambda r:int(r["verse"]))
    d=[]
    def add(scale,unit,rel,a,b,pos,identity):
        d.append({"id_relacion":f"R{len(d)+1:08d}","escala":scale,"unidad":unit,
          "elemento_a":a,"operacion":rel,"elemento_b":b,"posicion":pos,"frecuencia":1,
          "distancia":1,"direccion":"A→B","patron":f"{identity}|{rel}|A→B",
          "identidad":identity,"estado":"RELACION_DETECTADA"})
    for r in rows:
        ts=toks(r.get("text",""))
        for i in range(len(ts)-1): add("S1_palabra",f'{r["book_id"]}:{r["chapter"]}:{r["verse"]}',"SIGUE",ts[i].lower(),ts[i+1].lower(),i+1,"WORD_WORD")
    for (b,c),vs in chapters.items():
        for a,z in zip(vs,vs[1:]): add("S2_verso",f"{b}:{c}","SIGUE",f"V{a['verse']}",f"V{z['verse']}",int(a['verse']),"VERSE_VERSE")
        if vs: add("S4_capitulo",f"{b}:{c}","CONTIENE",f"V{vs[0]['verse']}",f"V{vs[-1]['verse']}",1,"CHAPTER_VERSE")
    for b,rs in by_book.items():
        for i in range(0,len(rs),block_size):
            x=rs[i:i+block_size]
            if x: add("S3_bloque",b,"CONTIENE",f"V{x[0]['chapter']}:{x[0]['verse']}",f"V{x[-1]['chapter']}:{x[-1]['verse']}",i,"BLOCK_VERSE")
        cs=sorted({int(r["chapter"]) for r in rs})
        for i in range(0,len(cs),major_size):
            x=cs[i:i+major_size]
            if x: add("S5_bloque_mayor",b,"CONTIENE",f"C{x[0]}",f"C{x[-1]}",i,"MAJORBLOCK_CHAPTER")
        for a,z in zip(cs,cs[1:]): add("S6_libro",b,"SIGUE",f"C{a}",f"C{z}",a,"CHAPTER_CHAPTER")
    return d

def compare(dets):
    # Exact relation identity is required. This prevents semantic equivalence
    # from being invented from different entity types.
    exact=defaultdict(list); families=defaultdict(list)
    for x in dets:
        exact[(x["identidad"],x["operacion"],x["direccion"],x["elemento_a"],x["elemento_b"])].append(x)
        families[(x["operacion"],x["direccion"],x["identidad"])].append(x)
    out=[]
    for key,items in exact.items():
        scales=sorted({x["escala"] for x in items},key=SCALES.index)
        out.append({"id_relacion":f"P{len(out)+1:06d}","patron_estructural":{"identidad":key[0],"operacion":key[1],"direccion":key[2],"elemento_a":key[3],"elemento_b":key[4]},"escalas_detectadas":scales,"numero_escalas":len(scales),"frecuencia_total":len(items),"estado":"RELACION_MULTIESCALA" if len(scales)>=2 else ("RELACION_REPETIDA" if len(items)>1 else "RELACION_DETECTADA"),"interpretacion_semantica":False,"es_fractal":False,"evidencias":items[:20]})
    fam=[]
    for key,items in families.items():
        scales=sorted({x["escala"] for x in items},key=SCALES.index)
        if len(scales)>=2: fam.append({"familia":{"operacion":key[0],"direccion":key[1],"identidad":key[2]},"escalas":scales,"frecuencia":len(items),"requiere_validacion_semantica":True})
    return out,fam

def main(inp,out):
    rows=load(inp); dets=detect(rows); pats,fam=compare(dets)
    payload={"version":"V2","fase":"DETECCION_MEDICION","interpretacion":False,"fractalidad_declarada":False,"registros_fuente":len(rows),"detecciones":len(dets),"patrones":len(pats),"familias_multiescala_candidatas":len(fam),"escalas":list(SCALES),"resultados":pats,"familias_candidatas":fam}
    Path(out).parent.mkdir(parents=True,exist_ok=True); Path(out).write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"estado":"V2_DETECCION_COMPLETADA","registros_fuente":len(rows),"detecciones":len(dets),"patrones":len(pats),"familias_multiescala_candidatas":len(fam),"salida":out},ensure_ascii=False,indent=2))

if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('Uso: python ALACRAN_V2_DETECTOR.py <entrada.jsonl> <salida.json>')
    main(*sys.argv[1:])
