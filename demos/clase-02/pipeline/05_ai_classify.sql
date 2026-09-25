-- WS4 step 5: judgment column, Databricks side. persona (from puesto_texto)
-- and categoria_tarea (from tarea_texto) via ai_classify, taxonomy shared
-- with Jev (see README.md).
--
-- ONE set-based CREATE TABLE AS SELECT, not one call per row: per
-- CLASS2-PLAN.md §9 WS2, a single statement over N rows measured ~16x more
-- row-efficient than N one-row statements (per-statement overhead, not
-- per-row model compute, dominates) -- this is the batching lesson the class
-- demo is built to show.
--
-- ai_classify returns a label only, no confidence -- that's the point of
-- comparing it with judgments_jev (06_jev.py) in 07_compare.sql.
--
-- Parameter (substituted by 05_ai_classify.sh): __SCHEMA__

CREATE OR REPLACE TABLE workspace.__SCHEMA__.judgments_ai_classify
COMMENT 'ai_classify persona/categoria_tarea judgments per participant. No confidence (Databricks AI Functions design) -- compare with judgments_jev, which reports confidence + probabilities.'
AS
SELECT
  participant_key,
  CASE WHEN puesto_texto IS NOT NULL
    THEN ai_classify(puesto_texto, ARRAY('ejecutivo', 'manager', 'practitioner', 'estudiante', 'otro'))
    ELSE NULL END AS persona_dbx,
  CASE WHEN tarea_texto IS NOT NULL
    THEN ai_classify(tarea_texto, ARRAY(
      'limpieza/calidad', 'reporting/dashboards', 'ETL/pipelines',
      'análisis/EDA', 'ML/modelos', 'documentación', 'otro'
    ))
    ELSE NULL END AS categoria_tarea_dbx
FROM workspace.__SCHEMA__.dim_participante;
