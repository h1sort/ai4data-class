# Temario: IA para Datos, de los chats a los agentes

## Sobre el curso

Curso práctico para perfiles de datos (analistas, ingenieros de datos, analytics engineers, científicos de datos y responsables de equipos de datos) que quieren trabajar con LLMs y agentes en producción: preparación de contexto, configuración del harness, conectar agentes a sus sistemas de datos con garantías y medir si funcionan.

Doce sesiones en cinco bloques: fundamentos y casos reales, interfaces de trabajo con agentes, construcción de productos de datos, evals y seguridad, y proyecto final.

La tesis del curso: la IA ha hecho que producir análisis cueste casi cero, pero no ha hecho más barato ponerse de acuerdo en qué es verdad. El trabajo del equipo de datos pasa de producir análisis a codificar su criterio (definiciones, contexto, controles, evals) en infraestructura para que cualquier agente, en cualquier interfaz, llegue a la misma respuesta correcta.

### Resultados de aprendizaje

Al terminar el curso serás capaz de:

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

- Entorno: terminal, VS Code, Cursor o Devin, git, `uv` para python.
- Datos: Postgres (local o Docker), DuckDB, cuenta gratuita de MotherDuck. Opcional: trial de Snowflake, BigQuery sandbox o Databricks Free Edition.
- Modelos y agentes: ideal al menos una suscripción a Claude, ChatGPT o Gemini; un agente de código (Claude Code, Codex CLI o Gemini CLI). Se indican alternativas gratuitas y modelos locales (Ollama) donde es viable.

## Mapa del curso

| Clase | Título | Bloque |
| --- | --- | --- |
| 1 | Cómo ha cambiado el rol de datos en la era IA | 1. La era agéntica de los datos |
| 2 | De OLTP a un Data Warehouse con agentes | 1. La era agéntica de los datos |
| 3 | Flujos agénticos de datos | 1. La era agéntica de los datos |
| 4 | LLMs vía chat para datos: de prompts a contexto | 2. Interfaces: chats, copilotos y harnesses |
| 5 | Copilotos y agentes de código para datos | 2. Interfaces: chats, copilotos y harnesses |
| 6 | Tu harness de datos: AGENTS.md, skills, MCP, hooks y subagentes | 2. Interfaces: chats, copilotos y harnesses |
| 7 | Contexto para agentes: capa semántica, metadatos y RAG | 3. Construir: contexto, APIs, decisiones y productos |
| 8 | APIs, salidas estructuradas y modelos de decisión | 3. Construir: contexto, APIs, decisiones y productos |
| 9 | IA dentro del warehouse y productos de datos | 3. Construir: contexto, APIs, decisiones y productos |
| 10 | Evals I: analizar y medir sistemas de IA sobre datos | 4. Confiar: evals, seguridad y operación |
| 11 | Evals II, seguridad y operación | 4. Confiar: evals, seguridad y operación |
| 12 | Proyecto final y futuro | 5. Proyecto final |

## Bloques temáticos

### Bloque 1: La era agéntica de los datos (Clases 1-3)

- Cuatro eras del stack de datos, por qué el consenso es ahora el recurso escaso y qué habilidades se demandan.
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

- Capa semántica, metadatos y artefactos legibles por agentes como contexto; context engineering y RAG aplicados a datos.
- APIs de LLMs, tool calling y salidas estructuradas. De strings a decisiones tipadas: modelos de decisión (System One Models, ej. Jev).
- Funciones de IA en SQL (Snowflake, Databricks, BigQuery) y agentes gestionados por la plataforma.
- Arquitectura de referencia y construcción de productos de datos: NLQ gobernado, informes automáticos, pipelines de decisión.

### Bloque 4: Confiar: evals, seguridad y operación (Clases 10-11)

- Ciclo Analizar → Medir → Mejorar (Hamel Husain y Shreya Shankar) aplicado a datos: trazas, error analysis, evaluadores de código y LLM-as-judge.
- Evals sobre la respuesta y sobre el camino; tasa de divergencia de consenso entre interfaces.
- Suites de tareas al estilo ADE-bench, evals en CI/CD, monitorización en producción.
- Seguridad de agentes de datos: prompt injection vía datos, tool poisoning, mínimo privilegio, auditoría.
- Coste, adopción en equipos y nuevos roles.

### Bloque 5: Proyecto final (Clase 12)

- Producto de datos agéntico con evals, de la fuente OLTP a la interfaz, presentado y defendido.

## Clases

Cada clase incluye ejercicio práctico y lecturas. Las herramientas son, en su mayoría, gratuitas o con capa gratuita. El repositorio del curso incluye un dataset OLTP de ejemplo que se reutiliza de la Clase 2 al proyecto final.

### Clase 1: Cómo ha cambiado el rol de datos en la era IA (Bloque 1)

Objetivo: entender qué ha cambiado de verdad, qué se pide ahora y el mapa mental que usaremos el resto del curso.

- Repaso de cómo ha cambiado el rol: cuatro eras, cuatro recursos escasos
  - ~2013, stack pre-moderno: datos en silos que no se podían cruzar, sin soporte para JSON, cien millones de filas tumbaban el servidor. El límite era qué podías consultar.
  - ~2016, cloud data warehouse: todos los datos de la empresa en un sitio, cómputo elástico, semiestructurado nativo. El límite era llegar a todo.
  - ~2020, Modern Data Stack y Reverse ETL: datos de cualquier SaaS con un clic, y los resultados de vuelta a los sistemas operativos. De reportar a operar.
  - ~2026, stack post-IA: producir un análisis o un dashboard cuesta casi cero, y cualquiera puede hacerlo con una pregunta distinta, una definición distinta y llegar a un número distinto. El recurso escaso es el consenso.
  - Qué se ha comoditizado (código repetitivo, EDA inicial, dashboards, documentación) y qué se ha revalorizado (modelado, semántica, gobierno, criterio).
  - De escribir SQL y pipelines a mano a especificar, revisar y orquestar trabajo hecho por agentes; de producir análisis a codificar tu criterio en infraestructura para que cualquier agente responda bien sin ti en la sala.
  - El dashboard deja de ser un destino que se abre los lunes y pasa a ser un repositorio de hechos y definiciones que los agentes descomponen y recombinan para quien pregunta.
- Nuevas habilidades en demanda
  - Los dos trabajos del equipo de datos hoy: que todo el mundo pueda construir con datos e IA de forma correcta e independiente, y construir y defender la realidad única sobre la que opera la empresa.
  - Context engineering: preparar metadatos, definiciones y ejemplos para que el modelo acierte.
  - Configurar y gobernar agentes: ficheros de instrucciones, skills, MCP, permisos, revisión.
  - Evals: saber medir si un sistema de IA sobre datos funciona.
  - Modelado semántico y calidad de datos: la IA amplifica lo bueno y lo malo de tu warehouse.
- Conceptos fundamentales para el curso
  - OLTP vs OLAP: por qué tu base de datos de producción no es donde debe leer un agente.
  - Data Warehouses vs Data Lakes vs Databases (y lakehouse): qué guarda cada uno, para quién y a qué coste.
  - Vocabulario mínimo de IA: LLM, ventana de contexto, tool calling, agente, MCP, skill, harness.
- ¿Qué sistemas están preparados para los agentes?
  - Criterios: catálogo y metadatos consultables, capa semántica, control de acceso (RBAC, filas y columnas), auditoría, endpoint MCP o API de agentes, funciones de IA en SQL, aislamiento de coste y carga.
  - Operable por cualquier agente: API y MCP como interfaz de primera clase, no una UI cerrada con su propio asistente. "No quiero usar tu agente; quiero usar mi agente para usar tu herramienta."
  - Por familia: Snowflake (Cortex, MCP gestionado, CoCo), Databricks (Unity Catalog, Genie), BigQuery (MCP remoto, AI.GENERATE), DuckDB/MotherDuck (ligero, local-first), Postgres (pg_duckdb, MCP de solo lectura).
- ¿Cuándo elegir cada uno?
  - Matriz de decisión: volumen, gobierno, presupuesto, tamaño de equipo, latencia y dónde ya viven tus datos.
- Qué stacks de datos puedes usar para trabajar con LLMs
  - Local y gratis: Postgres o CSV/Parquet → DuckDB → agente de código con MCP.
  - Cloud ligero: MotherDuck + dbt + agente de código.
  - Enterprise: Snowflake, Databricks o BigQuery con sus agentes nativos y MCP.
- Demo de cierre: un agente respondiendo preguntas sobre un warehouse local vía MCP. Puente a la Clase 2: cómo se construye eso desde cero.

### Clase 2: De OLTP a un Data Warehouse con agentes (Bloque 1)

Objetivo: ver de principio a fin una migración didáctica de una base de datos transaccional a un sistema preparado para analítica y agentes, construida con ayuda de agentes y después usada por agentes. Cubre: Migración → Uso.

- Punto de partida: una aplicación con Postgres (OLTP), esquema normalizado y sin documentación.
- Migración
  - Diseño del destino: DuckDB/MotherDuck por ser gratuito y didáctico; el patrón es el mismo en Snowflake, BigQuery o Databricks.
  - Extraer y cargar con un agente de código: `ATTACH` de Postgres desde DuckDB, `CREATE OR REPLACE TABLE ... AS SELECT`, cargas idempotentes y re-ejecutables.
  - Modelado analítico asistido: de tablas normalizadas a un modelo en estrella o capa "silver" con nombres predecibles y grano explícito.
  - Documentación generada y revisada: descripciones de tablas y columnas que serán el contexto de los agentes.
- Apoyado de agentes para el desarrollo
  - Cómo pedir el trabajo: plan → ejecutar → revisar. Qué revisar siempre y qué automatizar con tests de datos.
  - Errores típicos de los agentes en migraciones (tipos, zonas horarias, claves duplicadas, filtros silenciosos) y cómo detectarlos.
- Cómo trabajar con agentes ya en el data warehouse
  - Exponer el warehouse por MCP con un rol de solo lectura.
  - Preguntar en lenguaje natural desde el chat o desde el agente de código; leer el SQL generado; iterar el contexto hasta que acierte.
  - Primer contacto con la capa semántica: por qué "ingresos" necesita una definición antes de que nadie pregunte por ellos.
- Demo de cierre: la misma pregunta que el agente respondía mal al principio, respondida bien solo por mejorar el contexto. Puente a la Clase 3: qué pasa cuando esto se aplica a casos reales.

### Clase 3: Flujos agénticos de datos (Bloque 1)

Objetivo: charla entre motivacional y práctica con casos que el instructor ha aplicado en su carrera con IA y datos, en banca y en otros sectores, siempre con el mismo marco para que sean replicables.

- Marco de cada caso
  1. Contexto y problema: qué dolía, a quién y cuánto costaba.
  2. Cómo lo evaluamos: criterio de éxito, riesgos, qué no podía salir mal, dónde tenía que estar el humano.
  3. Solución aplicando IA: arquitectura, herramientas, nivel de autonomía.
  4. Resultado y lecciones: qué funcionó, qué no y qué haríamos distinto hoy.
- Casos (banca y otros sectores)
  - Clasificación y enriquecimiento de registros con texto libre a escala.
  - Documentar y migrar tablas y procesos legacy con agentes.
  - Conciliaciones y detección de anomalías en reporting.
  - Informes recurrentes con narrativa generada y cifras verificadas.
  - Anti-casos: dónde la IA no compensó y por qué.
- Patrones que se repiten
  - Humano en el bucle donde el error cuesta; automatización total donde el resultado se puede verificar.
  - Decisiones estructuradas antes que texto libre.
  - El contexto importa más que el modelo.
- Cierre del bloque: qué construiremos en las Clases 4-12 y cómo encaja con los casos vistos.

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
  - Conectar el chat de un vendedor directamente a datos crudos, sin capa semántica en medio, es rápido para una persona y una crisis de reproducibilidad para la empresa: cada corrección que haces enseña al vendedor sobre tu negocio en lugar de arreglar tu stack. Lo resolvemos en la Clase 7.
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
  - Solo lectura por defecto contra bases de datos; credenciales separadas para el agente.
  - Tests de datos como criterio de "hecho" (dbt tests, assertions).
  - Revisión de SQL generado: grano, joins, filtros de fecha, nulos, dobles conteos, tablas equivocadas.
- Casos de uso: modelos dbt, pipelines (Airflow, Dagster), depurar queries lentas, migrar dialectos SQL, documentación masiva.
- Ejercicio: con un agente de código, construir y testear un modelo dbt sobre el warehouse de la Clase 2 y revisar el diff como si fuera de un compañero.

### Clase 6: Tu harness de datos: AGENTS.md, skills, MCP, hooks y subagentes (Bloque 2)

- Agente = Modelo + Harness. El harness es todo lo que no es el modelo: prompts de sistema, ficheros de instrucciones, herramientas y MCP, skills, hooks, sandbox, orquestación, permisos y observabilidad.
- Guías (feedforward) vs sensores (feedback): anticipar errores vs detectarlos y dejar que el agente se corrija. Computacionales (tests, linters, dbt tests) vs inferenciales (LLM-as-judge, revisión).
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
- Context engineering aplicado: el menor conjunto de tokens de alta señal; recuperación just-in-time frente a cargar todo; compactación; "context rot".
- RAG hoy en datos: recuperación sobre documentación, tickets y definiciones; búsqueda vectorial en el warehouse (Cortex Search, Vector Search) como herramienta del agente, no como sustituto del SQL.
- Metadatos como producto: catálogo, linaje, owners, frescura. Todo lo que el agente puede consultar antes de responder.
- Artefactos legibles por agentes: cada producto de datos (dashboard, modelo, análisis) publicado también para máquinas: descriptor en markdown, SQL recuperable, valores cacheados, owners y cómo se relaciona con el resto del modelo. El equivalente a un `llms.txt` por producto de datos, para que tu respuesta aparezca cuando alguien le pregunta a su agente.
- Contexto agnóstico al agente: definiciones y conectores headless para que un compañero, un agente de código, una herramienta de BI o un bot de Slack den la misma respuesta. Modelos, harnesses e interfaces cambian cada trimestre; no encierres la inteligencia de tu empresa en la interfaz de un vendedor.
- Por qué la capa semántica llegó al comité de dirección: cada "esto se ve raro" y cada aclaración de una métrica es aprendizaje que compone dentro de tus cuatro paredes o dentro de las de otro. La capa semántica es donde se acumula el conocimiento tribal ("el TPV excluye devoluciones después del día 45") para que cada pregunta, agente y persona nueva empiece más lista que la anterior.
- Ejercicio, test de consenso: definir cinco métricas en una capa semántica y preguntar por cada una desde chat, agente de código y API. Contar cuántas respuestas distintas salen. Si es más de una, leer las trazas, arreglar el contexto y repetir hasta que la interfaz no cambie la respuesta.

### Clase 8: APIs, salidas estructuradas y modelos de decisión (Bloque 3)

- APIs de LLMs (OpenAI, Anthropic, Google y abiertos vía proveedores): SDKs, streaming, tool calling, salidas estructuradas con JSON Schema, batch, caché de prompts. Coste y latencia reales.
- Patrones para datos: enriquecimiento por filas (clasificar, extraer, normalizar), generación de SQL con validación, resúmenes de tablas, agentes con herramientas propias.
- De strings a decisiones: cuando lo que necesitas no es texto sino una decisión tipada (categoría, score, ruta, campo extraído) que el software use directamente.
  - "Smart if-statements" en pipelines: clasificar, enrutar, puntuar, extraer y ramificar donde una regla a mano es frágil.
  - Umbrales por confianza: automatizar por encima, revisión humana por debajo.
- Modelos de decisión / System One Models (ej. Jev, de TypeSafe AI): estado no estructurado de entrada, valores tipados con probabilidades calibradas de salida; sin errores de tipo; latencias de decenas o cientos de milisegundos y coste órdenes de magnitud menor. Casos: map-reduce sobre grandes volúmenes, tiempo real, verificar, juzgar y guardrails. Sistema 1 (rápido, estructurado) vs Sistema 2 (LLM con razonamiento): cuándo usar cada uno y cómo combinarlos.
- Fine-tuning y modelos pequeños especializados: cuándo compensan frente a prompts más contexto.
- Ejercicio: pipeline que clasifica y extrae campos de 10.000 registros de texto libre con (a) LLM y salidas estructuradas y (b) modelo de decisión. Comparar coste, latencia, acuerdo entre ambos y calibración.

### Clase 9: IA dentro del warehouse y productos de datos (Bloque 3)

- Funciones de IA en SQL: Snowflake (`AI_CLASSIFY`, `AI_EXTRACT` con scores, `AI_COMPLETE`), Databricks (`ai_query` y funciones por tarea), BigQuery (`AI.GENERATE` con `output_schema`). Enriquecer sin sacar los datos del warehouse; gobierno y coste.
- Más allá del SQL: preguntas que no tienen forma de SQL (llamadas, tickets, correos, contratos). Pre-modelar por significado igual que se modela por forma: un etiquetador de IA pasa una vez, offline, sobre todo el corpus y escribe columnas estructuradas (`motivo_perdida`, `tipo_objecion`, `competidor_mencionado`) que cualquier análisis futuro puede filtrar y agrupar. La taxonomía sale de observar qué preguntan los usuarios; las funciones de IA en SQL y los modelos de decisión de la Clase 8 son la herramienta.
  - Prompt versionado en tu infraestructura y taxonomía mantenida por el equipo, revisada con cada error. Anti-patrón: delegar el etiquetado a un vendedor cuya distribución cambia sin aviso y que no puedes reproducir, depurar ni revertir.
- Agentes gestionados por la plataforma: Snowflake Cortex Agents y Snowflake Intelligence, Databricks Genie, agentes de datos en BigQuery. Exponerlos por MCP. Cuándo usarlos y cuándo construir el tuyo.
- Construir productos de datos con LLMs
  - NLQ sobre datos gobernados con capa semántica.
  - Informes automáticos con narrativa generada y cifras verificadas contra el warehouse.
  - Agentes de mantenimiento: documentación, linaje, detección de anomalías, optimización de queries.
  - Arquitectura de referencia: fuente → warehouse → capa semántica → MCP/API → agente → interfaz (Streamlit o app) → trazas.
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
- Evaluar la respuesta y la evidencia: un número correcto por un camino imperfecto vale menos, y se rompe con el siguiente modelo, que un número correcto por el camino bendecido (leer el doc de dominio, usar la vista semántica, ejecutar el SQL canónico). Normalizar las trazas en pasos (`READ_DOMAIN_DOC`, `READ_SEMANTIC_VIEW`, `EXECUTE_SQL`, `SYNTHESIZE_ANSWER`) para poder afirmar sobre el proceso, no solo sobre el resultado.
- Asume que el modelo nunca se equivoca: tu contexto está subespecificado. La taxonomía de fallos se quema arreglando docs, modelos y definiciones, no esperando al siguiente modelo frontier.
- Ejercicio: 30 trazas del producto de la Clase 9 → taxonomía de fallos → tres evaluadores, al menos uno sobre el camino y no sobre la respuesta.

### Clase 11: Evals II, seguridad y operación (Bloque 4)

- Evals en CI/CD: suite de tareas que corre al cambiar prompt, modelo, skill o servidor MCP; comparar experimentos; evitar sobreajustar a la suite. Snapshot del sistema en cada ejecución (modelo, prompt, tools, código, corpus de evaluación y hash del conocimiento disponible) para poder reproducir un fallo semanas después.
- Tasa de divergencia de consenso: porcentaje de preguntas cuya respuesta o cuyo camino cambia según la interfaz o el modelo desde el que se pregunta. Para las métricas que mira dirección cada semana, el objetivo es cero.
- Monitorización en producción: drift, coste, latencia, tasa de intervención humana.
- Seguridad de agentes de datos
  - Prompt injection vía datos (filas, tickets, documentos) y tool poisoning (descripciones de tools MCP).
  - Exceso de agencia: mínimo privilegio, roles de solo lectura, seguridad a nivel de fila y columna, allowlists de queries, auditoría, aprobación humana para escrituras.
  - Red-teaming básico del producto antes que lo hagan otros.
- Coste: tokens, caché, modelos pequeños o de decisión para lo repetitivo, batch.
- Equipos y adopción: quién mantiene el AGENTS.md, las skills y la capa semántica; políticas de uso; cómo medir productividad sin engañarse.
- Ejercicio: pipeline de CI con evals y un intento de inyección contra el producto propio. Corregir y volver a pasar la suite.

### Clase 12: Proyecto final y futuro (Bloque 5)

- Presentaciones del proyecto final: arquitectura, harness, evals y demo en vivo.
- Debate: agentes de plataforma vs propios, modelos de decisión, estándares (MCP, Agent Skills), el rol del profesional de datos en dos años: cuando dirección "lea el dashboard" sin abrirlo nunca, el trabajo es que el significado sobreviva a la edición.
- Recap de herramientas y lecciones. Certificación y cierre.

## Proyecto final

Producto de datos agéntico con evals, de extremo a extremo:

1. Fuente OLTP → warehouse (DuckDB/MotherDuck o cloud) con modelo analítico documentado.
2. Capa semántica con al menos cinco métricas.
3. Harness: `AGENTS.md`, al menos una skill, MCP de solo lectura, hooks.
4. Un producto a elegir: NLQ gobernado, informe automático o pipeline de decisiones (clasificación/extracción con umbrales de confianza).
5. Suite de evals (mínimo 20 tareas, evaluadores de código y LLM-as-judge) en CI, más una prueba de seguridad.
6. Test de consenso: las cinco métricas preguntadas desde al menos dos interfaces distintas, con la tasa de divergencia medida y cada divergencia explicada y corregida.

Rúbrica: corrección de datos (30%), diseño de contexto y harness (25%), evals y evidencia (25%), seguridad y gobierno (10%), presentación (10%).

## Evaluación y certificación

- Ejercicios prácticos por clase.
- Proyecto final presentado en la Clase 12.
- Certificado al completar los ejercicios y el proyecto.

## Lecturas y referencias base

- Ian Macomber, "The Shape and Feel of the Post-AI Data Stack": https://www.iandmacomber.com/blog/post-ai-data-stack/
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
