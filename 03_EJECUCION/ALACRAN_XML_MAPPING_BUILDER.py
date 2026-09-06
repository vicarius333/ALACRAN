#!/usr/bin/env python3
"""Construye un mapeo XML candidato a partir de XML_STRUCTURE_REPORT.json.

IMPORTANTE: el resultado es CANDIDATO, nunca se considera validado
automaticamente. El programa evita imponer etiquetas semanticas.
"""
import json, sys

def local(tag):
    return tag.rsplit('}',1)[-1].lower() if '}' in tag else tag.lower()

def build(report_path, output_path):
    r=json.load(open(report_path,encoding='utf-8'))
    tags=list(r.get('tag_frequencies',{}).keys())
    def candidates(words):
        return [t for t in tags if any(w in local(t) for w in words)]
    result={
      'estado':'CANDIDATO_NO_VALIDADO',
      'source_report':report_path,
      'book_tag_candidates':candidates(['book','livre','libro','bible']),
      'chapter_tag_candidates':candidates(['chapter','chapitre','capitulo','capítulo']),
      'verse_tag_candidates':candidates(['verse','verset','versiculo','versículo']),
      'text_tag_candidates':candidates(['text','texte','texto']),
      'required_action':'Seleccionar y validar explicitamente las etiquetas contra el XML real antes de ejecutar la extraccion.'
    }
    json.dump(result,open(output_path,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    return result

if __name__=='__main__':
    if len(sys.argv)!=3:
        print('Uso: python ALACRAN_XML_MAPPING_BUILDER.py XML_STRUCTURE_REPORT.json XML_MAPPING_CANDIDATE.json'); sys.exit(2)
    print(json.dumps(build(sys.argv[1],sys.argv[2]),ensure_ascii=False,indent=2))
