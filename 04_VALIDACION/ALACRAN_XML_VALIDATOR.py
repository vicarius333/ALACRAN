#!/usr/bin/env python3
"""Valida JSONL bíblico normalizado y reporta integridad."""
import json,sys

def validate(path):
    required=['book_id','book','chapter','verse','text','source_id']
    total=bad=dup=0; refs=set(); issues=[]
    with open(path,encoding='utf-8') as f:
        for line_no,line in enumerate(f,1):
            if not line.strip(): continue
            total+=1
            try: r=json.loads(line)
            except Exception as e: bad+=1; issues.append({'line':line_no,'error':'JSON_INVALID'}); continue
            miss=[k for k in required if k not in r]
            if miss or not str(r.get('text','')).strip():
                bad+=1; issues.append({'line':line_no,'error':'REGISTRO_INCOMPLETO','faltantes':miss})
            ref=(r.get('source_id'),r.get('book_id'),r.get('chapter'),r.get('verse'))
            if ref in refs: dup+=1; issues.append({'line':line_no,'error':'REFERENCIA_DUPLICADA','ref':ref})
            refs.add(ref)
    return {'estado':'VALIDO' if bad==0 and dup==0 else 'NO_VALIDO','registros':total,'invalidos':bad,'duplicados':dup,'issues':issues[:100]}

if __name__=='__main__':
    if len(sys.argv)!=2: print('Uso: python ALACRAN_XML_VALIDATOR.py DATOS_BIBLICOS_NORMALIZADOS.jsonl'); sys.exit(2)
    print(json.dumps(validate(sys.argv[1]),ensure_ascii=False,indent=2))
