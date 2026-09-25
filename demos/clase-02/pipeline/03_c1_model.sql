-- Class 1 analytical model. IDs, questions, and options come from current D1
-- metadata; no poll IDs or answer wording are guessed here.
-- Parameters: __SCHEMA__, __GROUP_CODE_C1__, __CUTOFF__.

CREATE OR REPLACE TABLE workspace.__SCHEMA__.c1_fct_respuestas
COMMENT 'One row per respondent and Class 1 poll, group __GROUP_CODE_C1__, source cutoff __CUTOFF__.'
AS
SELECT
  v.voter_hash       AS participant_key,
  p.id               AS poll_id,
  p.code             AS poll_code,
  p.question         AS pregunta,
  p.kind             AS tipo,
  o.label            AS respuesta,
  o.position         AS posicion_opcion,
  v.created_at       AS created_at
FROM workspace.ai4data_raw.raw_poll_votes v
JOIN workspace.ai4data_raw.raw_polls p
  ON p.id = v.poll_id
JOIN workspace.ai4data_raw.raw_poll_groups g
  ON g.id = p.group_id
JOIN workspace.ai4data_raw.raw_poll_options o
  ON o.id = v.option_id AND o.poll_id = v.poll_id
WHERE g.code = '__GROUP_CODE_C1__'
  AND v.created_at <= '__CUTOFF__'

UNION ALL

SELECT
  t.voter_hash       AS participant_key,
  p.id               AS poll_id,
  p.code             AS poll_code,
  p.question         AS pregunta,
  p.kind             AS tipo,
  t.body             AS respuesta,
  CAST(NULL AS INT)  AS posicion_opcion,
  t.created_at       AS created_at
FROM workspace.ai4data_raw.raw_poll_text_answers t
JOIN workspace.ai4data_raw.raw_polls p
  ON p.id = t.poll_id
JOIN workspace.ai4data_raw.raw_poll_groups g
  ON g.id = p.group_id
WHERE g.code = '__GROUP_CODE_C1__'
  AND t.created_at <= '__CUTOFF__';


CREATE OR REPLACE TABLE workspace.__SCHEMA__.c1_dim_participante
COMMENT 'One row per distinct Class 1 respondent; participant_key is an internal join key only.'
AS
WITH poll_count AS (
  SELECT COUNT(DISTINCT p.id) AS n_polls
  FROM workspace.ai4data_raw.raw_polls p
  JOIN workspace.ai4data_raw.raw_poll_groups g ON g.id = p.group_id
  WHERE g.code = '__GROUP_CODE_C1__'
)
SELECT
  participant_key,
  COUNT(DISTINCT poll_id) AS n_preguntas_respondidas,
  COUNT(DISTINCT poll_id) = (SELECT n_polls FROM poll_count) AS respondio_todas
FROM workspace.__SCHEMA__.c1_fct_respuestas
GROUP BY participant_key;


CREATE OR REPLACE VIEW workspace.__SCHEMA__.c1_vw_resumen_respuestas
COMMENT 'Question-by-option aggregates for Class 1 charts; question-specific denominator; no participant keys or individual text answers.'
AS
WITH poll_meta AS (
  SELECT p.id AS poll_id, p.code AS poll_code, p.question AS pregunta, p.kind AS tipo
  FROM workspace.ai4data_raw.raw_polls p
  JOIN workspace.ai4data_raw.raw_poll_groups g ON g.id = p.group_id
  WHERE g.code = '__GROUP_CODE_C1__'
),
denominators AS (
  SELECT poll_id, COUNT(DISTINCT participant_key) AS denominador_pregunta
  FROM workspace.__SCHEMA__.c1_fct_respuestas
  GROUP BY poll_id
),
options AS (
  SELECT m.poll_id, m.poll_code, m.pregunta, m.tipo,
         o.label AS respuesta, o.position AS posicion_opcion
  FROM poll_meta m
  JOIN workspace.ai4data_raw.raw_poll_options o ON o.poll_id = m.poll_id
  WHERE m.tipo = 'choice'
),
choice_counts AS (
  SELECT poll_id, respuesta, posicion_opcion,
         COUNT(*) AS n_respuestas,
         COUNT(DISTINCT participant_key) AS n_participantes
  FROM workspace.__SCHEMA__.c1_fct_respuestas
  WHERE tipo = 'choice'
  GROUP BY poll_id, respuesta, posicion_opcion
),
text_counts AS (
  SELECT poll_id, COUNT(*) AS n_respuestas,
         COUNT(DISTINCT participant_key) AS n_participantes
  FROM workspace.__SCHEMA__.c1_fct_respuestas
  WHERE tipo = 'text'
  GROUP BY poll_id
),
summary AS (
  SELECT o.poll_id, o.poll_code, o.pregunta, o.tipo, o.respuesta,
         o.posicion_opcion,
         COALESCE(c.n_respuestas, 0) AS n_respuestas,
         COALESCE(c.n_participantes, 0) AS n_participantes
  FROM options o
  LEFT JOIN choice_counts c
    ON c.poll_id = o.poll_id
   AND c.respuesta = o.respuesta
   AND c.posicion_opcion = o.posicion_opcion

  UNION ALL

  SELECT m.poll_id, m.poll_code, m.pregunta, m.tipo,
         'Respuestas de texto (contenido oculto)' AS respuesta,
         CAST(NULL AS INT) AS posicion_opcion,
         COALESCE(t.n_respuestas, 0) AS n_respuestas,
         COALESCE(t.n_participantes, 0) AS n_participantes
  FROM poll_meta m
  LEFT JOIN text_counts t ON t.poll_id = m.poll_id
  WHERE m.tipo = 'text'
)
SELECT
  s.poll_code,
  s.pregunta,
  s.tipo,
  s.respuesta,
  s.posicion_opcion,
  s.n_respuestas,
  s.n_participantes,
  COALESCE(d.denominador_pregunta, 0) AS denominador_pregunta,
  CASE WHEN COALESCE(d.denominador_pregunta, 0) = 0 THEN CAST(0 AS DOUBLE)
       ELSE ROUND(100.0 * s.n_participantes / d.denominador_pregunta, 2)
  END AS porcentaje
FROM summary s
LEFT JOIN denominators d ON d.poll_id = s.poll_id;
