#!/usr/bin/env python3
"""ALACRAN - Inspector estructural de corpus XML.

Inspecciona un XML grande mediante streaming sin asumir etiquetas semanticas.
No interpreta el contenido ni produce hallazgos.
"""

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict


def local_name(tag):
    return tag.rsplit('}', 1)[-1] if '}' in tag else tag


def inspect_xml(xml_path, output_path, sample_limit=20):
    tag_counts = Counter()
    attr_counts = Counter()
    namespace_counts = Counter()
    path_counts = Counter()
    samples = []
    stack = []
    root_tag = None

    for event, elem in ET.iterparse(xml_path, events=('start', 'end')):
        if event == 'start':
            if root_tag is None:
                root_tag = elem.tag
            stack.append(elem.tag)
            tag_counts[elem.tag] += 1
            for key in elem.attrib:
                attr_counts[key] += 1
                if key.startswith('{') and '}' in key:
                    namespace_counts[key.split('}', 1)[0] + '}'] += 1
            if '}' in elem.tag:
                namespace_counts[elem.tag.split('}', 1)[0] + '}'] += 1
            if len(samples) < sample_limit:
                text = (elem.text or '').strip()
                samples.append({
                    'tag': elem.tag,
                    'local_name': local_name(elem.tag),
                    'attributes': dict(elem.attrib),
                    'text_length': len(text),
                    'path': [local_name(x) for x in stack]
                })
        else:
            path_counts[tuple(local_name(x) for x in stack)] += 1
            stack.pop()
            elem.clear()

    report = {
        'tool': 'ALACRAN_XML_INSPECTOR',
        'version': 'V1',
        'input': xml_path,
        'root_tag': root_tag,
        'tag_frequencies': dict(tag_counts),
        'attribute_frequencies': dict(attr_counts),
        'namespace_frequencies': dict(namespace_counts),
        'element_path_frequencies': {'/'.join(k): v for k, v in path_counts.items()},
        'samples': samples,
        'semantic_interpretation': False,
        'mapping_status': 'PENDIENTE',
        'next_step': 'Revisar este informe y definir explicitamente el mapeo XML antes de extraer datos normalizados.'
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return report


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Uso: python ALACRAN_XML_INSPECTOR.py <HebrewBible.xml> <XML_STRUCTURE_REPORT.json>')
        sys.exit(2)
    report = inspect_xml(sys.argv[1], sys.argv[2])
    print(json.dumps({
        'estado': 'INSPECCION_COMPLETADA',
        'root_tag': report['root_tag'],
        'tags_distintos': len(report['tag_frequencies']),
        'rutas_distintas': len(report['element_path_frequencies']),
        'salida': sys.argv[2]
    }, ensure_ascii=False, indent=2))
