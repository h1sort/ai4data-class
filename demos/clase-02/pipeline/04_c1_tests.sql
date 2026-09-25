-- Parameters: __SCHEMA__, __D1_ANSWER_COUNT__, __D1_PARTICIPANT_COUNT__.

SELECT 'C1 responses reconcile with D1' AS test_name,
       ABS((SELECT COUNT(*) FROM workspace.__SCHEMA__.c1_fct_respuestas)
           - __D1_ANSWER_COUNT__) AS violations;

SELECT 'C1 respondents reconcile with D1' AS test_name,
       ABS((SELECT COUNT(*) FROM workspace.__SCHEMA__.c1_dim_participante)
           - __D1_PARTICIPANT_COUNT__) AS violations;

SELECT 'unique respondent × poll grain' AS test_name,
       (SELECT COUNT(*) FROM (
          SELECT participant_key, poll_id
          FROM workspace.__SCHEMA__.c1_fct_respuestas
          GROUP BY participant_key, poll_id HAVING COUNT(*) > 1
        )) AS violations;

WITH view_denominators AS (
  SELECT poll_code, MIN(denominador_pregunta) AS min_denominator,
         MAX(denominador_pregunta) AS max_denominator
  FROM workspace.__SCHEMA__.c1_vw_resumen_respuestas
  GROUP BY poll_code
), fact_denominators AS (
  SELECT poll_code, COUNT(DISTINCT participant_key) AS n_participants
  FROM workspace.__SCHEMA__.c1_fct_respuestas
  GROUP BY poll_code
)
SELECT 'aggregate denominator matches fact' AS test_name,
       COUNT(*) AS violations
FROM view_denominators v
JOIN fact_denominators f ON f.poll_code = v.poll_code
WHERE v.min_denominator <> v.max_denominator
   OR v.max_denominator <> f.n_participants;
