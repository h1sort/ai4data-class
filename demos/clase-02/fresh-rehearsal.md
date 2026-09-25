# Ensayo fresco · Clase 2 · 25 septiembre 2026

**Estado:** encuesta, escala, ETL de Clase 1 y ETL de Clase 2 verificados. La preflight remota, los tres notebooks Serverless y Genie pasaron el ensayo del 25 de septiembre.

## Evidencia verificada

| Etapa | Comando y resultado |
|---|---|
| Encuesta por Wrangler | `uv run demos/clase-02/live.py poll` devolvió las opciones 1–5 con 0 votos y total 0. Es el resultado vigente al momento de consulta. |
| Encuesta por MCP | La misma consulta de `pipeline/poll_aggregate.sql` vía D1 `d1_database_query` devolvió las cinco opciones en 0. La respuesta informó `changed_db=false` y `rows_written=0`. |
| Escala · SQLite | `uv run demos/clase-02/live.py scale --engine sqlite` leyó la copia SQLite en modo de solo lectura. La última ejecución midió 7.47 s. Otra ejecución con caché caliente midió 6.08 s. La diapositiva conserva ~7.44 s como referencia histórica de ensayo; no es el tiempo prometido para otra máquina. |
| Escala · DuckDB | `uv run demos/clase-02/live.py scale --engine duckdb` leyó la copia DuckDB en modo de solo lectura: 0.14 s de consulta y 0.21 s de tiempo de proceso en la ejecución medida. |
| Equivalencia | Las dos bases contienen 11,198,026 viajes de enero–marzo de 2025. La consulta común produjo 120 grupos; los conteos de viajes coinciden exactamente y los porcentajes redondeados difieren como máximo 0.01. |
| ETL Clase 1 | `bash demos/clase-02/pipeline/etl_only.sh --dataset class1`; run `20260925T163432Z`, corte UTC `2026-09-25 16:34:32`. Extrajo 6 polls, 25 opciones, 2,483 votos y 0 respuestas de texto. C1 quedó en 2,483 respuestas y 430 participantes. Pasaron reconciliación, unicidad y denominadores. |
| ETL Clase 2 | `uv run demos/clase-02/live.py etl --dataset class2`; run `20260925T163829Z`, corte UTC `2026-09-25 16:38:29`. Extrajo los dos grupos: 9 polls, 30 opciones, 2,483 votos C1 y 0 votos / 0 respuestas de texto C2. C1 volvió a reconciliar a 2,483 / 430; las 12 comprobaciones C2 pasaron. Los archivos vacíos conservaron esquema explícito. |
| Preflight remota | `uv run demos/clase-02/live.py preflight --remote` terminó con código 0. Herramientas, archivos locales y configuración estaban presentes; el agregado D1 funcionó y Databricks devolvió `SELECT 1 = 1`. Esto no valida ejecución de notebooks, Genie ni Jev. |

El comando SQLite puede medir distinto en otro equipo o estado de caché. En clase, muestra el tiempo que imprime la corrida actual; los números de arriba son evidencia de una corrida reciente, no una garantía.

## Notebooks y Genie

- El SQL smoke sobre `workspace.ai4data.c1_vw_resumen_respuestas` devolvió las seis opciones de rol con denominador 430.
- `uv run demos/clase-02/notebooks/setup_workspace.py run 01_business_analytics` completó como `ai4data-agent`, run `736306116186560`. Marcador: `C1_BUSINESS_COMPLETE|respondents=430|questions=6|roles=6|cross_tab_roles=6`. Generó tres figuras (cobertura de seis preguntas, distribución de seis roles y uso/confianza en IA por rol) y una tabla cruzada por rol.
- `uv run demos/clase-02/notebooks/setup_workspace.py run 02_ml_classifier` completó en Serverless como `ai4data-agent`, run `1041833396718550`. Marcador: `ML_COMPLETE|train=60|holdout=25|accuracy=0.880|live_titles=0`. El modelo se validó con un fixture humano etiquetado (60 ejemplos de entrenamiento, 25 de holdout); la tabla C2 real todavía tiene cero títulos, así que no hubo predicciones de la audiencia. Los primeros intentos con `SparkContext` y `.cache()`/persist fallaron; el notebook se ajustó para Serverless antes de esta corrida exitosa.
- `uv run demos/clase-02/notebooks/setup_workspace.py run 03_llm_jev` completó en Serverless como `ai4data-agent`, run `996605603999209`. Marcador: `AI_JEV_COMPLETE|source=fixture sintético · el poll C2 sigue vacío o no se ha cargado|n=8|agreement=0.750`. Compara ocho títulos sintéticos de enseñanza porque C2 sigue vacío; el acuerdo entre métodos no es una medida de exactitud.
- `uv run demos/clase-02/notebooks/setup_genie.py` pasó cinco consultas SQL de control (filas: 6, 2, 5, 6, 5) y la conversación de humo consultó `workspace.ai4data.c1_vw_resumen_respuestas`, terminó con seis filas. Espacio `01f1b9020133164e9ffef42225cf323c`; [abrir Genie](https://dbc-df3c4dbf-3ef7.cloud.databricks.com/genie/rooms/01f1b9020133164e9ffef42225cf323c). El enlace, pregunta, SQL y resultado están en `notebooks/demo-links.json`.

El ensayo de datos, notebooks y Genie está completo para el estado de las encuestas al corte. C2 puede recibir respuestas nuevas durante la clase; ejecuta la ETL antes de repetir la parte en vivo.
