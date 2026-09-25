# WS4 demo pipeline (Class 2)

D1 → Databricks ETL for the 3-question Clase 2 poll (confianza en análisis
de IA, puesto, tarea a automatizar), plus the judgment column
(`ai_classify` vs Jev) and the payoff comparison. This is the reference
solution the live agent should reach on stage, and it doubles as the
fallback if the live demo breaks (see `out/fallback/`).

For the live class, see [`../../clase-02-prompts.md`](../../clase-02-prompts.md).
The public aggregate rehearsal numbers are in
[`../../clase-02-rehearsal-results.md`](../../clase-02-rehearsal-results.md).

## Taxonomy (shared between `ai_classify` and Jev)

- **persona**: `ejecutivo`, `manager`, `practitioner`, `estudiante`, `otro`
- **categoria_tarea**: `limpieza/calidad`, `reporting/dashboards`,
  `ETL/pipelines`, `análisis/EDA`, `ML/modelos`, `documentación`, `otro`

`ai_classify` takes labels only (`ARRAY(...)`). Jev's Choice questions take
`criteria`: `{label: description}` — same labels, plus a one-line
description for each (see `06_jev.py`'s `PERSONA_CRITERIA` /
`CATEGORIA_CRITERIA`).

## Data model

- `workspace.ai4data_raw.raw_*` — 1:1 landing tables from D1 JSON
  (`raw_poll_groups`, `raw_polls`, `raw_poll_options`, `raw_poll_votes`,
  `raw_poll_text_answers`). Always this one schema, `CREATE OR REPLACE`
  every run, regardless of rehearsal/class.
- `workspace.<schema>.dim_participante` — one row per `voter_hash` in the
  Clase 2 group: `confianza_analisis` (1-5), `puesto_texto`, `tarea_texto`,
  `respondio_todo`, `rol_declarado_c1` (Class 1 Q5, "trabajo principal",
  joined by `voter_hash` from the companion Class 1 group — NULL if that
  voter never answered there; that partial overlap is the point, §2.5).
- `workspace.<schema>.fct_respuestas` — grain voter_hash × question, Clase 2
  group only.
- `workspace.<schema>.judgments_ai_classify` — `persona_dbx`,
  `categoria_tarea_dbx`. No confidence (Databricks AI Functions design).
- `workspace.<schema>.judgments_jev` — `persona`, `persona_conf`,
  `categoria`, `categoria_conf`, `probabilities` (JSON), `model`,
  `input_tokens`, `latency_ms`.

`<schema>` is `ai4data_rehearsal` for rehearsals, `ai4data` for the real
class. These plus `ai4data_raw` are the only schemas the pipeline writes to.

## Run order

Either the whole thing:

```bash
./run_all.sh                                          # rehearsal shortcut:
                                                        #   Ensayo · Clase 2 = YWE57U6B8U
                                                        #   Ensayo · Clase 1 = R57BDNR5ZG
                                                        #   schema = ai4data_rehearsal
./run_all.sh 8P56ZUVE9Q JFQES4AF97 ai4data             # the real class
```

...or step by step (every step takes the group code(s) and/or schema it
needs directly, so any one step can be rerun standalone):

```bash
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
CUTOFF=$(date -u +'%Y-%m-%d %H:%M:%S')

./01_extract.sh YWE57U6B8U,R57BDNR5ZG "$RUN_ID"        # D1 -> out/<run_id>/*.ndjson
./02_load.sh "$RUN_ID"                                  # Volume + read_files -> ai4data_raw.raw_*
./03_model.sh ai4data_rehearsal YWE57U6B8U R57BDNR5ZG "$CUTOFF"   # dim_participante, fct_respuestas
./04_tests.sh ai4data_rehearsal YWE57U6B8U R57BDNR5ZG "$CUTOFF"   # reconciliation + uniqueness gate
./05_ai_classify.sh ai4data_rehearsal                    # judgments_ai_classify
uv run 06_jev.py --schema ai4data_rehearsal              # judgments_jev
./07_compare.sh ai4data_rehearsal                        # agreement, routing, injections, payoff
```

`run_all.sh` times every step, halts on the first failure (`04_tests.sh`'s
data-quality gate included) unless `--keep-going` is passed, and ends by
exporting `out/fallback/<run_id>/*.csv` via `_export_fallback.py`.

## Rehearsal seed data

`seed_rehearsal.py` creates the "Ensayo · Clase 1" group (Class 1's 6
questions/options, copied verbatim by discovering them live from D1 — never
hand-transcribed) and ~60 synthetic participants (`voter_hash` prefixed
`ensayo_`) who answer the 3 "Ensayo · Clase 2" questions, ~40 of whom also
vote in "Ensayo · Clase 1" (partial overlap, for `rol_declarado_c1`).
Content includes realistic Spanish/English job titles, junk, emoji, one
short/ambiguous answer, and 3 prompt-injection attempts. Idempotent: reruns
delete-then-reinsert only `ensayo_%`-prefixed rows, only inside the two
Ensayo groups.

```bash
python3 seed_rehearsal.py             # dry run: prints the plan
python3 seed_rehearsal.py --execute   # writes to remote D1 (Ensayo groups only)
```

## Environment

Everything reads `.env` (repo root) and runs Databricks calls as
`DATABRICKS_AGENT_TOKEN` (the scoped `ai4data-agent` service principal), not
the admin PAT that also lives in `.env` — `_lib.sh`'s `load_env` (bash) and
each Python script's own credential loading both force this. D1 access goes
through `wrangler` from the sibling `h1sort-website` checkout (or the
`D1_REPO` environment variable) and only ever
reads (SELECT) — the pipeline never writes to D1; only `seed_rehearsal.py`
does, and only in the two Ensayo groups.

## Guardrails this pipeline enforces

- D1: only `poll_groups`, `polls`, `poll_options`, `poll_votes`,
  `poll_text_answers`. Never `conversations`/`messages`/auth tables.
- `voter_hash` is a join key only — never selected into a comparison table
  or printed by any script.
- Databricks: writes only to `workspace.ai4data_raw`, `workspace.ai4data`,
  `workspace.ai4data_rehearsal`.
- `04_tests.sh` fails the run (by default) if reconciliation against D1's
  own counts, uniqueness, or the no-foreign-groups check don't pass.
