# ALACRAN V2 — Detección Multiescala

## Estado
FASE: DETECCIÓN Y MEDICIÓN
INTERPRETACIÓN: BLOQUEADA
FRACTALIDAD: NO DECLARADA
V1: INTACTA

## Regla de V2
Una relación solo puede considerarse `RELACION_MULTIESCALA` si la misma relación observable aparece en al menos dos escalas distintas.

En esta implementación, identidad suficiente significa conservar exactamente la identidad estructural registrada. No se inventa equivalencia semántica entre elementos distintos.

Cuando varias escalas comparten solo una familia abstracta (`SIGUE`, `CONTIENE`), se registra como `familia_multiescala_candidata` y requiere una fase posterior de validación funcional/semántica. No se convierte automáticamente en `RELACION_MULTIESCALA`.

## Escalas
- S1: palabra / forma
- S2: verso
- S3: bloque de versos (5 versos)
- S4: capítulo
- S5: bloque mayor (5 capítulos)
- S6: libro

Los tamaños 5 son parámetros operativos iniciales y no constituyen una afirmación sobre la estructura del corpus.

## Estados permitidos
- `RELACION_DETECTADA`
- `RELACION_REPETIDA`
- `RELACION_MULTIESCALA`
- `NO_CONFIRMADA`

## Prohibiciones
- No interpretación semántica.
- No inferencia de intención del autor.
- No equivalencia funcional inventada.
- No conclusión `ES_FRACTAL`.

## Flujo
`FUENTE → DETECCIÓN → MEDICIÓN → COMPARACIÓN → AUDITORÍA`

La interpretación queda fuera de V2.