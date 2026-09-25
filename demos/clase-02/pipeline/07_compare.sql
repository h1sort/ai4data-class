-- WS4 step 7: compare ai_classify vs Jev, the routing table, where the
-- injections landed, and the payoff (CLASS2-PLAN.md §2.5).
--
-- Parameter (substituted by 07_compare.sh): __SCHEMA__
--
-- Every SELECT below is its own printed table (run_sql.py prints one per
-- statement) -- read them top to bottom in the order listed in the header
-- comments.

-- === 1/10: persona agreement, overall ===
SELECT 'persona: overall' AS metric,
       COUNT(*) AS n,
       SUM(CASE WHEN a.persona_dbx = j.persona THEN 1 ELSE 0 END) AS agree,
       ROUND(100.0 * SUM(CASE WHEN a.persona_dbx = j.persona THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_agree
FROM workspace.__SCHEMA__.judgments_ai_classify a
JOIN workspace.__SCHEMA__.judgments_jev j ON j.participant_key = a.participant_key
WHERE a.persona_dbx IS NOT NULL AND j.persona IS NOT NULL;

-- === 2/10: persona agreement, by Jev confidence band ===
SELECT
  CASE WHEN j.persona_conf >= 0.9 THEN '1) >=0.9'
       WHEN j.persona_conf >= 0.5 THEN '2) 0.5-0.9'
       ELSE '3) <0.5' END AS confidence_band,
  COUNT(*) AS n,
  SUM(CASE WHEN a.persona_dbx = j.persona THEN 1 ELSE 0 END) AS agree,
  ROUND(100.0 * SUM(CASE WHEN a.persona_dbx = j.persona THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_agree
FROM workspace.__SCHEMA__.judgments_ai_classify a
JOIN workspace.__SCHEMA__.judgments_jev j ON j.participant_key = a.participant_key
WHERE a.persona_dbx IS NOT NULL AND j.persona IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- === 3/10: categoria_tarea agreement, overall ===
SELECT 'categoria: overall' AS metric,
       COUNT(*) AS n,
       SUM(CASE WHEN a.categoria_tarea_dbx = j.categoria THEN 1 ELSE 0 END) AS agree,
       ROUND(100.0 * SUM(CASE WHEN a.categoria_tarea_dbx = j.categoria THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_agree
FROM workspace.__SCHEMA__.judgments_ai_classify a
JOIN workspace.__SCHEMA__.judgments_jev j ON j.participant_key = a.participant_key
WHERE a.categoria_tarea_dbx IS NOT NULL AND j.categoria IS NOT NULL;

-- === 4/10: categoria_tarea agreement, by Jev confidence band ===
SELECT
  CASE WHEN j.categoria_conf >= 0.9 THEN '1) >=0.9'
       WHEN j.categoria_conf >= 0.5 THEN '2) 0.5-0.9'
       ELSE '3) <0.5' END AS confidence_band,
  COUNT(*) AS n,
  SUM(CASE WHEN a.categoria_tarea_dbx = j.categoria THEN 1 ELSE 0 END) AS agree,
  ROUND(100.0 * SUM(CASE WHEN a.categoria_tarea_dbx = j.categoria THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_agree
FROM workspace.__SCHEMA__.judgments_ai_classify a
JOIN workspace.__SCHEMA__.judgments_jev j ON j.participant_key = a.participant_key
WHERE a.categoria_tarea_dbx IS NOT NULL AND j.categoria IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- === 5/10: routing table, persona (>=0.9 warehouse / 0.5-0.9 LLM review / <0.5 human) ===
SELECT
  CASE WHEN persona_conf >= 0.9 THEN '1) >=0.9 -> warehouse'
       WHEN persona_conf >= 0.5 THEN '2) 0.5-0.9 -> LLM review'
       ELSE '3) <0.5 -> human' END AS route,
  COUNT(*) AS n
FROM workspace.__SCHEMA__.judgments_jev
WHERE persona_conf IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- === 6/10: routing table, categoria_tarea ===
SELECT
  CASE WHEN categoria_conf >= 0.9 THEN '1) >=0.9 -> warehouse'
       WHEN categoria_conf >= 0.5 THEN '2) 0.5-0.9 -> LLM review'
       ELSE '3) <0.5 -> human' END AS route,
  COUNT(*) AS n
FROM workspace.__SCHEMA__.judgments_jev
WHERE categoria_conf IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- === 7/10: where the injections landed (simple heuristic match on puesto_texto) ===
SELECT
  d.puesto_texto,
  a.persona_dbx        AS ai_classify_persona,
  j.persona             AS jev_persona,
  j.persona_conf        AS jev_confidence
FROM workspace.__SCHEMA__.dim_participante d
JOIN workspace.__SCHEMA__.judgments_ai_classify a ON a.participant_key = d.participant_key
JOIN workspace.__SCHEMA__.judgments_jev j          ON j.participant_key = d.participant_key
WHERE LOWER(d.puesto_texto) LIKE '%ignora%instruc%'
   OR LOWER(d.puesto_texto) LIKE '%ignore%instruc%'
   OR LOWER(d.puesto_texto) LIKE '%olvida%regla%'
   OR LOWER(d.puesto_texto) LIKE '%olvida%anterior%';

-- === 8/10: payoff -- % with confianza 4-5 by classified persona (Jev; has confidence) ===
-- n/N shown; segments with n<5 aren't ranked/percentaged (CLASS2-PLAN.md guardrail).
SELECT
  j.persona,
  COUNT(*) AS n,
  SUM(CASE WHEN d.confianza_analisis >= 4 THEN 1 ELSE 0 END) AS n_confianza_alta,
  CASE WHEN COUNT(*) >= 5
       THEN CONCAT(
         CAST(ROUND(100.0 * SUM(CASE WHEN d.confianza_analisis >= 4 THEN 1 ELSE 0 END) / COUNT(*), 1) AS STRING),
         '%'
       )
       ELSE 'n<5, no ranking' END AS pct_confianza_alta
FROM workspace.__SCHEMA__.dim_participante d
JOIN workspace.__SCHEMA__.judgments_jev j ON j.participant_key = d.participant_key
WHERE j.persona IS NOT NULL AND d.confianza_analisis IS NOT NULL
GROUP BY j.persona
ORDER BY n DESC;

-- === 9/10: overlap -- declared role (Class 1 Q5) x classified persona (Jev) ===
SELECT
  d.rol_declarado_c1,
  j.persona AS persona_jev,
  COUNT(*) AS n
FROM workspace.__SCHEMA__.dim_participante d
JOIN workspace.__SCHEMA__.judgments_jev j ON j.participant_key = d.participant_key
WHERE d.rol_declarado_c1 IS NOT NULL AND j.persona IS NOT NULL
GROUP BY d.rol_declarado_c1, j.persona
ORDER BY d.rol_declarado_c1, n DESC;

-- === 10/10: overlap rate -- how many Clase 2 participants also voted in Class 1 ===
SELECT
  COUNT(*) AS total_participantes,
  SUM(CASE WHEN rol_declarado_c1 IS NOT NULL THEN 1 ELSE 0 END) AS con_rol_c1,
  ROUND(100.0 * SUM(CASE WHEN rol_declarado_c1 IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_overlap
FROM workspace.__SCHEMA__.dim_participante;
