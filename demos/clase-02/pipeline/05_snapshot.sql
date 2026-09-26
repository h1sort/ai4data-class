-- WS0 fix (Class 3): persist a structured, queryable ETL snapshot.
--
-- Root cause this closes: 03_model.sql/03_c1_model.sql already stamp the
-- cutoff into each table's Delta COMMENT, and 04_tests.sh/04_c1_tests.sh
-- already fetch fresh D1 source counts for reconciliation -- but neither
-- was ever written anywhere queryable. The cutoff lived only in a comment
-- string (needs DESCRIBE TABLE EXTENDED to read) and the D1 source counts
-- only in that run's terminal output, gone once the shell scrolled. On
-- stage in Clase 2, once the presenter's terminal had moved on, there was
-- no way for anyone -- agent or human -- to tell whether a "0 answers"
-- moment meant the poll was genuinely still empty at that instant, or that
-- they were looking at an earlier run's numbers. That ambiguity, not a
-- broken extract/load/model query, is what made the live answers seem to
-- "not show up": the data was correct, but its freshness was unverifiable
-- after the fact. This table makes loaded_at/cutoff/source-counts durable
-- so the Class 3 freshness demo (D1 live count vs Databricks snapshot) has
-- something to query.
--
-- Append-only: one row per dataset stage (class1 | class2) per etl_only.sh
-- or run_all.sh run. Written by 04_c1_tests.sh and 04_tests.sh, after their
-- own reconciliation verdict is known. NULL columns are metrics that stage
-- doesn't measure (e.g. a class1-only run leaves the class2 D1 counts NULL).
--
-- Parameters (substituted by the caller via render_and_run):
--   __SCHEMA__                 target schema (ai4data | ai4data_rehearsal)
--   __RUN_ID__                 this run's id (from etl_only.sh/run_all.sh)
--   __DATASET__                'class1' | 'class2'
--   __GROUP_CODES__            comma-separated D1 group codes used this run
--   __CUTOFF__                 UTC cutoff used to build the model tables
--   __LOADED_AT__              UTC wall-clock time this snapshot row is written
--   __D1_VOTES_CONFIANZA__     class2 confianza vote count at cutoff, or NULL
--   __D1_TEXT_PUESTO__         class2 puesto text count at cutoff, or NULL
--   __D1_TEXT_TAREA__          class2 tarea text count at cutoff, or NULL
--   __D1_C1_ANSWERS__          class1 answer-row count at cutoff, or NULL
--   __D1_C1_PARTICIPANTS__     class1 distinct participant count at cutoff, or NULL
--   __STATUS__                 'PASS' | 'FAIL' (this stage's test verdict)

CREATE TABLE IF NOT EXISTS workspace.__SCHEMA__.etl_snapshots (
  run_id STRING,
  dataset STRING,
  group_codes STRING,
  cutoff_utc STRING,
  loaded_at_utc STRING,
  d1_votes_confianza BIGINT,
  d1_text_puesto BIGINT,
  d1_text_tarea BIGINT,
  d1_c1_answers BIGINT,
  d1_c1_participants BIGINT,
  status STRING
) USING DELTA
COMMENT 'Append-only ETL run log (WS0, Class 3): one row per dataset stage per etl_only.sh/run_all.sh run. loaded_at_utc/cutoff_utc + source counts back the freshness demo (D1 live count vs this snapshot). Query the max(loaded_at_utc) row per dataset for "as of".';

INSERT INTO workspace.__SCHEMA__.etl_snapshots
VALUES (
  '__RUN_ID__', '__DATASET__', '__GROUP_CODES__', '__CUTOFF__', '__LOADED_AT__',
  __D1_VOTES_CONFIANZA__, __D1_TEXT_PUESTO__, __D1_TEXT_TAREA__,
  __D1_C1_ANSWERS__, __D1_C1_PARTICIPANTS__, '__STATUS__'
);
