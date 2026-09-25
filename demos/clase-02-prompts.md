# Demo en vivo: de D1 a un warehouse con agentes

Abre Codex en este repositorio. Copia el prompt 0 una vez; pega los demás uno por turno y espera la salida antes de avanzar. El código de referencia está en `demos/clase-02/pipeline/`; la encuesta en vivo está en [Clase 2](https://h1sort.com/p/8P56ZUVE9Q). Usa `ai4data_rehearsal` y los grupos Ensayo para practicar. Los resultados de ensayo, sin respuestas individuales, están en [`clase-02-rehearsal-results.md`](clase-02-rehearsal-results.md).

Antes de abrir Codex, inicia su proceso con `DATABRICKS_TOKEN=$DATABRICKS_AGENT_TOKEN` desde un shell que haya cargado `.env`. El pipeline fuerza el mismo token. Su acceso a D1 usa el login local de `wrangler`. Nunca proyectes `.env`, tokens, respuestas individuales ni `voter_hash`.

## 0. Encargo y límites

```text
Eres mi ingeniero de datos durante una clase en vivo. Responde en español y muestra resultados breves que podamos proyectar. Trabaja en este repositorio y explica los comandos antes de ejecutarlos. Nuestro objetivo: mover respuestas de la encuesta de Clase 2 desde Cloudflare D1 a Databricks, comprobar la carga y convertir texto libre en columnas tipadas con ai_classify y Jev. Usa el pipeline de referencia en demos/clase-02/pipeline; puedes inspeccionarlo y ejecutarlo. No simules resultados ni inventes participantes.

La encuesta de Clase 2 tiene código 8P56ZUVE9Q: confianza en un análisis de IA (1–5), puesto (texto) y tarea a automatizar (texto). Clase 1 tiene código JFQES4AF97; solo necesitamos su Q5, rol declarado, para el cruce entre clases. Ignora los grupos Ensayo YWE57U6B8U y R57BDNR5ZG y cualquier otro grupo, incluido real-time-processing-class. Si te pido practicar, usa ambos códigos Ensayo y workspace.ai4data_rehearsal, nunca mezcles códigos reales con ese esquema.

Usa wrangler desde el checkout hermano h1sort-website (o la ruta D1_REPO) para D1 h1sort-chat. En D1, permite únicamente SELECT, CTE de lectura, PRAGMA de esquema y EXPLAIN QUERY PLAN sobre poll_groups, polls, poll_options, poll_votes y poll_text_answers. La misma D1 guarda chats y autenticación: no los consultes. No escribas en D1 ni cambies encuestas. En Databricks usa el CLI y su Statement API en el warehouse 90f6df4041b446b7. Escribe solo en workspace.ai4data_raw, workspace.ai4data o workspace.ai4data_rehearsal. No cambies permisos ni credenciales.

La identidad para la demo es el service principal ai4data-agent. Las claves están en .env; no las imprimas ni las incluyas en comandos visibles, logs o archivos nuevos. No muestres ni exportes hashes de navegadores ni respuestas de personas. Un participante observable es un voter_hash distinto de Clase 2: representa un navegador, no necesariamente una persona. Usa un corte UTC fijo para modelado y reconciliación; el pipeline comparte el mismo CUTOFF entre ambos pasos. Mantén los NULL como ausencias. Si falla una prueba, detente antes de interpretar.

Para Jev, usa TYPESAFE_API_KEY de .env sin imprimirla. Sus etiquetas son las mismas que las de ai_classify; las descripciones de criterios están en 06_jev.py. La confianza es una señal de revisión, no una verdad. Antes de publicar un resultado, declara su n/N y separa ensayo de datos reales.

Empieza mostrando el orden de los pasos 01–07 de run_all.sh y qué tablas de origen y destino usa cada uno. No ejecutes todavía el pipeline.
```

Plan B: abre el diagrama de capas y el orden de ejecución en [`pipeline/README.md`](clase-02/pipeline/README.md).

## 1. Conectar el warehouse con el CLI

```text
Ejecuta databricks current-user me y databricks warehouses list. Confirma que la identidad es ai4data-agent, localiza el warehouse 90f6df4041b446b7 y explica cómo se envía una sentencia SQL por el CLI. No muestres tokens. Si la identidad es la cuenta administradora, detente y corrige el entorno antes de seguir.
```

Plan B: muestra `demos/clase-02/databricks/run_sql.sh` y explica el Statement API sin ejecutar SQL.

## 2. Explorar la fuente transaccional

```text
Con wrangler, inspecciona solo el esquema de las cinco tablas permitidas. Ubica por código los tres sondeos de Clase 2 y Q5 de Clase 1. Usa EXPLAIN QUERY PLAN para una consulta agregada que cruce rol declarado de Clase 1 con confianza de Clase 2 por voter_hash; no proyectes hashes ni filas individuales. Cuenta tablas y joins. Explica por qué el cruce entre grupos es parcial y por qué el modelo analítico simplifica la pregunta. No cambies datos.
```

Plan B: muestra la comparación OLTP/warehouse de la diapositiva 5.

## 3. Pedir el plan ETL

```text
Antes de ejecutar, revisa 01_extract.sh, 02_load.sql, 03_model.sql y 04_tests.sql. Propón el plan D1 filtrada por ambos códigos → NDJSON → volumen → raw → dim_participante/fct_respuestas → pruebas. Identifica dónde se filtran los grupos, dónde entra el corte UTC y cómo se reconcilian los recuentos. Indica las columnas que guardarán confianza, puesto, tarea y rol declarado. Espera mi siguiente prompt.
```

Plan B: usa la sección «Data model» de `pipeline/README.md`.

## 4. Extraer y cargar

```text
Ejecuta 01_extract.sh y 02_load.sh para los grupos 8P56ZUVE9Q y JFQES4AF97 con un RUN_ID UTC nuevo. Extrae solo las cinco tablas de encuesta. Carga los NDJSON al volumen workspace.ai4data_raw.landing y recrea las cinco tablas raw. Muestra únicamente nombres de tabla y recuentos; no muestres NDJSON, respuestas, hashes o rutas con credenciales. Guarda RUN_ID y un CUTOFF UTC para los próximos pasos.
```

Plan B: usa `run_all.sh` con los códigos reales; si falla, muestra la arquitectura y los recuentos agregados del ensayo en `clase-02-rehearsal-results.md`.

## 5. Modelar y reconciliar

```text
Con el RUN_ID y CUTOFF ya fijados, ejecuta 03_model.sh ai4data 8P56ZUVE9Q JFQES4AF97 "$CUTOFF". Antes de 04_tests.sh, pide a la sala que prediga si pasarán las diez pruebas. Ejecuta 04_tests.sh con exactamente el mismo esquema, códigos y CUTOFF. Muestra PASS/FAIL, recuentos agregados y ausencias por pregunta. Si alguna falla, investiga sin seguir a la clasificación. No conviertas ausencias en cero ni confundas participantes con respuestas.
```

Plan B: revela las diez pruebas aprobadas del ensayo en `clase-02-rehearsal-results.md`, etiquetadas como ensayo.

## 6. Clasificar dentro del warehouse

```text
Ejecuta 05_ai_classify.sh ai4data. Explica las dos columnas que crea: persona desde puesto_texto y categoria_tarea desde tarea_texto. Muestra recuentos por etiqueta y por NULL, sin texto individual. Examina las tres inyecciones solo si realmente existen en los datos reales; si no existen, usa los resultados sintéticos del ensayo y márcalos como tales. ¿Qué señal de incertidumbre devuelve ai_classify? No atribuyas certeza a una etiqueta por el solo hecho de tener tipo.
```

Plan B: muestra la distribución agregada y las tres inyecciones sintéticas de `clase-02-rehearsal-results.md`.

## 7. Clasificar con Jev y decidir revisión

```text
Ejecuta 06_jev.py --schema ai4data. Verifica antes que la clave TypeSafe esté disponible sin mostrarla. Explica por qué una sola llamada plantea dos preguntas (persona y categoría), qué etiquetas y descripciones se envían, cuánto tarda y cuánto cuesta aproximadamente según los tokens de entrada. Resume las bandas de confianza: >=0.9 warehouse, 0.5–0.9 revisión con LLM, <0.5 revisión humana. No declares esas bandas calibradas para esta población; son una política de demostración.
```

Plan B: muestra los tiempos, coste y bandas del ensayo en `clase-02-rehearsal-results.md`.

## 8. Comparar las dos columnas de juicio

```text
Ejecuta 07_compare.sh ai4data. Antes de revelar el resultado, pregunta a la sala si ai_classify y Jev coincidirán en persona más del 80%. Muestra acuerdo global y por banda de confianza con n/N, además de categoría de tarea. Para las inyecciones, usa solo ejemplos presentes; si no hay, compara el ensayo, claramente etiquetado. Explica que acuerdo entre sistemas no mide exactitud frente a verdad etiquetada. No imprimas respuestas individuales de participantes reales.
```

Plan B: revela el acuerdo del ensayo en `clase-02-rehearsal-results.md`.

## 9. La pregunta final

```text
Pregunta primero a la sala qué persona clasificada tendrá mayor proporción de confianza 4–5. Después usa las tablas agregadas de 07_compare.sh: por persona Jev muestra numerador, denominador y porcentaje; no ordenes segmentos con n<5. Muestra cuántos navegadores de Clase 2 también respondieron Q5 de Clase 1 y un ejemplo del cruce rol declarado × persona clasificada. Son taxonomías diferentes: no calcules un «porcentaje de coincidencia» igualando los textos. Explica que el solapamiento parcial limita la comparación y que son autoinformes, no competencia medida.
```

Plan B: revela las tablas agregadas del ensayo en `clase-02-rehearsal-results.md` y vuelve a las diapositivas 23–24.
