-- WS4 step 3: model layer. Builds workspace.<schema>.fct_respuestas
-- (grain: voter_hash x question, Clase 2 group only) and
-- workspace.<schema>.dim_participante (grain: voter_hash, Clase 2 group
-- only), with rol_declarado_c1 joined in from the companion Class 1 group
-- when the same voter_hash voted there -- NULL otherwise. That partial
-- overlap is the join at the heart of the payoff (CLASS2-PLAN.md §2.5).
--
-- Parameters (substituted by 03_model.sh):
--   __SCHEMA__          target schema: ai4data (class) or ai4data_rehearsal
--   __GROUP_CODE_C2__   Clase 2 group code (poll_groups.code)
--   __GROUP_CODE_C1__   Class 1 (or Ensayo · Clase 1) group code
--   __CUTOFF__          UTC cutoff 'YYYY-MM-DD HH:MM:SS' -- rows created
--                        after this are excluded, so a rerun mid-demo with
--                        new responses trickling in doesn't shift the numbers
--                        already discussed on stage.
--
-- Idempotent: CREATE OR REPLACE, safe to rerun.

CREATE OR REPLACE TABLE workspace.__SCHEMA__.fct_respuestas
COMMENT 'Grain: voter_hash x question, Clase 2 group __GROUP_CODE_C2__ only, cutoff __CUTOFF__. One row per answer (choice vote or text answer).'
AS
SELECT
  v.voter_hash,
  g.code           AS group_code,
  p.id             AS poll_id,
  p.code           AS poll_code,
  p.question       AS question,
  'choice'         AS kind,
  o.label          AS answer_value,
  v.created_at     AS created_at
FROM workspace.ai4data_raw.raw_poll_votes v
JOIN workspace.ai4data_raw.raw_polls p        ON p.id = v.poll_id
JOIN workspace.ai4data_raw.raw_poll_groups g  ON g.id = p.group_id
JOIN workspace.ai4data_raw.raw_poll_options o ON o.id = v.option_id AND o.poll_id = v.poll_id
WHERE g.code = '__GROUP_CODE_C2__'
  AND v.created_at <= '__CUTOFF__'

UNION ALL

SELECT
  t.voter_hash,
  g.code           AS group_code,
  p.id             AS poll_id,
  p.code           AS poll_code,
  p.question       AS question,
  'text'           AS kind,
  t.body           AS answer_value,
  t.created_at     AS created_at
FROM workspace.ai4data_raw.raw_poll_text_answers t
JOIN workspace.ai4data_raw.raw_polls p        ON p.id = t.poll_id
JOIN workspace.ai4data_raw.raw_poll_groups g  ON g.id = p.group_id
WHERE g.code = '__GROUP_CODE_C2__'
  AND t.created_at <= '__CUTOFF__';


CREATE OR REPLACE TABLE workspace.__SCHEMA__.dim_participante
COMMENT 'One row per voter_hash in Clase 2 group __GROUP_CODE_C2__ (cutoff __CUTOFF__). rol_declarado_c1 is Q5 ("trabajo principal") from the companion Class 1 group __GROUP_CODE_C1__ when the same voter_hash voted there, NULL otherwise -- the two-sources-of-role join (CLASS2-PLAN.md §2.5).'
AS
WITH confianza AS (
  SELECT v.voter_hash, CAST(o.label AS INT) AS confianza_analisis
  FROM workspace.ai4data_raw.raw_poll_votes v
  JOIN workspace.ai4data_raw.raw_polls p        ON p.id = v.poll_id
  JOIN workspace.ai4data_raw.raw_poll_groups g  ON g.id = p.group_id
  JOIN workspace.ai4data_raw.raw_poll_options o ON o.id = v.option_id AND o.poll_id = v.poll_id
  WHERE g.code = '__GROUP_CODE_C2__' AND p.kind = 'choice' AND v.created_at <= '__CUTOFF__'
),
puesto AS (
  SELECT t.voter_hash, t.body AS puesto_texto
  FROM workspace.ai4data_raw.raw_poll_text_answers t
  JOIN workspace.ai4data_raw.raw_polls p       ON p.id = t.poll_id
  JOIN workspace.ai4data_raw.raw_poll_groups g ON g.id = p.group_id
  WHERE g.code = '__GROUP_CODE_C2__' AND p.max_length = 120 AND t.created_at <= '__CUTOFF__'
),
tarea AS (
  SELECT t.voter_hash, t.body AS tarea_texto
  FROM workspace.ai4data_raw.raw_poll_text_answers t
  JOIN workspace.ai4data_raw.raw_polls p       ON p.id = t.poll_id
  JOIN workspace.ai4data_raw.raw_poll_groups g ON g.id = p.group_id
  WHERE g.code = '__GROUP_CODE_C2__' AND p.max_length = 280 AND t.created_at <= '__CUTOFF__'
),
rol_c1 AS (
  SELECT v.voter_hash, o.label AS rol_declarado_c1
  FROM workspace.ai4data_raw.raw_poll_votes v
  JOIN workspace.ai4data_raw.raw_polls p        ON p.id = v.poll_id
  JOIN workspace.ai4data_raw.raw_poll_groups g  ON g.id = p.group_id
  JOIN workspace.ai4data_raw.raw_poll_options o ON o.id = v.option_id AND o.poll_id = v.poll_id
  WHERE g.code = '__GROUP_CODE_C1__'
    AND p.question = '¿Cuál describe mejor tu trabajo principal?'
    AND v.created_at <= '__CUTOFF__'
),
participantes AS (
  SELECT voter_hash FROM confianza
  UNION
  SELECT voter_hash FROM puesto
  UNION
  SELECT voter_hash FROM tarea
)
SELECT
  pa.voter_hash                              AS participant_key,
  c.confianza_analisis,
  pu.puesto_texto,
  ta.tarea_texto,
  (c.confianza_analisis IS NOT NULL
    AND pu.puesto_texto IS NOT NULL
    AND ta.tarea_texto IS NOT NULL)          AS respondio_todo,
  r.rol_declarado_c1
FROM participantes pa
LEFT JOIN confianza c  ON c.voter_hash = pa.voter_hash
LEFT JOIN puesto    pu ON pu.voter_hash = pa.voter_hash
LEFT JOIN tarea     ta ON ta.voter_hash = pa.voter_hash
LEFT JOIN rol_c1     r ON r.voter_hash = pa.voter_hash;
