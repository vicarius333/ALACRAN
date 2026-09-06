# RUN ALACRAN — Ingesta y cierre

## 1. Obtener la fuente
Descargar `HebrewBible.xml` desde la fuente registrada en `BIBLIA/FUENTE_XML_MANIFIESTO.json`.

## 2. Inspeccionar
```bash
python 03_EJECUCION/ALACRAN_XML_INSPECTOR.py HebrewBible.xml XML_STRUCTURE_REPORT.json
```

## 3. Generar candidatos de mapeo
```bash
python 03_EJECUCION/ALACRAN_XML_MAPPING_BUILDER.py XML_STRUCTURE_REPORT.json XML_MAPPING_CANDIDATE.json
```

## 4. Validar el mapeo
Crear `XML_MAPPING.json` seleccionando las etiquetas reales del informe. No copiar candidatos sin comprobarlos contra el XML.

Campos esperados:
- `book_tag`
- `chapter_tag`
- `verse_tag`
- opcionalmente `book_id_attribute`, `book_name_attribute`, `chapter_number_attribute`, `verse_number_attribute`
- `source_id`

## 5. Extraer
```bash
python 03_EJECUCION/ALACRAN_EXTRACTOR_XML.py HebrewBible.xml XML_MAPPING.json DATOS_BIBLICOS_NORMALIZADOS.jsonl
```

## 6. Validar
```bash
python 04_VALIDACION/ALACRAN_XML_VALIDATOR.py DATOS_BIBLICOS_NORMALIZADOS.jsonl
```

## 7. Regla de cierre
Solo si la validación es `VALIDO` puede cambiarse el estado de ingesta a `COMPLETADA` y comenzar el análisis ALACRAN.

## Prohibiciones
- No modificar el XML fuente.
- No mezclar versiones sin declarar procedencia.
- No convertir candidatos en hechos.
- No generar patrones o hipótesis durante la ingesta.
- No declarar corpus completo sin una ejecución real y un informe de validación.
