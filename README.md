# IA para datos · materiales de clase

Curso de Código Facilito: de los chats a los agentes. Los materiales de Clase 1 y Clase 2 están aquí para consulta y práctica.

## Clase 2 · de la transacción a la decisión

- [Diapositivas](slides/clase-02.html): encuesta, presentación, OLTP/OLAP, ETL, analítica y clasificación.
- [Guion de presentación](demos/clase-02-prompts.md): comandos por diapositiva, prompts y alternativas.
- [Notebooks Databricks](demos/clase-02/notebooks/README.md): negocio, ML y comparación LLM/Jev; preparación de Genie.
- [Contrato de datos](demos/clase-02/data-contract.md) y [pipeline](demos/clase-02/pipeline/README.md).
- [Dataset NYC TLC](demos/clase-02/scale/data/README.md): SQLite y DuckDB sobre 11,198,026 viajes.
- [Ensayo fresco](demos/clase-02/fresh-rehearsal.md): comandos, conteos y tiempos verificados; indica lo que falta validar.
- [Ensayo anterior](demos/clase-02-rehearsal-results.md): resultados históricos, separados de la audiencia real.
- [Encuesta de hoy](https://h1sort.com/p/8P56ZUVE9Q).

Desde la raíz del repositorio:

```bash
uv run demos/clase-02/live.py preflight --remote
uv run demos/clase-02/live.py poll
uv run demos/clase-02/live.py scale --engine sqlite
uv run demos/clase-02/live.py scale --engine duckdb
uv run demos/clase-02/live.py etl --dataset class1
uv run demos/clase-02/live.py etl --dataset class2
```

La ETL termina después del modelado y las pruebas; la clasificación se ejecuta en los notebooks. `preflight` comprueba herramientas, archivos y configuración; `--remote` añade consultas de lectura a D1 y Databricks. El ensayo de notebooks, Jev y Genie se documenta por separado.

Necesitas `uv`, los CLIs indicados por preflight y tus credenciales de Cloudflare, Databricks y TypeSafe. El pipeline usa el checkout hermano [`h1sort-website`](https://github.com/h1sort/h1sort-website), configurable con `D1_REPO`, para ejecutar Wrangler. Copia [.env.example](.env.example) a `.env` y completa las variables sin subir claves a Git. Las extracciones, bases de taxi y respuestas individuales se generan localmente y están ignoradas por Git.

## Clase 1 · la verdad y el consenso

- [Diapositivas](slides/clase-01.html)
- [Prompts de la encuesta](demos/clase-01-poll-prompts.md)
- [Transcripción](slides/clase-01-transcript.md)
- [Encuesta de Clase 1](https://h1sort.com/p/JFQES4AF97)
