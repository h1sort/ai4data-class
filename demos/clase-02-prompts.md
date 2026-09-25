# Guion de la demo · Clase 2

Abre [las diapositivas](../slides/clase-02.html). Todos los comandos se ejecutan desde la raíz del repositorio. Las rutas de notebook están en [notebooks/](clase-02/notebooks/). Los resultados anteriores de ensayo son históricos: no sustituyen una ejecución actual.

## Antes de transmitir

```bash
uv run demos/clase-02/live.py preflight --remote
uv run demos/clase-02/live.py etl --dataset class1
```

Prepara los tres notebooks en Databricks y la página de Genie usando las instrucciones de [notebooks/](clase-02/notebooks/). Ejecuta el notebook de negocio antes de clase y deja sus gráficas listas. Verifica el acceso a Jev sin mostrar la clave. El notebook usa una referencia a secretos, nunca una clave pegada en una celda.

## 1. Consulta pequeña · diapositiva 8

```bash
uv run demos/clase-02/live.py poll
```

Luego pide al agente vía MCP:

```text
Consulta Cloudflare D1 con tus herramientas MCP. Usa solo las tablas de encuestas y el grupo 8P56ZUVE9Q. Obtén la distribución de respuestas de la pregunta de confianza en análisis de IA. Muestra las opciones, sus recuentos y el total de respuestas de esa pregunta, sin identificadores de participantes. No cambies datos. Usa el mismo SQL que la demo CLI en este repositorio para comparar resultados.
```

Si todavía no hay respuestas, las opciones con cero votos son un resultado válido. El acceso MCP necesita una conexión autenticada; el comando CLI sigue disponible como alternativa.

La consulta compartida vive en [poll_aggregate.sql](clase-02/pipeline/poll_aggregate.sql); las instrucciones exactas del MCP están en [poll-mcp.md](clase-02/pipeline/poll-mcp.md).

## 2. Escala · diapositivas 9–10

Pregunta: **¿Cómo cambia el porcentaje promedio de propina según la hora y el tipo de pago?**

Abre [query.sql](clase-02/scale/query.sql), muestra las columnas necesarias y ejecuta cada motor en su propia diapositiva:

```bash
uv run demos/clase-02/live.py scale --engine sqlite
uv run demos/clase-02/live.py scale --engine duckdb
```

La base local es SQLite. Los 11,198,026 registros son viajes, no clientes. En el ensayo fresco del 25 de septiembre, SQLite midió 7.47 s y DuckDB 0.14 s de consulta (0.21 s de proceso); otra corrida con caché caliente midió SQLite en 6.08 s. La caché y el equipo cambian el tiempo: narra la salida actual. La consulta calcula la media de porcentajes por viaje con tarifa positiva, no el cociente de sumas. La propina registrada no representa todas las propinas en efectivo.

La copia analítica evita que esta consulta compita con el servidor operacional. La demo no simula tráfico concurrente ni mide ese impacto.

## 3. ETL con agente · diapositiva 15

```text
Ejecuta una ETL de demostración desde Cloudflare D1 a Databricks usando los CLIs disponibles y el código de demos/clase-02/pipeline. La encuesta de hoy es 8P56ZUVE9Q y la anterior JFQES4AF97. Inspecciona el esquema de encuestas; extrae solo esos grupos; carga y modela los datos en workspace.ai4data usando la identidad ai4data-agent. Conserva la separación entre participantes y respuestas, los valores ausentes y un corte UTC fijo. Verifica unicidad, recuentos y ausencia de grupos ajenos. Muestra solo los recuentos y pruebas. No modifiques D1 ni las encuestas. Termina después de la ETL y las pruebas: la clasificación viene en otro notebook. Usa credenciales del entorno sin imprimirlas. Si ya hay un paso probado que resuelve esto, ejecútalo y explica su resultado.
```

Alternativa directa:

```bash
uv run demos/clase-02/live.py etl --dataset class2
```

No uses `pipeline/run_all.sh` en este momento: ese guion histórico incluye clasificación y comparación.

## 4. Business analytics · diapositiva 17

Abre `01_business_analytics.ipynb` en Databricks y ejecuta las celdas de visualización. Usa toda la población de Clase 1; no solo quienes también contestaron Clase 2. Señala qué mide cada denominador y qué decisión permitiría tomar.

Cierre verbal: **“Listo. Casi. Lo difícil sigue siendo medir un problema que importe y poder actuar sobre él.”**

## 5. Genie · diapositiva 18

Abre el [espacio de Genie](https://dbc-df3c4dbf-3ef7.cloud.databricks.com/genie/rooms/01f1b9020133164e9ffef42225cf323c) y pregunta por la distribución de roles o confianza. Ya pasó una pregunta de humo y generó SQL sobre `c1_vw_resumen_respuestas` con seis filas. Revisa el SQL, su población y el denominador; compáralos con el notebook. La URL, pregunta y SQL probados también están en [`demo-links.json`](clase-02/notebooks/demo-links.json). Si Genie no abre, usa el SQL agregado de respaldo indicado en el README de notebooks.

## 6. ML · diapositiva 19

Abre `02_ml_classifier.ipynb`. Muestra las etiquetas de entrenamiento, entrena el clasificador y llama a `clasificar_persona_ml(puesto_texto)` desde SQL sobre la encuesta de Clase 2. Separa ejemplos de entrenamiento, evaluación y audiencia. En el último ensayo C2 todavía tenía cero títulos; vuelve a ejecutar ETL antes del notebook. Si sigue vacío, muestra `live_titles=0` y explica que no hay predicciones de la audiencia; no sustituyas respuestas por datos sintéticos. El modelo pequeño sirve para explicar el flujo; su evaluación no garantiza precisión sobre esta audiencia.

## 7. LLM / Jev · diapositiva 20

Abre `03_llm_jev.ipynb`. Usa las mismas entradas y etiquetas para comparar métodos. Ejecuta un lote acotado, observa latencia, coincidencias y discrepancias, y examina la confianza de Jev. El notebook debe identificar claramente su fixture sintético si el poll C2 continúa vacío. Coincidir entre modelos no equivale a acertar. LLM/Jev reducen el trabajo de entrenar un modelo propio; la definición de categorías y su evaluación siguen siendo necesarias.

## Cierre · diapositivas 21–22

Recorre el diagrama cliente ↔ OLTP → ETL/ELT → OLAP → Analytics / ML. Ubica en él cada demo que acabamos de ejecutar.

## Referencias

- [Pipeline y comandos individuales](clase-02/pipeline/README.md).
- [Datos NYC TLC y preparación](clase-02/scale/data/README.md).
- [Ensayo histórico, claramente identificado](clase-02-rehearsal-results.md).
- [Astronomer: la columna de juicio](https://www.astronomer.io/blog/what-jev-will-do-to-data-engineering/).
