-- WS2 (Databricks) setup for Class 2.
--
-- Creates the three schemas the demo pipeline is allowed to write to (see
-- CLASS2-PLAN.md §4 guardrail 7) plus the landing volume used by the ETL to
-- stage JSON exported from D1 before it's loaded into ai4data_raw tables.
--
-- Idempotent: safe to re-run. Run with:
--   ./demos/clase-02/databricks/run_sql.sh -f demos/clase-02/databricks/00_setup.sql

CREATE SCHEMA IF NOT EXISTS workspace.ai4data_raw
  COMMENT 'Class 2 (AI4Data): raw landing zone. Tables here are 1:1 with the JSON exported from D1 (poll groups/polls/options/votes/text answers), loaded via read_files() over the ai4data_raw.landing volume. Untyped/unmodeled; the ETL step 02_load recreates these tables on every run (CREATE OR REPLACE).';

CREATE SCHEMA IF NOT EXISTS workspace.ai4data
  COMMENT 'Class 2 (AI4Data): modeled layer. dim_participante / fct_respuestas built from ai4data_raw, plus ai_classify/Jev judgment columns and the comparison views used in the live demo and slides.';

CREATE SCHEMA IF NOT EXISTS workspace.ai4data_rehearsal
  COMMENT 'Class 2 (AI4Data): mirror of workspace.ai4data used for rehearsals against the "Ensayo - Clase 2" poll group, so rehearsal runs never touch data destined for the real class demo.';

CREATE VOLUME IF NOT EXISTS workspace.ai4data_raw.landing
  COMMENT 'Class 2 (AI4Data): landing volume for JSON files exported from D1 by 01_extract.sh, staged here via `databricks fs cp` before 02_load.sql reads them with read_files().';
