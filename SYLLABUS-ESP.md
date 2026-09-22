# Temario: IA para Datos, de los chats a los agentes

## Sobre el curso

Curso práctico para perfiles de datos (analistas, ingenieros de datos, analytics engineers, científicos de datos y responsables de equipos de datos) que quieren trabajar con LLMs y agentes en serio: no solo "preguntarle al chat", sino preparar el contexto, configurar el harness, conectar agentes a sus sistemas de datos con garantías y medir si funcionan.

Doce sesiones. Las tres primeras son gratuitas y abiertas; el resto forma parte del curso completo.

### Modelo freemium

- **Clases 1-3 (gratis, online):** por qué cambia el rol de datos, una migración OLTP → warehouse hecha con agentes de principio a fin, y casos reales. Objetivo: que entiendas por qué esto va en serio y veas que funciona con datos reales.
- **Clases 4-12 (curso completo):** hacerlo tú, con tus datos. Chats con conectores, agentes de código, tu propio harness (AGENTS.md, skills, MCP, hooks), capa semántica, APIs y modelos de decisión, IA dentro del warehouse, evals, seguridad y proyecto final.

### Modelo mental del curso: Saber, Hacer, Decidir

Usamos una definición deliberadamente útil de agente: *un agente LLM ejecuta herramientas en bucle para lograr un objetivo* (Simon Willison). Objetivo → modelo → petición de herramienta → el harness la ejecuta → observación, y vuelta a empezar. Todo lo que rodea al modelo en ese bucle (permisos, límites, identidad, auditoría, recuperación) es el harness, y ahí vive la ingeniería, no dentro del prompt.

Clasificamos cada sistema por la libertad más consecuente que le delegamos, porque la arquitectura sigue a la consecuencia. El modelo puede ser el mismo; lo que cambia es la autoridad y el precio de equivocarse.

| Autoridad | Pregunta típica en datos | Si falla | Control principal | Clases |
| --- | --- | --- | --- | --- |
| **Saber** (Know) | "¿Cuántos clientes activos tuvimos en marzo?" | Respuesta incorrecta o no autorizada | Contexto y capa semántica, acceso por identidad, límites, rastro (SQL y fuentes) | 2, 4, 7, 9 |
| **Hacer** (Do) | "Migra estas tablas y crea el modelo dbt" | Acción incorrecta | Herramientas estrechas, propuesta ≠ ejecución, revisión, idempotencia, auditoría | 2, 5, 6 |
| **Decidir** (Decide) | "¿Esta transacción se escala a revisión?" | Juicio incorrecto | Evidencia completa, umbrales calibrados, razonamiento estructurado, escalado humano, workflow explícito | 3, 8, 9, 11 |

Principios que se repiten en todas las clases:

- La arquitectura sigue a la consecuencia: primero nombra la autoridad, después el control.
- Propuesta no es ejecución: el modelo propone; código, permisos y personas deciden.
- Puede pasar vs debe pasar: el modelo razona en local; los invariantes se codifican en el workflow, no se piden en el prompt.
- Empieza con la menor libertad que crea valor: SQL fijo → agente → workflow explícito.
- El contexto importa más que el modelo.
- Dale esa libertad. Controla todo lo demás.

### Resultados de aprendizaje

Al terminar el curso serás capaz de:

- Clasificar un sistema de IA sobre datos por la autoridad que delega (saber, hacer, decidir) y nombrar el control que corresponde a cada una.
- Explicar qué sistemas de datos están preparados para agentes y elegir el stack adecuado para tu caso.
- Migrar datos de un sistema transaccional a uno analítico con ayuda de agentes, y exponerlo a agentes de forma segura (solo lectura, MCP, capa semántica).
- Trabajar con chats, copilotos y agentes de código en tareas de datos reales, sabiendo qué nivel de autonomía usar en cada caso.
- Configurar un harness de datos: ficheros de instrucciones, skills, servidores MCP, hooks y subagentes.
- Diseñar el contexto (metadatos, definiciones de métricas, capa semántica) que hace que un agente acierte.
- Construir productos de datos con APIs de LLMs, salidas estructuradas y modelos de decisión, dentro y fuera del warehouse.
- Evaluar sistemas de IA sobre datos con error analysis, evaluadores de código y LLM-as-judge, integrados en CI.
- Identificar y mitigar riesgos de seguridad (prompt injection vía datos, tool poisoning, exceso de permisos).

### A quién va dirigido

- Analistas y analytics engineers que ya escriben SQL y quieren multiplicar su alcance.
- Ingenieros de datos que quieren usar agentes para construir y mantener pipelines sin perder el control.
- Científicos de datos y desarrolladores que van a construir productos de datos con LLMs.
- Líderes de datos que necesitan decidir stack, políticas y adopción en su equipo.

Requisito: SQL intermedio y nociones de Python. No hace falta experiencia previa con IA.

### Requisitos y herramientas

- Entorno: terminal, VS Code o Cursor, git, `uv` para Python.
- Datos: Postgres (local o Docker), DuckDB, cuenta gratuita de MotherDuck. Opcional: trial de Snowflake, BigQuery sandbox o Databricks Free Edition.
- Modelos y agentes: al menos una suscripción a Claude, ChatGPT o Gemini; un agente de código (Claude Code, Codex CLI o Gemini CLI). Se indican alternativas gratuitas y modelos locales (Ollama) donde es viable.
- Notebooks: marimo o Jupyter.

## Mapa del curso

| Clase | Título | Bloque | Acceso |
| --- | --- | --- | --- |
| 1 | Cómo ha cambiado el rol de datos en la era IA | 1. La era agéntica de los datos | Gratis |
| 2 | De OLTP a un Data Warehouse con agentes | 1. La era agéntica de los datos | Gratis |
| 3 | Flujos agénticos de datos | 1. La era agéntica de los datos | Gratis |
| 4 | LLMs vía chat para datos: de prompts a contexto | 2. Interfaces: chats, copilotos y harnesses | Curso completo |
| 5 | Copilotos y agentes de código para datos | 2. Interfaces: chats, copilotos y harnesses | Curso completo |
| 6 | Tu harness de datos: AGENTS.md, skills, MCP, hooks y subagentes | 2. Interfaces: chats, copilotos y harnesses | Curso completo |
| 7 | Contexto para agentes: capa semántica, metadatos y RAG | 3. Construir: contexto, APIs, decisiones y productos | Curso completo |
| 8 | APIs, salidas estructuradas y modelos de decisión | 3. Construir: contexto, APIs, decisiones y productos | Curso completo |
| 9 | IA dentro del warehouse y productos de datos | 3. Construir: contexto, APIs, decisiones y productos | Curso completo |
| 10 | Evals I: analizar y medir sistemas de IA sobre datos | 4. Confiar: evals, seguridad y operación | Curso completo |
| 11 | Evals II, seguridad y operación | 4. Confiar: evals, seguridad y operación | Curso completo |
| 12 | Proyecto final y futuro | 5. Proyecto final | Curso completo |

## Bloques temáticos

### Bloque 1: La era agéntica de los datos (Clases 1-3, gratis)

- Qué ha cambiado en el rol de datos y qué habilidades se demandan ahora.
- Fundamentos: OLTP vs OLAP; databases vs data warehouses vs data lakes; qué hace a un sistema "preparado para agentes".
- Stacks para trabajar con LLMs: local, cloud ligero y enterprise.
- Migración didáctica OLTP → warehouse con agentes, y uso del warehouse desde agentes.
- Casos reales enmarcados como Problema → Cómo lo evaluamos → Solución → Resultado.

### Bloque 2: Interfaces: chats, copilotos y harnesses (Clases 4-6)

- Cómo funciona un LLM, lo justo para usarlo bien. De prompt engineering a context engineering.
- Chats con conectores y agentes de datos (ChatGPT Data agent, Claude con MCP y Excel, Gemini en Sheets y BigQuery).
- Copilotos y agentes de código: IDEs, CLIs (Claude Code, Codex, Gemini CLI), agentes nativos de datos (Snowflake CoCo, Databricks Genie Code) y notebooks (marimo, Jupyter AI).
- Harness: Agente = Modelo + Harness. AGENTS.md, Agent Skills, MCP, hooks, subagentes y permisos.

### Bloque 3: Construir: contexto, APIs, decisiones y productos (Clases 7-9)

- Capa semántica y metadatos como contexto; context engineering y RAG aplicados a datos.
- APIs de LLMs, tool calling y salidas estructuradas. De strings a decisiones tipadas: modelos de decisión (System One Models, ej. Jev).
- Funciones de IA en SQL (Snowflake, Databricks, BigQuery) y agentes gestionados por la plataforma.
- Arquitectura de referencia y construcción de productos de datos: NLQ gobernado, informes automáticos, pipelines de decisión.

### Bloque 4: Confiar: evals, seguridad y operación (Clases 10-11)

- Ciclo Analizar → Medir → Mejorar (Hamel Husain y Shreya Shankar) aplicado a datos: trazas, error analysis, evaluadores de código y LLM-as-judge.
- Suites de tareas al estilo ADE-bench, evals en CI/CD, monitorización en producción.
- Seguridad de agentes de datos: prompt injection vía datos, tool poisoning, mínimo privilegio, auditoría.
- Coste, adopción en equipos y nuevos roles.

### Bloque 5: Proyecto final (Clase 12)

- Producto de datos agéntico con evals, de la fuente OLTP a la interfaz, presentado y defendido.

## Clases

Cada clase incluye ejercicio práctico y lecturas. Las herramientas son, en su mayoría, gratuitas o con capa gratuita. El repositorio del curso incluye un dataset OLTP de ejemplo que se reutiliza de la Clase 2 al proyecto final.

### Clase 1: Cómo ha cambiado el rol de datos en la era IA (Bloque 1, gratis)

Objetivo: entender qué ha cambiado de verdad, qué se pide ahora y el mapa mental que usaremos el resto del curso.

- Repaso de cómo ha cambiado el rol
  - De escribir SQL y pipelines a mano a especificar, revisar y orquestar trabajo hecho por agentes.
  - Del "dashboard para todos" a "agentes que responden sobre datos gobernados".
  - Qué se ha comoditizado (código repetitivo, EDA inicial, documentación) y qué se ha revalorizado (modelado, semántica, gobierno, criterio).
- Nuevas habilidades en demanda
  - Context engineering: preparar metadatos, definiciones y ejemplos para que el modelo acierte.
  - Configurar y gobernar agentes: ficheros de instrucciones, skills, MCP, permisos, revisión.
  - Evals: saber medir si un sistema de IA sobre datos funciona.
  - Modelado semántico y calidad de datos: la IA amplifica lo bueno y lo malo de tu warehouse.
- Conceptos fundamentales para el curso
  - OLTP vs OLAP: por qué tu base de datos de producción no es donde debe leer un agente.
  - Data Warehouses vs Data Lakes vs Databases (y lakehouse): qué guarda cada uno, para quién y a qué coste.
  - Vocabulario mínimo de IA: LLM, ventana de contexto, tool calling, agente, MCP, skill, harness.
  - Qué es un agente: ejecuta herramientas en bucle para lograr un objetivo. El bucle (objetivo → modelo → herramienta → harness → observación) y por qué el harness es donde está la ingeniería.
  - El gradiente de autoridad aplicado a datos: Saber (responder sobre datos), Hacer (cambiar pipelines, tablas, código) y Decidir (juzgar filas o casos). Mismo modelo, distinta consecuencia; la arquitectura sigue a la consecuencia.
- ¿Qué sistemas están preparados para los agentes?
  - Criterios: catálogo y metadatos consultables, capa semántica, control de acceso (RBAC, filas y columnas), auditoría, endpoint MCP o API de agentes, funciones de IA en SQL, aislamiento de coste y carga.
  - Por familia: Snowflake (Cortex, MCP gestionado, CoCo), Databricks (Unity Catalog, Genie), BigQuery (MCP remoto, AI.GENERATE), DuckDB/MotherDuck (ligero, local-first), Postgres (pg_duckdb, MCP de solo lectura).
- ¿Cuándo elegir cada uno?
  - Matriz de decisión: volumen, gobierno, presupuesto, tamaño de equipo, latencia y dónde ya viven tus datos.
- Qué stacks de datos puedes usar para trabajar con LLMs
  - Local y gratis: Postgres o CSV/Parquet → DuckDB → agente de código con MCP.
  - Cloud ligero: MotherDuck + dbt + agente de código.
  - Enterprise: Snowflake, Databricks o BigQuery con sus agentes nativos y MCP.
- Demo de cierre: un agente respondiendo preguntas sobre un warehouse local vía MCP. Puente a la Clase 2: cómo se construye eso desde cero.

### Clase 2: De OLTP a un Data Warehouse con agentes (Bloque 1, gratis)

Objetivo: ver de principio a fin una migración didáctica de una base de datos transaccional a un sistema preparado para analítica y agentes, construida con ayuda de agentes y después usada por agentes. Cubre: Migración → Uso.

- Punto de partida: una aplicación con Postgres (OLTP), esquema normalizado y sin documentación.
- Migración
  - Diseño del destino: DuckDB/MotherDuck por ser gratuito y didáctico; el patrón es el mismo en Snowflake, BigQuery o Databricks.
  - Extraer y cargar con un agente de código: `ATTACH` de Postgres desde DuckDB, `CREATE OR REPLACE TABLE ... AS SELECT`, cargas idempotentes y re-ejecutables.
  - Modelado analítico asistido: de tablas normalizadas a un modelo en estrella o capa "silver" con nombres predecibles y grano explícito.
  - Documentación generada y revisada: descripciones de tablas y columnas que serán el contexto de los agentes.
- Apoyado de agentes para el desarrollo (autoridad: Hacer)
  - Cómo pedir el trabajo: plan → ejecutar → revisar. Qué revisar siempre y qué automatizar con tests de datos.
  - El agente propone; tú ejecutas o apruebas. Git y los tests de datos son el registro y la red de seguridad.
  - Errores típicos de los agentes en migraciones (tipos, zonas horarias, claves duplicadas, filtros silenciosos) y cómo detectarlos.
- Cómo trabajar con agentes ya en el data warehouse (autoridad: Saber)
  - Exponer el warehouse por MCP con un rol de solo lectura. Solo lectura no significa sin control: identidad, límites de turnos y consultas, y rastro.
  - Preguntar en lenguaje natural desde el chat o desde el agente de código; leer el SQL generado, las tablas fuente y los supuestos; iterar el contexto hasta que acierte.
  - Primer contacto con la capa semántica: por qué "ingresos" necesita una definición antes de que nadie pregunte por ellos.
- Demo de cierre: la misma pregunta que el agente respondía mal al principio, respondida bien solo por mejorar el contexto. Puente a la Clase 3: qué pasa cuando esto se aplica a casos reales.

### Clase 3: Flujos agénticos de datos (Bloque 1, gratis)

Objetivo: charla entre motivacional y práctica con casos que el instructor ha aplicado en su carrera con IA y datos, en banca y en otros sectores, siempre con el mismo marco para que sean replicables.

- Marco de cada caso
  1. Contexto y problema: qué dolía, a quién y cuánto costaba.
  2. Cómo lo evaluamos: qué autoridad delegamos (saber, hacer o decidir) y el precio de equivocarse; criterio de éxito, riesgos, qué no podía salir mal, dónde tenía que estar el humano.
  3. Solución aplicando IA: arquitectura, herramientas, nivel de autonomía.
  4. Resultado y lecciones: qué funcionó, qué no y qué haríamos distinto hoy.
- Casos (banca y otros sectores)
  - Clasificación y enriquecimiento de registros con texto libre a escala.
  - Documentar y migrar tablas y procesos legacy con agentes.
  - Conciliaciones y detección de anomalías en reporting.
  - Informes recurrentes con narrativa generada y cifras verificadas.
  - Anti-casos: dónde la IA no compensó y por qué.
- Patrones que se repiten
  - Nombra la autoridad, después el control. Empieza con la menor libertad que crea valor.
  - Humano en el bucle donde el error cuesta; automatización total donde el resultado se puede verificar.
  - Decisiones estructuradas antes que texto libre.
  - El contexto importa más que el modelo.
- Cierre del bloque gratuito: mapa detallado de las Clases 4-12 y qué serás capaz de construir al terminar el curso.

### Clase 4: LLMs vía chat para datos: de prompts a contexto (Bloque 2)

- Cómo funciona un LLM, lo justo para usarlo bien: tokens, ventana de contexto, modelos de razonamiento, tool calling, salidas estructuradas; por qué alucina y en qué situaciones.
- Elegir modelo para datos: frontier (Claude, GPT, Gemini) vs abiertos (Llama, Qwen, DeepSeek) vs locales (Ollama). Coste, latencia, privacidad, calidad en SQL y Python.
- De prompt engineering a context engineering: el prompt es una parte; el contexto (esquema, definiciones, ejemplos, resultados previos) decide la calidad.
  - Técnicas: esquema y definiciones en el contexto, ejemplos few-shot, pedir el SQL antes que la respuesta, exigir supuestos explícitos, razonamiento paso a paso para interpretar resultados.
- Chats con conectores y agentes de datos, lo que ha cambiado
  - ChatGPT: Data agent con conectores a Snowflake, BigQuery, Databricks, Redshift y otros; usa contexto de dbt y capas semánticas; genera dashboards.
  - Claude: Projects, conectores MCP a tu warehouse, análisis de ficheros, Claude for Excel.
  - Gemini: en Sheets (`=AI()`, Fill with Gemini) y en BigQuery.
  - Cuándo el chat basta (exploración, interpretación, comunicación) y cuándo no (reproducibilidad, escala, gobierno).
  - Si una consulta fija responde la pregunta, no necesitas un agente: un SQL guardado o un dashboard es más barato y más fiable. El bucle aporta cuando la investigación es dinámica.
  - Deja rastro: SQL, tablas fuente y supuestos en cada respuesta; abstenerse cuando la evidencia no alcanza.
- Uso en datos: EDA guiada, traducir insights para stakeholders, generar y contrastar hipótesis, revisar SQL ajeno, documentar.
- Privacidad y seguridad en chats: qué datos subes, retención, planes empresa vs consumo, anonimización.
- Ejercicio: el mismo dataset en tres configuraciones (chat sin contexto, chat con esquema y definiciones, chat con conector). Comparar SQL, respuestas y errores.

### Clase 5: Copilotos y agentes de código para datos (Bloque 2)

- Niveles de autonomía: autocompletado → chat en el IDE → modo agente → agentes en background o en la nube. Qué nivel para qué tarea y qué riesgo asume cada uno.
- Herramientas
  - IDEs: Cursor, VS Code con Copilot en modo agente, Windsurf.
  - Agentes de terminal: Claude Code, Codex CLI, Gemini CLI, OpenCode.
  - Agentes nativos de datos: Snowflake CoCo (Snowsight, Desktop, CLI), Databricks Genie Code, Gemini en BigQuery. Qué aportan: contexto de catálogo, RBAC y linaje sin configuración.
  - Notebooks: marimo (reactivo, ficheros `.py`, `mo.sql`), Jupyter AI, Hex, Deepnote.
- Buenas prácticas de trabajo con agentes de código en datos
  - Plan primero; tareas pequeñas y verificables; git como red de seguridad.
  - Clasifica las herramientas del agente por consecuencia: lectura, lectura sensible (PII), escritura reversible (esquema de desarrollo, rama), escritura consecuente (producción, `DROP`, `DELETE`). Aprobación explícita a partir de la escritura.
  - Herramientas estrechas, no llaves maestras: `run_readonly_sql` antes que un shell con credenciales de producción. Acceso a la herramienta ≠ permiso del usuario ≠ aprobación de ejecución.
  - Solo lectura por defecto contra bases de datos; credenciales separadas para el agente.
  - Tests de datos como criterio de "hecho" (dbt tests, assertions).
  - Revisión de SQL generado: grano, joins, filtros de fecha, nulos, dobles conteos, tablas equivocadas.
- Casos de uso: modelos dbt, pipelines (Airflow, Dagster), depurar queries lentas, migrar dialectos SQL, documentación masiva.
- Ejercicio: con un agente de código, construir y testear un modelo dbt sobre el warehouse de la Clase 2 y revisar el diff como si fuera de un compañero.

### Clase 6: Tu harness de datos: AGENTS.md, skills, MCP, hooks y subagentes (Bloque 2)

- Agente = Modelo + Harness. El harness es todo lo que no es el modelo: prompts de sistema, ficheros de instrucciones, herramientas y MCP, skills, hooks, sandbox, orquestación, permisos y observabilidad. En el bucle objetivo → modelo → herramienta → harness → observación, el paso "harness" es donde viven políticas, límites, identidad, auditoría y recuperación.
- Guías (feedforward) vs sensores (feedback): anticipar errores vs detectarlos y dejar que el agente se corrija. Computacionales (tests, linters, dbt tests) vs inferenciales (LLM-as-judge, revisión).
- Tres reglas del harness: una descripción de tool no es autorización (la identidad viaja en el contexto de ejecución, no en el prompt); los presupuestos son controles de parada (límite de turnos, de llamadas a herramientas y deadlines); la salida de una herramienta es entrada no confiable. Los controles se suman; el prompt es una capa pequeña.
- Ficheros de instrucciones: `AGENTS.md` / `CLAUDE.md` para un repo de datos: convenciones de nombres, definiciones de métricas, tablas de referencia, qué no tocar.
- Agent Skills, estándar abierto: carpetas con `SKILL.md` (name, description, instrucciones, scripts y referencias); progressive disclosure. Skills para datos: cómo modelar en nuestro dbt, cómo perfilar un CSV, checklist de revisión de SQL.
- MCP (Model Context Protocol): tools, resources y prompts. Servidores relevantes para datos: dbt MCP (capa semántica, `text_to_sql`), Snowflake-managed MCP (Cortex Analyst, Search y Agents como tools), BigQuery MCP remoto, DuckDB y Postgres de solo lectura. Local vs remoto, OAuth, permisos por tool; leer las descripciones de las tools que instalas.
- Hooks: validar SQL antes de ejecutarlo, bloquear DML/DDL, formatear, correr tests después de cada cambio.
- Subagentes: aislar contexto (explorar esquema, escribir SQL, revisar) y paralelizar.
- Evidencia: ADE-bench (dbt Labs) muestra que el mismo modelo resuelve más tareas con skills y MCP que sin ellos. El harness importa tanto como el modelo.
- Ejercicio: montar un harness para el repo del curso (AGENTS.md, dos skills, MCP a DuckDB de solo lectura, hook que bloquea escrituras) y medir antes/después con cinco tareas.

### Clase 7: Contexto para agentes: capa semántica, metadatos y RAG (Bloque 3)

- Por qué falla text-to-SQL: el esquema crudo no lleva significado de negocio. Casos de "SQL correcto que cuenta lo que no es".
- Capa "silver" preparada para IA: nombres predecibles, descripciones prescriptivas, grano explícito, métricas complejas precomputadas en el modelo correcto.
- Capa semántica: métricas, dimensiones y entidades definidas una vez para personas y agentes (dbt Semantic Layer, vistas semánticas de Snowflake y Cortex Analyst, métricas y Genie spaces en Databricks). Cómo la consumen los agentes vía MCP (`list_metrics`, `query_metrics`, `get_dimensions`).
- Una salida estructurada no es grounding; la capa semántica sí. El esquema valida la forma de la respuesta; el código verifica que las cifras salen de las fuentes que dice.
- La autorización viaja con la consulta: filas y columnas filtradas por la identidad del usuario antes de entrar en el contexto del modelo, no por instrucciones en el prompt.
- Context engineering aplicado: el menor conjunto de tokens de alta señal; recuperación just-in-time frente a cargar todo; compactación; "context rot".
- RAG hoy en datos: recuperación sobre documentación, tickets y definiciones; búsqueda vectorial en el warehouse (Cortex Search, Vector Search) como herramienta del agente, no como sustituto del SQL.
- Metadatos como producto: catálogo, linaje, owners, frescura. Todo lo que el agente puede consultar antes de responder.
- Ejercicio: definir cinco métricas en una capa semántica y comprobar que el agente responde igual desde chat, agente de código y API.

### Clase 8: APIs, salidas estructuradas y modelos de decisión (Bloque 3)

- APIs de LLMs (OpenAI, Anthropic, Google y abiertos vía proveedores): SDKs, streaming, tool calling, salidas estructuradas con JSON Schema, batch, caché de prompts. Coste y latencia reales.
- Patrones para datos: enriquecimiento por filas (clasificar, extraer, normalizar), generación de SQL con validación, resúmenes de tablas, agentes con herramientas propias.
- De strings a decisiones: cuando lo que necesitas no es texto sino una decisión tipada (categoría, score, ruta, campo extraído) que el software use directamente.
  - "Smart if-statements" en pipelines: clasificar, enrutar, puntuar, extraer y ramificar donde una regla a mano es frágil.
  - Umbrales por confianza: automatizar por encima, revisión humana por debajo.
- Construye un caso, no un veredicto (autoridad: Decidir). La línea base seductora es `registro → LLM → etiqueta`. El trabajo con consecuencias exige: evidencia completa antes de evaluar, umbrales validados y ruta de política, razonamiento estructurado con procedencia, escalado y rastro duradero. La salida del modelo es una recomendación; la decisión final es del workflow o de una persona.
  - Puede pasar vs debe pasar: el modelo decide en local (qué evidencia mirar, cómo interpretarla); qué evidencia es obligatoria, qué umbral aplica y cuándo se escala son invariantes que van en código.
  - Calibración con datos held-out: un score solo sirve para automatizar si más confianza significa más acierto.
- Modelos de decisión / System One Models (ej. Jev, de TypeSafe AI): estado no estructurado de entrada, valores tipados con probabilidades calibradas de salida; sin errores de tipo; latencias de decenas o cientos de milisegundos y coste órdenes de magnitud menor. Casos: map-reduce sobre grandes volúmenes, tiempo real, verificar, juzgar y guardrails. Sistema 1 (rápido, estructurado) vs Sistema 2 (LLM con razonamiento): cuándo usar cada uno y cómo combinarlos.
- Fine-tuning y modelos pequeños especializados: cuándo compensan frente a prompts más contexto.
- Ejercicio: pipeline que clasifica y extrae campos de 10.000 registros de texto libre con (a) LLM y salidas estructuradas y (b) modelo de decisión. Comparar coste, latencia, acuerdo entre ambos y calibración.

### Clase 9: IA dentro del warehouse y productos de datos (Bloque 3)

- Funciones de IA en SQL: Snowflake (`AI_CLASSIFY`, `AI_EXTRACT` con scores, `AI_COMPLETE`), Databricks (`ai_query` y funciones por tarea), BigQuery (`AI.GENERATE` con `output_schema`). Enriquecer sin sacar los datos del warehouse; gobierno y coste.
- Agentes gestionados por la plataforma: Snowflake Cortex Agents y Snowflake Intelligence, Databricks Genie, agentes de datos en BigQuery. Exponerlos por MCP. Cuándo usarlos y cuándo construir el tuyo.
- Construir productos de datos con LLMs
  - NLQ sobre datos gobernados con capa semántica.
  - Informes automáticos con narrativa generada y cifras verificadas contra el warehouse.
  - Agentes de mantenimiento: documentación, linaje, detección de anomalías, optimización de queries.
  - Arquitectura de referencia: fuente → warehouse → capa semántica → MCP/API → agente → interfaz (Streamlit o app) → trazas.
- Elegir por flujo de control, no por moda: camino predeterminado → código y SQL fijo; la elección dinámica de herramientas aporta valor → bucle de agente; hay que pausar, persistir, inspeccionar u obligar un orden → workflow explícito (LangGraph o el orquestador que ya uses) con agentes acotados dentro. Un workflow no es más inteligente; tiene más invariantes.
- Observabilidad desde el primer día: trazar cada llamada (prompt, tools, SQL, filas, respuesta). Estas trazas son el insumo de las evals.
- Ejercicio: prototipo de NLQ e informe automático sobre el warehouse del curso, con trazas guardadas.

### Clase 10: Evals I: analizar y medir sistemas de IA sobre datos (Bloque 4)

- Por qué evals: sin medida no hay mejora ni confianza. Error analysis como la inversión de mayor retorno. Ciclo Analizar → Medir → Mejorar (Hamel Husain y Shreya Shankar).
- Instrumentación y trazas: registrar todo lo que hizo el agente. Un visor de datos simple como herramienta principal.
- Error analysis: leer trazas, anotar fallos en abierto, agrupar en modos de fallo, priorizar. Un experto de dominio vale más que un comité.
- Datos sintéticos para descubrir errores cuando aún no hay logs de producción.
- Tipos de evaluadores
  - Nivel 1, código: SQL válido, tablas permitidas, grano correcto, comparación de resultados contra answer key, tests de datos.
  - Nivel 2, LLM-as-judge validado contra criterio humano (acuerdo, sesgos, cuándo una métrica es ruido).
  - Nivel 3, A/B y métricas de producto.
- Evaluar agentes: tool calls, retrieval, multi-turno. ADE-bench como modelo de suite de tareas para datos (tarea, answer key, tests que deciden pasa/no pasa).
- Evals proporcionales a la autoridad: Saber → fugas de acceso, frescura, citas correctas; Hacer → elección de herramienta, replay de propuestas, escrituras repetidas; Decidir → calibración held-out, tasa de overrides humanos, drift.
- Ejercicio: 30 trazas del producto de la Clase 9 → taxonomía de fallos → tres evaluadores.

### Clase 11: Evals II, seguridad y operación (Bloque 4)

- Evals en CI/CD: suite de tareas que corre al cambiar prompt, modelo, skill o servidor MCP; comparar experimentos; evitar sobreajustar a la suite.
- Monitorización en producción: drift, coste, latencia, tasa de intervención humana.
- Seguridad de agentes de datos
  - Prompt injection vía datos (filas, tickets, documentos) y tool poisoning (descripciones de tools MCP).
  - Exceso de agencia: mínimo privilegio, roles de solo lectura, seguridad a nivel de fila y columna, allowlists de queries, auditoría, aprobación humana para escrituras.
  - Escrituras seguras: previsualizar el efecto exacto, token de aprobación de un solo uso, clave de idempotencia, y ante un timeout reconciliar antes de reintentar.
  - Red-teaming básico del producto antes que lo hagan otros.
- Protocolo de manejo: de comportamiento observado a control. Método para convertir cada modo de fallo en un control concreto, por autoridad.
  - Saber: usa la tabla equivocada → capa semántica y evals de retrieval; datos viejos → frescura y versionado; llega a datos restringidos → filtrado por identidad; rellena huecos con cifras plausibles → umbral de evidencia y abstención; da vueltas → presupuestos y deadlines; no deja rastro → SQL y fuentes citadas.
  - Hacer: elige la herramienta equivocada → conjunto pequeño y evals de elección; la usa mal → esquemas tipados y validación en servidor; repite una escritura → idempotencia y reconciliación; obedece instrucciones en los datos → salida de herramienta como entrada no confiable; actúa como otro usuario → identidad propagada; actúa en silencio → previsualización, confirmación y auditoría.
  - Decidir: decide antes de tener la evidencia → campos obligatorios y joins; trata el conflicto como certeza → calibración y escalado; pierde el hilo al fallar → checkpoints durables y nodos idempotentes; no sabe explicar → procedencia y razonamiento estructurado; caso nuevo → interrupción humana y etiqueta de override.
- La supervisión humana es proporcional a la autoridad: revisión por muestreo en Saber, aprobación por escritura en Hacer, revisión obligatoria por umbral en Decidir.
- Coste: tokens, caché, modelos pequeños o de decisión para lo repetitivo, batch.
- Equipos y adopción: quién mantiene el AGENTS.md, las skills y la capa semántica; políticas de uso; cómo medir productividad sin engañarse.
- Ejercicio: pipeline de CI con evals y un intento de inyección contra el producto propio. Corregir y volver a pasar la suite.

### Clase 12: Proyecto final y futuro (Bloque 5)

- Presentaciones del proyecto final: arquitectura, harness, evals y demo en vivo.
- Debate: agentes de plataforma vs propios, modelos de decisión, estándares (MCP, Agent Skills), el rol del profesional de datos en dos años.
- Recap de herramientas y lecciones. Certificación y cierre.

## Proyecto final

Producto de datos agéntico con evals, de extremo a extremo:

1. Fuente OLTP → warehouse (DuckDB/MotherDuck o cloud) con modelo analítico documentado.
2. Capa semántica con al menos cinco métricas.
3. Harness: `AGENTS.md`, al menos una skill, MCP de solo lectura, hooks.
4. Un producto a elegir: NLQ gobernado, informe automático o pipeline de decisiones (clasificación/extracción con umbrales de confianza).
5. Suite de evals (mínimo 20 tareas, evaluadores de código y LLM-as-judge) en CI, más una prueba de seguridad.
6. Protocolo de manejo de una página: qué autoridad delega el producto (saber, hacer, decidir), qué libertad necesita, los modos de fallo observados en las trazas y el control aplicado a cada uno.

Rúbrica: corrección de datos (30%), diseño de contexto y harness (25%), evals y evidencia (25%), seguridad, gobierno y protocolo de manejo (10%), presentación (10%).

## Evaluación y certificación

- Ejercicios prácticos por clase (Clases 4-11).
- Proyecto final presentado en la Clase 12.
- Certificado al completar los ejercicios y el proyecto.

## Lecturas y referencias base

- Simon Willison, "I think 'agent' may finally have a widely enough agreed upon definition to be useful": https://simonw.substack.com/p/i-think-agent-may-finally-have-a
- Anthropic, "Effective context engineering for AI agents": https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic, "Equipping agents for the real world with Agent Skills" y especificación Agent Skills: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills · https://github.com/agentskills/agentskills
- Birgitta Böckeler (martinfowler.com), "Harness engineering for coding agent users": https://martinfowler.com/articles/harness-engineering.html
- Addy Osmani, "Agent Harness Engineering": https://addyosmani.com/blog/agent-harness-engineering/
- Hamel Husain y Shreya Shankar, "LLM Evals: Everything You Need to Know" y curso gratuito por email: https://hamel.dev/blog/posts/evals-faq/ · https://ai.hamel.dev/eval-course
- dbt Labs, ADE-bench y "Building a better data agent benchmark": https://github.com/dbt-labs/ade-bench · https://docs.getdbt.com/blog/building-a-better-data-agent-benchmark
- dbt Labs, dbt MCP server: https://github.com/dbt-labs/dbt-mcp
- Snowflake, servidor MCP gestionado, CoCo y funciones `AI_CLASSIFY` / `AI_EXTRACT`: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp · https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code · https://docs.snowflake.com/en/sql-reference/functions/ai_classify
- Databricks, Genie Code y AI Functions: https://docs.databricks.com/aws/en/genie-code/ · https://docs.databricks.com/aws/en/large-language-models/ai-functions
- Google Cloud, BigQuery MCP server y `AI.GENERATE`: https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp · https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-ai-generate
- MotherDuck, replicar Postgres a DuckDB/MotherDuck y pg_duckdb: https://motherduck.com/docs/key-tasks/data-warehousing/replication/postgres/ · https://github.com/duckdb/pg_duckdb
- TypeSafe AI, "Introducing System One Models & Jev": https://typesafe.ai/blog/introducing-system-one-models-and-jev
- OpenAI, Data agent en ChatGPT Work: https://openai.com/index/put-data-to-work
- OWASP Top 10 for LLM Applications (prompt injection, excessive agency).
- Daniel Kahneman, "Thinking, Fast and Slow" (origen de la metáfora Sistema 1 / Sistema 2).
