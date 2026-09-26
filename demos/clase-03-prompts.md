# Guion de la demo · Clase 3

Abre [las diapositivas](../slides/clase-03.html). Los comandos se ejecutan desde la raíz del repositorio salvo que se indique otra carpeta. Toda cifra de la presentación proviene de un comando de este guion o de [sources.md](clase-03/sources.md).

## Antes de transmitir

- Conexión por cable. Fuente del terminal grande.
- Pestañas abiertas: [transformer-explainer](https://poloclub.github.io/transformer-explainer/), Databricks (notebooks de `/Shared/AI4Data/Clase3`), el espacio de Genie y la encuesta de Clase 2 en el teléfono.
- Comprueba que Databricks lee `workspace.ai4data` y el grupo real de Clase 2 (`8P56ZUVE9Q`).
- Ejecuta una vez el «antes» de la Trampa 1 para calentar el modelo.

## 0–1 · Portada y recorrido del bootcamp

La portada presenta tres criterios: significado, frescura y evidencia. Presenta las tres palancas y el mapa OLTP → ETL/ELT → OLAP; justo después viene «De una encuesta viva a respuestas que podemos revisar». Esa síntesis sale de las transcripciones: Clase 1 conectó un agente a la encuesta viva en D1; Clase 2 llevó las respuestas por ETL a OLAP y clasificó texto libre; hoy revisamos cuándo las respuestas del agente son defendibles.

## 2–6 · Del LLM al agente

Abre transformer-explainer en vivo. La receta y sus fuentes están en [sources.md](clase-03/sources.md): el costo de Llama 3.1 es **estimado**; Common Crawl es un ejemplo general, no el corpus confirmado de Llama. Pregunta «¿Qué convierte a un LLM en un agente?» y recoge 3–4 respuestas antes de mostrar la definición de Simon Willison.

## 8 · Trampa 1 · propinas en efectivo

La diapositiva incluye el prompt completo y un botón para copiarlo: nombra DuckDB, los tres Parquet de NYC TLC (enero–marzo de 2025) y la pregunta. Es el mismo texto de `trap1-tips/prompt.txt`, usado antes y después. Pide a la sala una predicción. Luego:

```bash
cd demos/clase-03/trap1-tips/antes
/Users/Haro/.opencode/bin/opencode run --auto --model opencode/nemotron-3-ultra-free "$(cat ../prompt.txt)"
```

Señala la conclusión principal y compárala con el SQL que el propio agente ejecutó. Muestra el diccionario de la TLC: `tip_amount` sólo registra propinas con tarjeta; `payment_type = 0` es *Flex Fare trip* y suma 2,263,749 viajes. Después, con la capa semántica:

```bash
cd ../despues
/Users/Haro/.opencode/bin/opencode run --auto --model opencode/nemotron-3-ultra-free "$(cat ../prompt.txt)"
```

Sin red o si el modelo gratuito se cuelga: usa las transcripciones de [runs_before/](clase-03/trap1-tips/runs_before/) y [runs_after/](clase-03/trap1-tips/runs_after/). Detalle y tasa medida (7/7 antes, 0/7 después) en [trap1-tips/README.md](clase-03/trap1-tips/README.md).

## 9 · Trampa 2 · datos viejos

El diagrama de la diapositiva incluye los comandos. Desde la raíz del repositorio:

```bash
uv run demos/clase-02/live.py etl --dataset class2
```

Esta ETL lee el grupo real de Clase 2 en D1, carga y modela `workspace.ai4data.dim_participante` y `workspace.ai4data.fct_respuestas`, y registra el corte en `workspace.ai4data.etl_snapshots`. La clasificación es un paso separado. Abre [10_trap2_walkthrough.ipynb](https://dbc-df3c4dbf-3ef7.cloud.databricks.com/#workspace/Shared/AI4Data/Clase3/10_trap2_walkthrough) o ejecútalo desde terminal:

```bash
uv run demos/clase-03/databricks/setup_workspace.py run 10_trap2_walkthrough
```

El notebook genera `workspace.ai4data.c3_personas_v1` a partir de los 165 puestos y compara JEV con `ai_classify`. Abre el [espacio de Genie](https://dbc-df3c4dbf-3ef7.cloud.databricks.com/genie/rooms/01f1b9c1000c11369a488c3037b59db1) y pregunta «¿Cuántos ejecutivos hay en la clase?». Verifica el SQL generado antes de citar la cifra.

La siguiente diapositiva tiene botones para copiar el conteo vivo de D1 (votos + respuestas de texto) y la consulta al último snapshot aprobado de Databricks. Usa ambos para comparar la misma unidad. En la última comprobación, el agente devolvió «a fecha 2026-09-26 15:06:33, 494 de 494 filas»; vuelve a ejecutar las consultas antes de decir un número en vivo.

## 10 · Trampa 3 · inyección de prompts

La fila real de `tarea_texto` que intenta hacer decir «jojojojo» y ocho respuestas no válidas quedaron como `otro` en v1 y `no_valido` en v2. En esa corrida comparativa de 165 puestos, 32 etiquetas cambiaron en al menos un método; ninguna respuesta real intentó forzar la etiqueta «ejecutivo». La vista actual `c3_personas_v1` cuenta 7 ejecutivos con `ai_classify` y 9 con JEV; confirma esos números en vivo porque la vista puede regenerarse. v2 no demuestra inmunidad ni es un reemplazo libre de efectos secundarios.

## 11 · Evals y palancas

```bash
uv run demos/clase-03/evals/run_evals.py --mode both
uv run demos/clase-03/agent/agent.py "Usa check_freshness para Clase 2 y dime a fecha de qué carga cuántas de las respuestas actuales ya están en el snapshot."
```

El agente de [agent.py](clase-03/agent/agent.py) es el bucle de la diapositiva 4: objetivo, modelo, petición de herramienta, ejecución del harness y observación. Necesita `ANTHROPIC_API_KEY` en el entorno o en `../h1sort-website/.dev.vars`. La inyección del caso T3 es un caso de prueba sintético, no una respuesta de la clase.

## Cierre y contacto

Vuelve al recorrido de las tres clases: preguntamos a la fuente, movimos y modelamos el dato, y verificamos el resultado. Cierra con los cuatro criterios de la diapositiva: métrica, fecha, frontera de confianza y eval. La última diapositiva contiene LinkedIn, X y h1sort.com. Deja tiempo para preguntas después de mostrarla.
