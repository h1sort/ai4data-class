# Guion de la demo · Clase 3

Abre [las diapositivas](../slides/clase-03.html). Los comandos se ejecutan desde la raíz del repositorio salvo que se indique otra carpeta. Toda cifra de la presentación proviene de un comando de este guion o de [sources.md](clase-03/sources.md).

## Antes de transmitir

- Conexión por cable. Fuente del terminal grande.
- Pestañas abiertas: [transformer-explainer](https://poloclub.github.io/transformer-explainer/), Databricks (notebooks de `/Shared/AI4Data/Clase3`), el espacio de Genie y la encuesta de Clase 2 en el teléfono.
- Comprueba que Databricks lee `workspace.ai4data` (datos reales, grupo `8P56ZUVE9Q`), no el esquema de ensayo.
- Ejecuta una vez el «antes» de la Trampa 1 para calentar el modelo.

## 0–1 · Corrección y recapitulación

«Dije ~100×. Fue 46×»: 6.9 s ÷ 0.15 s = 46.0. Cuatro eras en una frase, las tres palancas y el mapa OLTP → ETL/ELT → OLAP con Clase 1, Clase 2 y hoy.

## 2–6 · Del LLM al agente

Abre transformer-explainer en vivo. La receta y sus fuentes están en [sources.md](clase-03/sources.md): el costo de Llama 3.1 es **estimado**; Common Crawl es un ejemplo general, no el corpus confirmado de Llama. Pregunta «¿Qué convierte a un LLM en un agente?» y recoge 3–4 respuestas antes de mostrar la definición de Simon Willison.

## 8 · Trampa 1 · propinas en efectivo

Pide a la sala una predicción. Luego:

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

_Pendiente de WS3._

## 10 · Trampa 3 · inyección de prompts

_Pendiente de WS4._

## 11 · Evals y palancas

```bash
uv run demos/clase-03/evals/run_evals.py --mode both
uv run demos/clase-03/agent/agent.py "¿Cuántos viajes hay en el dataset de taxis?"
```

El agente de [agent.py](clase-03/agent/agent.py) es el bucle de la diapositiva 4: objetivo, modelo, petición de herramienta, ejecución del harness y observación. Necesita `ANTHROPIC_API_KEY` en el entorno o en `../h1sort-website/.dev.vars`. La inyección del caso T3 es un caso de prueba sintético, no una respuesta de la clase.

## Q&A

Tiempo protegido. Los mensajes de cierre van después.
