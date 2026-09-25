-- WS4 step 4: data-quality tests. Every SELECT below returns one row with a
-- `violations` count -- 0 means PASS. Reviewed visually in run_sql.sh's
-- printed tables (or grepped for a nonzero count by run_all.sh).
--
-- Parameters (substituted by 04_tests.sh):
--   __SCHEMA__               target schema (ai4data | ai4data_rehearsal)
--   __GROUP_CODE_C2__        Clase 2 group code
--   __GROUP_CODE_C1__        companion Class 1 group code
--   __D1_VOTES_CONFIANZA__   D1-side count of confianza votes (from wrangler,
--                            same cutoff as 03_model.sh), for reconciliation
--   __D1_TEXT_PUESTO__       D1-side count of puesto text answers
--   __D1_TEXT_TAREA__        D1-side count of tarea text answers

SELECT 'uniqueness: dim_participante.participant_key' AS test_name,
       (SELECT COUNT(*) FROM (
          SELECT participant_key FROM workspace.__SCHEMA__.dim_participante
          GROUP BY participant_key HAVING COUNT(*) > 1
        )) AS violations;

SELECT 'uniqueness: fct_respuestas voter x poll' AS test_name,
       (SELECT COUNT(*) FROM (
          SELECT voter_hash, poll_id FROM workspace.__SCHEMA__.fct_respuestas
          GROUP BY voter_hash, poll_id HAVING COUNT(*) > 1
        )) AS violations;

SELECT 'options belong to their own poll' AS test_name,
       (SELECT COUNT(*) FROM workspace.ai4data_raw.raw_poll_votes v
        JOIN workspace.ai4data_raw.raw_poll_options o ON o.id = v.option_id
        WHERE o.poll_id <> v.poll_id) AS violations;

SELECT 'no foreign groups in raw_poll_votes' AS test_name,
       (SELECT COUNT(*) FROM workspace.ai4data_raw.raw_poll_votes v
        JOIN workspace.ai4data_raw.raw_polls p       ON p.id = v.poll_id
        JOIN workspace.ai4data_raw.raw_poll_groups g ON g.id = p.group_id
        WHERE g.code NOT IN ('__GROUP_CODE_C2__', '__GROUP_CODE_C1__')) AS violations;

SELECT 'no foreign groups in raw_poll_text_answers' AS test_name,
       (SELECT COUNT(*) FROM workspace.ai4data_raw.raw_poll_text_answers t
        JOIN workspace.ai4data_raw.raw_polls p       ON p.id = t.poll_id
        JOIN workspace.ai4data_raw.raw_poll_groups g ON g.id = p.group_id
        WHERE g.code NOT IN ('__GROUP_CODE_C2__', '__GROUP_CODE_C1__')) AS violations;

-- A missing answer must stay NULL, never get coerced into '' or a sentinel
-- like 'No' -- that's what "nulls reported, never turned into No" means in
-- practice: a non-answer and a real answer must never collide on the same
-- non-NULL value.
SELECT 'no empty-string coercion in puesto_texto' AS test_name,
       (SELECT COUNT(*) FROM workspace.__SCHEMA__.dim_participante WHERE puesto_texto = '') AS violations;

SELECT 'no empty-string coercion in tarea_texto' AS test_name,
       (SELECT COUNT(*) FROM workspace.__SCHEMA__.dim_participante WHERE tarea_texto = '') AS violations;

-- Informational, not pass/fail: how many participants have a NULL for each
-- column (should match D1's "skipped this question" count, shown on stage
-- next to this).
SELECT 'info: puesto_texto NULL count' AS test_name,
       (SELECT COUNT(*) FROM workspace.__SCHEMA__.dim_participante WHERE puesto_texto IS NULL) AS violations;

SELECT 'info: tarea_texto NULL count' AS test_name,
       (SELECT COUNT(*) FROM workspace.__SCHEMA__.dim_participante WHERE tarea_texto IS NULL) AS violations;

SELECT 'reconciliation: confianza votes vs D1' AS test_name,
       ABS((SELECT COUNT(*) FROM workspace.__SCHEMA__.fct_respuestas
            WHERE group_code = '__GROUP_CODE_C2__' AND kind = 'choice')
           - __D1_VOTES_CONFIANZA__) AS violations;

SELECT 'reconciliation: puesto answers vs D1' AS test_name,
       ABS((SELECT COUNT(*) FROM workspace.__SCHEMA__.dim_participante WHERE puesto_texto IS NOT NULL)
           - __D1_TEXT_PUESTO__) AS violations;

SELECT 'reconciliation: tarea answers vs D1' AS test_name,
       ABS((SELECT COUNT(*) FROM workspace.__SCHEMA__.dim_participante WHERE tarea_texto IS NOT NULL)
           - __D1_TEXT_TAREA__) AS violations;
