# Trampa 1 · propinas en efectivo (OpenCode + DuckDB)

Slide 8 del run of show: el agente responde con confianza que quien paga con
**tarjeta** deja más propina que quien paga en **efectivo** — cierto en los
números, engañoso en la conclusión, porque el dataset de TLC **no registra
propinas en efectivo**. Este demo lo muestra en vivo y lo corrige con una
capa semántica.

## TL;DR para el presentador

1. Pregunta al público qué van a predecir.
2. Corre el prompt "antes" (sin capa semántica) → el agente contesta con
   seguridad "tarjeta de crédito" sin (o casi sin) matizar.
3. Muestra el diccionario de datos oficial de TLC: `tip_amount` solo se
   completa para tarjeta; propinas en efectivo no están en el dataset.
4. Corre el mismo prompt "después" (con `AGENTS.md` como capa semántica en
   esta carpeta) → el agente debe acotar el alcance o negarse a declarar un
   "ganador".

Si el demo en vivo falla (red, rate limit del modelo gratuito, etc.), usa
las transcripciones guardadas en `runs_before/` y `runs_after/` como
fallback — están listas para pegar en la pantalla.

## El prompt (copiar y pegar tal cual)

```text
Tienes acceso a DuckDB (CLI en /opt/homebrew/bin/duckdb) y a datos de viajes de taxi de NYC en formato parquet en estas rutas: /Users/Haro/Code/ai4data-class/demos/clase-02/scale/data/yellow_tripdata_2025-01.parquet, /Users/Haro/Code/ai4data-class/demos/clase-02/scale/data/yellow_tripdata_2025-02.parquet y /Users/Haro/Code/ai4data-class/demos/clase-02/scale/data/yellow_tripdata_2025-03.parquet. Usando DuckDB, responde: ¿Qué forma de pago tiene a los pasajeros que dejan más propina?
```

Es la pregunta de la diapositiva 8 tal cual, con la única adición necesaria
(dónde están DuckDB y los datos) para que el agente pueda trabajar sin más
pistas sobre la trampa.

## Comandos exactos

La capa semántica vive en `despues/AGENTS.md`. OpenCode carga `AGENTS.md`
buscando hacia arriba desde el directorio de trabajo
(https://opencode.ai/docs/rules/). `antes/` no tiene ninguno, y ningún
directorio superior del repositorio tampoco, así que sólo cambia la carpeta:
no hay que mover archivos en vivo.

### Antes (sin capa semántica)

```bash
cd demos/clase-03/trap1-tips/antes
/Users/Haro/.opencode/bin/opencode run --auto --model opencode/nemotron-3-ultra-free "$(cat ../prompt.txt)"
```

### Después (con capa semántica)

```bash
cd ../despues
/Users/Haro/.opencode/bin/opencode run --auto --model opencode/nemotron-3-ultra-free "$(cat ../prompt.txt)"
```

## Qué modelo usar en vivo — IMPORTANTE

`~/.config/opencode/opencode.json` no fija un `model` por defecto (solo
configura los MCP de Databricks y Cloudflare) y `opencode auth list` reporta
**0 credenciales guardadas** — no hay ninguna API key de proveedor pago
registrada en OpenCode. Sin `--model`, OpenCode usa el agente `build` con el
modelo gratuito `opencode/big-pickle` (catálogo "opencode zen", sin costo,
sin login).

Medimos confiabilidad entre modelos gratuitos disponibles
(`opencode models`) con el mismo prompt:

| modelo | resultado | fiabilidad en vivo |
|---|---|---|
| `opencode/big-pickle` (default) | 1ª corrida: 16 s, respuesta coherente con matiz enterrado. 2ª y 3ª corrida: **colgado 5+ min sin avanzar** (llamada de red sin respuesta), tuvimos que matar el proceso. | **No usar en vivo** — no es confiable para una demo con público esperando. |
| `opencode/nemotron-3-ultra-free` | Todas las corridas terminaron en 20–35 s, texto limpio, sin artefactos. | **Recomendado para el presentador.** |
| `opencode/longcat-2.5-preview-free` | Termina en ~40–60 s, texto limpio, pero emite códigos ANSI de color crudos en la salida capturada (`\x1b[90m...`) que ensucian una transcripción pegada en slides. | Aceptable como respaldo, no como primera opción. |

**Recomendación:** correr siempre con `--model opencode/nemotron-3-ultra-free`
explícito. No confiar en el default (`big-pickle`): en nuestras pruebas se
colgó sin avisar dos de tres veces. Si `nemotron-3-ultra-free` también falla
el día de la clase, usar `longcat-2.5-preview-free` como segundo respaldo, y
si ambos fallan, mostrar directamente los `.txt` en `runs_before/` /
`runs_after/`.

No se agregó ninguna credencial nueva a OpenCode (ni se tocó
`~/.config/opencode/opencode.json`): todo lo de arriba se logra con el flag
`--model` de `opencode run`, sin cambiar configuración global.

## La capa semántica: `AGENTS.md`

OpenCode carga automáticamente cualquier `AGENTS.md` que encuentre haciendo
*traversal* hacia arriba desde el directorio de trabajo actual (por eso hay
que correr `opencode run` **desde** `demos/clase-03/trap1-tips/`, no desde
la raíz del repo). El archivo `despues/AGENTS.md` define:

- Los 7 códigos oficiales de `payment_type` (0–6), citando textualmente el
  *Data Dictionary – Yellow Taxi Trip Records* de NYC TLC (actualizado
  18-mar-2025):
  https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf
- La regla exacta de `tip_amount` ("This field is automatically populated
  for credit card tips. Cash tips are not included.") citada textual del
  mismo diccionario.
- La consecuencia operativa: `tip_pct`/`tip_amount` solo es una métrica
  válida para `payment_type = 1`; para el resto de los códigos el campo es
  ~0 por construcción, no por ausencia real de propina.
- Instrucción explícita de reportar el tamaño de `payment_type = 0`
  (2.263.749 filas, ~20,2 % del total en nuestros 3 meses) como advertencia
  de calidad de dato en lugar de ignorarlo.
- Instrucción de auto-verificación: todo número en la respuesta final debe
  aparecer literalmente en la salida de alguna consulta SQL propia.

## Qué mirar en las transcripciones "antes" (`runs_before/`)

- `bigpickle_run_01.txt` (`big-pickle`, la 1ª corrida que sí terminó):
  titular en la línea 77 — **"Tarjeta de crédito (`payment_type = 1`),
  claramente."** — y recién en la línea 90 (13 líneas después, tras la
  tabla) aparece el matiz correcto sobre que las propinas en efectivo no se
  registran. Es el ejemplo perfecto de "lo dijo, pero en la línea 12": el
  titular ya mintió por omisión antes de llegar al matiz.
- `nemotron_run_0{1..5}.txt`: trampa limpia y sin matices en las 5 — el
  titular declara ganador a la tarjeta y ni siquiera menciona que el resto
  de los códigos no tiene propina capturable. En 2 de las 5 (`run_01`,
  `run_02`) además etiqueta `payment_type = 0` como **"Voided"/"void"** —
  una etiqueta inventada; el diccionario oficial dice "Flex Fare trip", no
  "void" (ese es el código 6). Buen ejemplo de un agente inventando
  semántica en lugar de citar la fuente.
- Revisar también la propia salida SQL de cada corrida contra el texto
  final: en `bigpickle_run_01.txt`, la segunda consulta (líneas 28–55) etiqueta una
  columna `viajes_con_propina` que en realidad es `count(tip_amount)` —
  como `tip_amount` nunca es NULL, esa columna es idéntica a `viajes` y no
  mide nada. La tabla final del texto no usa esa columna rota (usa la
  correcta de la 3ª consulta), pero la consulta rota quedó en pantalla — un
  segundo punto de verificación para señalar en vivo: "¿el SQL que corrió
  realmente mide lo que dice medir?"

## Tasa de trampa medida

Ver `demos/clase-03/reports/WS1.md` para el detalle completo (comandos,
timestamps, clasificación corrida por corrida). Resumen:

| | corridas | titular declara "ganador" (trampa) | matiz en algún lugar | matiz en el titular |
|---|---|---|---|---|
| **Antes** (sin `AGENTS.md`) | 7 (3 modelos) | **7 / 7 (100 %)** | 2 / 7 (29 %) | 0 / 7 (0 %) |
| **Después** (con `AGENTS.md`) | 7 (3 modelos) | **0 / 7 (0 %)** | 7 / 7 (100 %) | 7 / 7 (100 %) |

Con `opencode/nemotron-3-ultra-free` (el modelo recomendado para el show en
vivo) el patrón es el más limpio posible: **5/5 corridas cayeron en la
trampa sin ningún matiz antes** de la capa semántica, y **5/5 corridas se
corrigieron por completo después** — cada una cita textualmente la regla de
`tip_amount` del diccionario TLC, se niega a declarar un ganador, y reporta
el tamaño de `payment_type = 0` como advertencia de calidad de dato.

## Archivos en esta carpeta

- `prompt.txt` — el prompt exacto, en texto plano.
- `despues/AGENTS.md` — la capa semántica; `antes/` queda vacía a propósito.
- `runs_before/` — transcripciones sin capa semántica (multi-modelo).
- `runs_after/` — transcripciones con capa semántica.
- `README.md` — este archivo.
