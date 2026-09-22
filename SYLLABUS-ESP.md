# Temario

## Bloques temáticos

### Bloque 1: Fundamentos Teóricos de LLMs en Análisis de Datos (Semanas 1-2)

- Conceptos base: IA Generativa, LLMs, token embeddings, atención, transformers aplicados a datos.
- Cómo funcionan LLMs para datos: capacidades en SQL/Python, limitaciones (hallucinations en insights), ventajas/desventajas.
- Modelos especializados (ej. para SQL) vs. generales (ej. GPT-4, Claude).
- Principios base: estadística general, calidad de datos para maximizar IA.
- Referencia: Análisis de modelos para datos (ej. integraciones como Snowflake Cortex).

### Bloque 2: LLMs vía Chat y RAG para Datos (Semanas 3-4)

- Ingeniería de prompts para datos: tácticas en chats (ej. para interpretación de datasets, traducción de insights).
- RAG: Integrar datasets en LLMs (ej. embeddings para retrieval en data lakes), con privacidad.
- Uso en datos: análisis exploratorio automatizado, generación de resúmenes, detección de outliers.
- Herramientas: Chats generales, customizaciones para datasets (ej. custom GPTs para queries NL).
- Diferencias locales vs. nube, seguridad en datos sensibles.

### Bloque 3: LLMs vía Copilotos y CLIs para Datos (Semanas 5-6)

- Copilotos en entornos de datos: GitHub Copilot en Jupyter/VS Code para código SQL/Python, debugging.
- CLIs: Herramientas como Pandas AI o SQL agents para terminal.
- Mejores prácticas: generación de código para transformaciones, autogenerar DAGs (ej. Airflow con prompts).
- Niveles de autonomía: copilotos vs. agentes para ETL, vibe querying en datos.
- Integración en notebooks: Jupyter/Marimo AI extensions.

### Bloque 4: LLMs vía APIs y Productos en Data Warehouses (Semanas 7-8)

- APIs de LLMs (OpenAI, Anthropic): conexión para datos, SDKs.
- Construir productos: apps de datos con LLMs (ej. reportes automatizados, NLQ sobre dashboards).
- LLMs en data warehouses: Snowflake Cortex para insights automáticos, optimización de queries, explicación de linaje; comparativas con BigQuery ML, Azure Synapse.
- Agentes para datos: limpieza de columnas, sugerencias de optimización.
- Privacidad: datos propios en warehouses, fine-tuning básico para datasets.

### Bloque 5: Evaluaciones (Evals) para Sistemas de IA en Datos (Semanas 9-10)

- Inspirado en Hamel Husain: tipos de evals (Level 1: unit tests para queries; Level 2: human/model eval para insights; Level 3: A/B para reportes).
- Construir evals domain-specific: assertions para datos, logging traces (ej. en datasets), data curation.
- Eval para RAG en datos y fine-tuning: síntesis de test data, debugging de pipelines.
- Métricas: correlación human-model en interpretaciones, tracking progreso en warehouses.

### Bloque 6: Flujos Avanzados, Equipos y Proyecto Final (Semanas 11-12)

- IA en equipos de datos: documentación automática de tablas/flujos, generación de visualizaciones con prompts.
- Data warehouses avanzados: Uso de Cortex para crear visualizaciones, generar insights, transformación de datasets.
- Nube con IA: Integraciones en Snowflake, AWS Athena, etc.
- Proyecto final: Producto de datos con LLMs (ej. dashboard NLQ) + evals.
- Futuro de IA en datos: debates, estrategias de adopción.

## Clases

Incluyen lecturas adicionales. Herramientas, en su mayoría, gratuitas (ChatGPT free, Jupyter). Recomendado: Entorno (Jupyter/VS Code), modelos (Claude Sonnet por defecto, comparativas), acceso a data warehouses trial (ej. Snowflake free tier).

### Clase 1: Fundamentos Teóricos de LLMs en Datos (Bloque 1)

- IA Generativa y LLMs: embeddings, atención para datos.
- Cómo generan insights: pros/cons, modelos clave para datos.
- Futuro de análisis con IA; principios atemporales.
- Ejercicio: Generar resumen simple de dataset vía chat.
- Lectura: Intro a Snowflake Cortex.

### Clase 2: Características y Modelos de LLMs para Datos (Bloque 1)

- Análisis de modelos: data-specific vs. generales, integraciones warehouses.
- Limitaciones: hallucinations en datos.
- Configuración entorno: locales (Ollama para datos) vs. nube.
- Ejercicio: Comparar outputs en SQL/Python para datasets.
- Debate: ¿Reemplazará IA a analistas?

### Clase 3: LLMs vía Chat e Ingeniería de Prompts para Datos (Bloque 2)

- Prompts avanzados: chain-of-thought para interpretación de datasets.
- Uso en chats: análisis exploratorio, traducción de insights para stakeholders.
- Añadir contexto: por dataset/query.
- Ejercicio: Tarea de datos con prompts (ej. detección outliers).
- Herramientas: ChatGPT/Claude para datasets.

### Clase 4: Introducción a RAG con LLMs para Datos (Bloque 2)

- RAG: embeddings para retrieval en datasets, custom queries.
- Privacidad: datos locales en RAG.
- Aplicación: Generar resúmenes, insights automáticos.
- Ejercicio: Crear RAG para queries NL en dataset.
- Lectura: RAG en data contexts (Hugging Face).

### Clase 5: LLMs vía Copilotos en Entornos de Datos (Bloque 3)

- Integración Copilot: en Jupyter para SQL/Python, debugging.
- Mejores prácticas: generación código para transformaciones.
- Comparativa: Jupyter AI extensions.
- Ejercicio: Desarrollar script de limpieza con Copilot.
- Seguridad: validar outputs en datos.

### Clase 6: LLMs vía CLIs y Agentes para Datos (Bloque 3)

- CLIs: Pandas AI, SQL agents para terminal.
- Agentes vs. copilotos: autonomía en ETL, autogenerar DAGs.
- IA en pipelines: sugerencias optimización.
- Ejercicio: Pipeline CLI con agentes.
- Debate: Autonomía en equipos de datos.

### Clase 7: LLMs vía APIs - Fundamentos para Datos (Bloque 4)

- APIs: OpenAI/Anthropic para datos, SDKs.
- Construir apps: integrar LLMs en pipelines datos.
- Local vs. nube: pros/cons para warehouses.
- Ejercicio: API para generador de insights.
- Privacidad: manejo datasets.

### Clase 8: Productos en Data Warehouses con LLMs (Bloque 4)

- Integraciones: Snowflake Cortex para NLQ, visualizaciones con prompts.
- Producto real: dashboard con generación reportes automáticos.
- Agentes: explicación linaje, documentación tablas.
- Ejercicio: Prototipo en Snowflake con Cortex.
- Lectura: Casos Hamel Husain adaptados a datos.

### Clase 9: Introducción a Evals para LLMs en Datos (Bloque 5)

- Tipos: Level 1 (unit tests para queries datos).
- Inspirado en Hamel: scoped tests, synthetic data para datasets.
- Logging traces: en data flows.
- Ejercicio: Crear unit tests para outputs LLM en datos.
- Tracking: métricas en tools como Metabase.

### Clase 10: Evals Avanzadas y Human/Model Eval para Datos (Bloque 5)

- Level 2: human eval para insights, model critiques.
- Correlación: en interpretaciones datos; A/B para reportes.
- Eval RAG/fine-tuning: curation para datasets.
- Ejercicio: Evaluar producto Clase 8.
- Debugging: traces para issues en warehouses.

### Clase 11: IA en Equipos de Datos y Warehouses Avanzados (Bloque 6)

- Equipos: documentación IA de flujos, generación visualizaciones.
- Warehouses: Cortex para outliers, optimización queries.
- Nube: Integraciones BigQuery, Azure.
- Ejercicio: Integrar warehouse en producto.
- Estrategias adopción.

### Clase 12: Proyecto Final y Futuro de IA en Datos (Bloque 6)

- Proyecto: Producto datos con LLMs + evals (ej. NLQ dashboard).
- Presentaciones: flujos, evals.
- Futuro: debates expertos, proyecciones warehouses AI.
- Recap: herramientas, lecciones.
- Certificación y cierre.
