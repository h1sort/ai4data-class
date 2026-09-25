# Clase 2 rebuild — implementation contract

Status: implementation authorized and in progress with three Luna 6 max workers (deck, data, notebooks), supervised by the planner/integrator. This plan supersedes the previous deck narrative and CLI-only presentation preference. Preserve existing working pipeline components where useful. Do not change polls or their questions, options, URLs, or QR.

## Narrative and slide order

Spanish teaching copy; preserve Class 1's visual language. One clear idea per slide. Demo slides include a visible copyable command and a direct script/notebook link, plus short presenter notes with expected output and fallback. Commands run from the repository root.

| # | Slide / message | Visual and demo requirement |
|---|---|---|
| 1 | Today's poll | Preserve current opening poll section verbatim, including QR, URL and text. |
| 2 | who_is_this_dude? | Copy the complete bio slide from Class 1, including its styling and links. |
| 3 | Cover | Proposed title: “De la transacción a la decisión.” Subtitle: “OLTP → ETL → OLAP → Analytics / ML”. |
| 4 | What we learned last class | From the transcript: analysis is cheap; definitions still need agreement; count people versus answers correctly; agents need context, tools and verification. Recall the live poll analysis. |
| 5 | It worked with 400 people | Big contrast: “¿Y con 11 millones de clientes, cada uno con sus transacciones?” Hypothetical clients; the upcoming measured dataset contains trips. Remove the confession / promise narrative. |
| 6 | OLTP runs the application | Define Online Transaction Processing. Open source examples: PostgreSQL, MySQL, SQLite (MariaDB optional). Proprietary: Microsoft SQL Server, Oracle Database, IBM Db2. Use recognizable local logos with source attribution. |
| 7 | The refrigerator | Three stacked boxes, top to bottom: SQL API → compute → storage. Incoming transactions and an analytical scan compete for resources. Agent access is useful; workload and permissions still matter. Present as a traditional deployment model. |
| 8 | How we talk to a database | Client library/program, CLI, UI, MCP tools; show that agents can use each when equipped. Run one bounded aggregate on today's D1 poll through Wrangler and show the equivalent MCP interaction. |
| 9 | Now try 11,198,026 trips | Real NYC sample rows, scope and row count. Display the analytical question and SQL file. Run SQLite only, once; cite ~7.44 s as prior rehearsal, display the actual live time. Narrate operational contention as a hypothetical, not a measured load test. |
| 10 | Move the query to OLAP | Same SQL, same rows, DuckDB only. Read-only analytical snapshot. Reveal measured time after execution. No analytical query hits the operational database; the copy/refresh still has a cost. End: “¿Qué cambió?” |
| 11 | Rows versus columns | Reuse existing row/column visual. Explain OLTP and OLAP as workload categories; row and column layouts are common architectural choices, not definitions or absolute equivalences. |
| 12 | The architecture also changes | Revisit three layers: columnar storage; separate, elastic compute in modern cloud warehouses, vectorized execution; SQL plus platform-dependent Python/Spark/Snowpark and other APIs. Logos: Databricks, Snowflake, Amazon Redshift, Microsoft Fabric, Google BigQuery. DuckDB is embedded, not itself an elastic cloud warehouse. |
| 13 | How does data get there? | Large OLTP → ? → OLAP diagram. One click or keyboard advance reveals “ETL”. Expand extract / transform / load; briefly acknowledge ELT. |
| 14 | ETL is real engineering | Batch / microbatch / streaming; idempotency; modeling; bounded retries; edge cases; human intervention; DAG operation. “Gran parte del trabajo de ingeniería de datos”; 80% only as an explicitly informal instructor estimate. Agent assistance helps, toy demo follows. |
| 15 | ETL with an agent | Copyable prompt: inspect D1 poll schema, extract the specified groups, load Databricks via CLI, build models, reconcile counts, rerun safely. Visible single-command fallback runs ETL and checks only, without prematurely running classifiers. |
| 16 | Three things we can do now | (1) Business analytics: agreed measures, dashboard/report, business action. (2) ML: learn a difficult classification from labeled examples. (3) AI assistance: text-to-SQL for analytics; LLM/Jev classification for semantic columns. Link Astronomer article in notes. |
| 17 | Business analytics | Open Class 1 notebook. Charts: response coverage; declared role distribution; AI experience by role; trust measures by role, subject to actual question wording. End “Listo. Casi.” Data quality, meaningful measures and organizational ability to act remain necessary. |
| 18 | Ask the data: Genie | Open a prepared Genie space, choose a tested question, inspect SQL and chart. Clear metric definitions and curated tables. Include exact workspace URL once created and one fallback query. |
| 19 | ML: a new classification column | Notebook trains a small text classifier, registers a session SQL UDF and invokes it over Class 2 job titles. Training labels and held-out evaluation are explicit. Explain need for representative labeled data and ML ownership. |
| 20 | LLM and Jev: specify the judgment | Notebook runs ai_classify and Jev on the same sample and taxonomy; compare with ML. Show disagreement, latency, missing values and Jev confidence. Credentials configured through a secret reference/setup cell; never literal keys in notebook or slides. These reduce task-specific training work; evaluation remains. |
| 21 | What we covered | Operational versus analytical workloads; architectural isolation; ETL/modeling; business analytics; ML and model-provided semantic judgments. |
| 22 | New tools, durable fundamentals | Large final diagram: client ↔ OLTP → ETL/ELT → OLAP → Analytics / ML. Agents assist across the diagram. A well-studied default for many problems; avoid a universal “always” claim. |

## Existing assets and gaps

- `slides/clase-02.html`: 28 current sections; retain opening poll and reusable design/row-column elements, replace the narrative.
- `slides/clase-01.html#who-is-this-dude`: exact bio source.
- `slides/clase-01-transcript.md`: recap source; key demonstration distinguishes unique participants from answers and questions the metric definitions.
- `demos/clase-02/scale/query.sql`: existing identical SQL for SQLite and DuckDB, average tip percentage by pickup hour and payment type for positive fares.
- Existing `scale/run.sh` runs multiple engines/queries/repetitions. Keep as rehearsal tool; add a simple per-engine stage runner.
- Existing `pipeline/01_extract.sh` can extract both real groups. Existing models only provide a Class 2 participant table with a partial Class 1 role join. Full Class 1 analytics is a new model.
- Existing ai_classify / Jev scripts and shared taxonomy can be reused. No teaching notebooks currently exist.
- Live Databricks notebook compute, import permissions, Genie capability, MCP access and current credentials need preflight; prior rehearsal notes are not current verification.
- User reports rehearsal data may have been deleted. Treat all earlier dry-run results as historical evidence only. Inventory local files, remote rehearsal tables and poll rehearsal groups before relying on them; rebuild isolated synthetic fixtures if needed. Never recreate or modify the real polls to restore rehearsal data. A fresh end-to-end rehearsal is required.

## Shared contracts to freeze before delegation

Proposed single stage entry point:

```text
uv run demos/clase-02/live.py preflight
uv run demos/clase-02/live.py poll
uv run demos/clase-02/live.py scale --engine sqlite
uv run demos/clase-02/live.py scale --engine duckdb
uv run demos/clase-02/live.py etl --dataset class1
uv run demos/clase-02/live.py etl --dataset class2
```

These are implementation targets, not existing commands. The integration owner creates `live.py`; workstream owners provide the underlying functions/scripts and exact invocation contracts. Use PEP 723 dependencies if needed so uv installs requirements without manual environment repair.

- Real groups: C1 `JFQES4AF97`, C2 `8P56ZUVE9Q`. Rehearsal groups stay distinct.
- Existing catalog/schema: `workspace.ai4data`, raw `workspace.ai4data_raw`, rehearsal `workspace.ai4data_rehearsal`.
- Keep existing C2 `dim_participante` and `fct_respuestas` semantics compatible with classification scripts.
- Add `c1_dim_participante`, `c1_fct_respuestas` and a curated aggregate view for charts/Genie. Confirm columns from actual D1 question and option metadata; never hard-code guessed question IDs.
- C1 analytics includes all C1 respondents, not only the overlap with C2. Use question-specific denominators and show sample sizes.
- Notebook paths: `demos/clase-02/notebooks/01_business_analytics.ipynb`, `02_ml_classifier.ipynb`, `03_llm_jev.ipynb`.
- Common persona taxonomy: ejecutivo, manager, practitioner, estudiante, otro. All methods classify the same job-title input and same sample. Task category is optional enrichment, not the primary comparison.
- ML: curated, explicitly labeled teaching dataset, separate held-out examples, deterministic split, TF-IDF plus simple linear classifier. Do not use model-generated labels as independent ground truth. Small dataset performance is illustrative only.
- SQL UDF target: `clasificar_persona_ml(puesto_texto)` available within the notebook session. Confirm supported notebook compute before choosing the registration mechanism.
- AI notebook includes safe secret setup instructions, bounded sample size, bounded retries, reusable results and comparisons. Accuracy requires human labels; agreement alone is not accuracy.
- New files use local relative links; imported notebook and Genie URLs are recorded in a small demo manifest for deck integration.
- Store licensed/source-attributed logos locally; use HTML/CSS/SVG for architecture diagrams.

## Swarm work packages

Use `gpt-6-luna` with `max` effort. The tool offers no `gpt-6-terra`; available Terra is `gpt-5.6-terra`, so do not silently substitute it. Maximum three workers alongside the planner/integrator.

### A — Deck and visuals

Owns `slides/clase-02.html` and new Class 2 visual assets only. Implements all 22 slides, logo assets/attribution, ETL reveal, copy buttons, visible demo links and notes. Uses frozen command/table/notebook contracts. Preserves poll section verbatim and imports exact bio. Does not edit pipeline or notebooks.

Acceptance: sequence matches table; no stale narrative; keyboard navigation respects buttons and text selection; reveal works once; no overflow at 1280×720 and 1920×1080; links and asset paths resolve.

### B — Data and stage demos

Owns `demos/clase-02/pipeline/`, `scale/`, and a new `demos/clase-02/data-contract.md`. Implements separated scale runs, sample metadata, real C1 extraction/model, ETL-only entry points, count reconciliation and rerun behavior. Supplies poll query and MCP demo instructions. Coordinates schema with C before making incompatible changes.

Acceptance: identical scale query results within numeric tolerance; actual timing printed; source reads only; C1 model covers full group; rerun does not duplicate data; C2 compatibility retained; ETL stops before paid classifiers.

### C — Databricks teaching experience

Owns new `notebooks/`, training fixtures, notebook import/setup tooling and Genie setup instructions/artifacts. Implements three notebooks, charts, ML training + SQL UDF, bounded AI/Jev comparison and secret wiring. Uses B's data contract; can build against explicit fixtures while data load completes.

Acceptance: notebooks run in order on identified supported compute; real C1 charts populate; ML SQL function runs; same-input comparison works; secrets never appear in outputs; Genie questions reconcile with known SQL. If an external feature is unavailable, identify the specific gap and provide a working SQL/notebook fallback.

### Planner / integrator

Owns this plan, `demos/clase-02/live.py`, demo manifest, root README and presenter runbook. Freezes contracts, answers cross-workstream questions, reviews claims, checks visual/runtime evidence, connects exact workspace links, and reports verified versus blocked items. No concurrent edits to worker-owned files until handoff.

## Execution sequence and completion gate

1. Freeze sequence and contracts; preflight access/compute and inspect current remote schema without printing secrets.
2. Launch A/B/C on Luna 6 max. Provide each its file ownership, dependencies, contracts and acceptance criteria.
3. B publishes schema contract early; C confirms notebook runtime/UDF feasibility early; A builds against stable link targets.
4. Integrate stage entry point and actual notebook/Genie URLs. Prep C1 ETL and notebooks before class; C2 ETL refresh remains a live teaching step.
5. Rehearse the instructor path: poll → SQLite → DuckDB → ETL → business charts → Genie → ML → AI/Jev. Record actual commands, durations, results and any fallbacks.
6. Verify immutable poll, bio match, slide order, assets, copy/reveal behavior, desktop viewport fit and credential hygiene. Validate data reconciliation and notebook execution; avoid redundant tests of presentation copy.
7. Deliver deck, single runbook, runnable entry point, imported notebooks/links and precise remaining external blockers, if any. No fabricated readiness or benchmark guarantees.

## Source for semantic-column narrative

Astronomer, “What Jev will do to data engineering”: https://www.astronomer.io/blog/what-jev-will-do-to-data-engineering/

Use its progression of rules → trained ML → LLM → typed decision model as motivation. Its own comparison distinguishes model agreement from correctness and calls for a labeled evaluation sample. External benchmark numbers are not our demo measurements.
