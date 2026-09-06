#!/usr/bin/env python3
"""ALACRAN - Extractor XML normalizado.

El mapeo de etiquetas debe ser proporcionado explicitamente despues de la
inspeccion estructural. El extractor no inventa ni infiere etiquetas.
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def text_of(elem):
    return ''.join(elem.itertext()).strip()


def extract(xml_path, mapping_path, output_path):
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    required = ['book_tag', 'chapter_tag', 'verse_tag']
    missing = [x for x in required if x not in mapping]
    if missing:
        raise ValueError(f'Mapeo incompleto: faltan {missing}')

    book_tag = mapping['book_tag']
    chapter_tag = mapping['chapter_tag']
    verse_tag = mapping['verse_tag']
    source_id = mapping.get('source_id', 'ALACRAN_FUENTE_XML_BEBLIA_V1')

    current_book = None
    current_chapter = None
    count = 0

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as out:
        for event, elem in ET.iterparse(xml_path, events=('start', 'end')):
            if event == 'start':
                if elem.tag == book_tag:
                    current_book = {
                        'id': mapping.get('book_id_attribute') and elem.attrib.get(mapping['book_id_attribute']),
                        'name': mapping.get('book_name_attribute') and elem.attrib.get(mapping['book_name_attribute'])
                    }
                elif elem.tag == chapter_tag:
                    current_chapter = mapping.get('chapter_number_attribute') and elem.attrib.get(mapping['chapter_number_attribute'])
            else:
                if elem.tag == verse_tag:
                    ref = {
                        'book_id': current_book.get('id') if current_book else None,
                        'book': current_book.get('name') if current_book else None,
                        'chapter': current_chapter,
                        'verse': mapping.get('verse_number_attribute') and elem.attrib.get(mapping['verse_number_attribute']),
                        'text': text_of(elem),
                        'source_id': source_id
                    }
                    out.write(json.dumps(ref, ensure_ascii=False) + '\n')
                    count += 1
                elem.clear()

    return count


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Uso: python ALACRAN_EXTRACTOR_XML.py <HebrewBible.xml> <mapping.json> <DATOS_BIBLICOS_NORMALIZADOS.jsonl>')
        sys.exit(2)
    n = extract(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps({'estado': 'EXTRACCION_COMPLETADA', 'registros': n, 'salida': sys.argv[3]}, ensure_ascii=False, indent=2))
