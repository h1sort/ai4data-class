# Resultados del ensayo · Clase 2

Resultados del 25 de septiembre de 2026. Son datos **sintéticos** de «Ensayo · Clase 2» (`YWE57U6B8U`) y «Ensayo · Clase 1» (`R57BDNR5ZG`); sirven como referencia y respaldo para la demo, no describen al público real. La ejecución completa de `pipeline/run_all.sh` tardó **139 s** y las **10 pruebas** de datos pasaron. Hubo 61 navegadores en Clase 2: 60 del generador y 1 respuesta de prueba anterior. Cuarenta de los 61 (65.6 %) tenían también rol declarado en el ensayo de Clase 1.

## Clasificación y revisión

| Medida | Resultado |
|---|---:|
| Acuerdo de persona `ai_classify` × Jev | 48/57 (84.2 %) |
| Confianza Jev ≥0.9 | 43/45 (95.6 %) |
| Confianza Jev 0.5–0.9 | 5/10 (50.0 %) |
| Confianza Jev <0.5 | 0/2 (0.0 %) |
| Acuerdo de categoría de tarea | 52/55 (94.5 %) |
| Jev para 60 participantes | 2.8 s; 37,808 tokens de entrada; ~$0.0016 |

`ai_classify` tomó unos 50 s y fue el paso más lento. El acuerdo compara dos sistemas, no mide exactitud frente a etiquetas verificadas. Las bandas de confianza muestran dónde difirieron en este ensayo; sus umbrales no están calibrados para la audiencia real.

Las tres inyecciones sintéticas en el puesto recibieron `ejecutivo`, `otro` y `ejecutivo` de `ai_classify`, sin confianza. Jev devolvió `practitioner` en las tres, con confianza **0.26**, **0.25** y **0.51**. Una prueba anterior de la primera inyección, con descripciones mínimas de las opciones Jev, había devuelto `ejecutivo` a **0.56**. El cambio de criterios cambió el juicio.

## ¿Qué persona declara más confianza en IA?

Confianza alta significa respuesta 4 o 5 a la pregunta de confianza en un análisis generado por IA. Persona proviene de Jev sobre el puesto escrito por cada participante. Cada denominador incluye solo participantes con ambos valores.

| Persona Jev | Confianza 4–5 | n/N |
|---|---:|---:|
| estudiante | 60.0 % | 3/5 |
| ejecutivo | 50.0 % | 5/10 |
| practitioner | 47.1 % | 16/34 |
| manager | 37.5 % | 3/8 |

No hubo un grupo `otro` con denominador válido en este corte. Las diferencias, especialmente con n=5, son descriptivas de datos inventados; no respaldan una conclusión sobre personas reales.

## Cruce con el rol declarado en Clase 1

De los 40 navegadores presentes en ambos ensayos, el cruce agregado incluye estos ejemplos:

| Rol declarado en Clase 1 | Persona Jev en Clase 2 | Navegadores |
|---|---|---:|
| Liderazgo / gestión | ejecutivo | 9 |
| Liderazgo / gestión | manager | 3 |
| Liderazgo / gestión | practitioner | 1 |
| Ingeniería de datos | practitioner | 7 |
| Ingeniería de datos | manager | 1 |

Los nombres de las categorías difieren entre preguntas. Este cruce no tiene un porcentaje de coincidencia definido sin acordar primero una correspondencia entre taxonomías. Los CSV completos de respaldo se generan **localmente** en `pipeline/out/fallback/<run_id>/` y están ignorados por Git porque contienen respuestas y claves individuales.
