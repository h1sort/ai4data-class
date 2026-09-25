# Clase 2 demo data contract

This contract is shared by the live launcher, pipeline, scale demos, and
notebooks. Commands below are run from the repository root. Poll definitions,
options, URLs, and QR assets are immutable for this rebuild. The ETL only reads
D1; it never writes to either real or rehearsal polls.

## Stage commands

The integration entry point dispatches to these underlying commands:

```bash
bash demos/clase-02/pipeline/poll.sh
bash demos/clase-02/scale/run_engine.sh --engine sqlite
bash demos/clase-02/scale/run_engine.sh --engine duckdb
bash demos/clase-02/pipeline/etl_only.sh --dataset class1
bash demos/clase-02/pipeline/etl_only.sh --dataset class2
```

`poll.sh` reads the live Clase 2 confidence poll and groups votes by option.
It prints the current result count; it does not fabricate responses if the
poll is still empty. The same bounded aggregate can be issued through the D1
MCP `d1_database_query` tool using the query in
[`pipeline/poll_aggregate.sql`](pipeline/poll_aggregate.sql); this provides the
CLI/MCP hand-off for the agent demo.

The NYC scale query is deliberately available as one invocation per engine.
Both engines use the same [`scale/query.sql`](scale/query.sql) against the
same 11,198,026 Jan–Mar 2025 trip rows. The row-store stand-in is SQLite; the
analytical copy is DuckDB. Each stage runner executes the query once and
prints its actual elapsed time. Earlier rehearsal times are historical, not
promised timings.

## Source and write boundaries

| Dataset | D1 group | Databricks target |
|---|---|---|
| Class 1 | `JFQES4AF97` | `workspace.ai4data` |
| Class 2 | `8P56ZUVE9Q` | `workspace.ai4data` |
| Class 2 rehearsal | `YWE57U6B8U` plus its separate rehearsal Class 1 group | `workspace.ai4data_rehearsal` only |

The real Class 1 ETL reads all polls and responses in that group, then builds
the curated C1 tables. The Class 2 ETL reads the C2 group and its C1 companion
for the existing optional role join. Each run replaces only its selected
raw/model tables and can be repeated safely. The legacy `run_all.sh` remains
the full classifier rehearsal pipeline; the stage ETL entry point stops after
extract, load, model, and reconciliation checks. It does not invoke paid
classifiers.

Raw D1 landing tables are written only in `workspace.ai4data_raw`:

| Table | Columns |
|---|---|
| `raw_poll_groups` | `id`, `title`, `code`, `created_at` |
| `raw_polls` | `id`, `group_id`, `code`, `question`, `kind`, `max_length`, `status`, `created_at`, `updated_at`, `opened_at`, `closed_at` |
| `raw_poll_options` | `id`, `poll_id`, `label`, `position` |
| `raw_poll_votes` | `id`, `poll_id`, `option_id`, `voter_hash`, `created_at` |
| `raw_poll_text_answers` | `id`, `poll_id`, `voter_hash`, `body`, `created_at` |

The loader supplies these schemas explicitly so empty answer files still
create stable tables. `voter_hash` is an internal join key only: don't print
it, export it to notebook charts, or expose it in an aggregate.

## Class 1 analytics tables

The real Class 1 ETL produces these tables in `workspace.ai4data`:

| Table | Grain and columns |
|---|---|
| `c1_dim_participante` | One row per distinct Class 1 respondent: `participant_key` (internal voter hash), `n_preguntas_respondidas`, `respondio_todas`. |
| `c1_fct_respuestas` | One row per respondent and poll: `participant_key`, `poll_id`, `poll_code`, `pregunta`, `tipo`, `respuesta`, `posicion_opcion`, `created_at`. The key supports role/usage/trust cross-tabs; notebooks must aggregate before displaying. |
| `c1_vw_resumen_respuestas` | One row per question and answer option: `poll_code`, `pregunta`, `tipo`, `respuesta`, `posicion_opcion`, `n_respuestas`, `n_participantes`, `denominador_pregunta`, `porcentaje`. It contains no participant key and no individual answer text. `n_respuestas` counts answer rows; `n_participantes` counts distinct people who chose that option; `denominador_pregunta` counts people who answered the question; `porcentaje` divides option participants by that question's denominator. |

Poll IDs, question wording, options, and option positions are loaded from D1
metadata at runtime. Don't hard-code question IDs or infer question meaning
from position. The view is the safe source for dashboards and Genie. For
cross-tabs, notebooks can join `c1_fct_respuestas` on `participant_key`, then
group the results before display; do not show the key itself.

The six current Class 1 polls are choice questions. A fresh read-only D1
inventory returned 430 unique participants and 2,483 votes across the group;
question response counts range from 404 to 430. Those counts can change if
the open poll receives more answers, so every ETL run reconciles against a
same-run source snapshot and records its cutoff.

## Class 2 compatibility

The current Class 2 modeling contract stays intact:

- `workspace.ai4data.dim_participante`: one row per C2 participant with
  `confianza_analisis`, `puesto_texto`, `tarea_texto`, `respondio_todo`, and
  optional `rol_declarado_c1` from matching C1 voters.
- `workspace.ai4data.fct_respuestas`: one row per participant and C2 poll,
  with `group_code`, `poll_id`, `poll_code`, `question`, `kind`,
  `answer_value`, and `created_at`.

The live C2 group currently has the expected 1–5 confidence question and two
text prompts. Its vote/text counts were zero at the last read, so the poll
demo will show live zeroes until the class responds.
