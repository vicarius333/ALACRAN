# ALACRAN — Ejecución local del corpus XML

## Objetivo
Ejecutar la ingesta sin modificar el XML fuente y sin asumir su estructura.

## 1. Obtener la fuente
Guardar `HebrewBible.xml` localmente desde la fuente registrada en:
`BIBLIA/FUENTE_XML_MANIFIESTO.json`

## 2. Inspeccionar
```bash
python 03_EJECUCION/ALACRAN_XML_INSPECTOR.py HebrewBible.xml XML_STRUCTURE_REPORT.json
```

La inspección produce frecuencias de etiquetas, atributos, namespaces, rutas y muestras. No produce interpretaciones.

## 3. Mapear
Completar `BIBLIA/XML_MAPPING_TEMPLATE.json` usando únicamente elementos observados en `XML_STRUCTURE_REPORT.json`.

## 4. Extraer
```bash
python 03_EJECUCION/ALACRAN_EXTRACTOR_XML.py HebrewBible.xml BIBLIA/XML_MAPPING.json DATOS_BIBLICOS_NORMALIZADOS.jsonl
```

## 5. Validar
El JSONL resultante debe pasar por el validador ALACRAN antes de cualquier análisis.

## Regla de cierre
Si la estructura real no permite identificar inequívocamente libro, capítulo y unidad textual, el proceso se detiene en `NO_VERIFICADO` y no se fabrican registros.
