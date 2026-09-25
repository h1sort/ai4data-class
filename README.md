# IA para datos · materiales de clase

Curso de Código Facilito: de los chats a los agentes. Los materiales de Clase 1 y Clase 2 están aquí para consulta y práctica.

## Clase 2 · de OLTP a un data warehouse, con agentes

- [Diapositivas](slides/clase-02.html) — ábrelas en el navegador; flechas o espacio para avanzar, `R` para revelar resultados tras la predicción.
- [Prompts de la demo](demos/clase-02-prompts.md) — secuencia para Codex, con límites y Plan B por paso.
- [Resultados agregados del ensayo](demos/clase-02-rehearsal-results.md) — cifras sintéticas que aparecen en las diapositivas; no son resultados de la audiencia real.
- [Pipeline D1 → Databricks → Jev](demos/clase-02/pipeline/README.md) — código de referencia, orden de ejecución y modelo de datos.
- [Momento de escala SQLite vs DuckDB](demos/clase-02/scale/data/README.md) — datos NYC TLC y scripts en `demos/clase-02/scale/`.
- [Configuración Databricks](demos/clase-02/databricks/00_setup.sql) y [plantilla de credenciales](.env.example).
- [Encuesta de Clase 2](https://h1sort.com/p/8P56ZUVE9Q).

La ejecución de la demo requiere tus propias credenciales de Cloudflare, Databricks y TypeSafe. El pipeline espera un checkout de [`h1sort-website`](https://github.com/h1sort/h1sort-website) junto a este repositorio para ejecutar `wrangler`; puedes definir `D1_REPO` si está en otra ruta. Copia `.env.example` a `.env` y completa las variables sin subir `.env` a Git. Los archivos de datos grandes, extracciones y CSV con respuestas individuales se generan localmente y están ignorados por Git.

## Clase 1 · la verdad y el consenso

- [Diapositivas](slides/clase-01.html)
- [Prompts de la encuesta](demos/clase-01-poll-prompts.md)
- [Transcripción](slides/clase-01-transcript.md)
- [Encuesta de Clase 1](https://h1sort.com/p/JFQES4AF97)
