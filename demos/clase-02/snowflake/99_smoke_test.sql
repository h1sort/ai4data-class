-- ============================================================================
-- WS2 smoke test. Run with the AGENT connection, not ACCOUNTADMIN:
--   snow sql -c ai4data_agent -f demos/clase-02/snowflake/99_smoke_test.sql
--
-- Two things to prove:
--   1. AI_CLASSIFY works and SNOWFLAKE.CORTEX_USER is actually granted.
--   2. AI4DATA_AGENT is scoped to AI4DATA only -- it must NOT be able to see
--      SNOWFLAKE_SAMPLE_DATA or any other database (guardrail §4.7).
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. AI_CLASSIFY sanity check
-- ----------------------------------------------------------------------------
-- Same taxonomy as WS4/§3: persona = {ejecutivo, manager, practitioner,
-- estudiante, otro}. 'CDO' is C-level, so expect label = 'ejecutivo'
-- (matches the Jev result for the same input in §3: ejecutivo, conf 1.00).
SELECT AI_CLASSIFY(
  'CDO',
  ['ejecutivo', 'manager', 'practitioner', 'estudiante', 'otro']
) AS persona_test;
-- Expected shape: {"labels": ["ejecutivo"]}

-- ----------------------------------------------------------------------------
-- 2. Isolation checks: AI4DATA_AGENT must see AI4DATA and nothing else
-- ----------------------------------------------------------------------------

-- Should list AI4DATA only (plus the always-visible SNOWFLAKE metadata
-- database, which every role can see for privilege/usage metadata -- that is
-- expected and is not a data-access path). It must NOT list
-- SNOWFLAKE_SAMPLE_DATA or any other customer database.
SHOW DATABASES;

-- This must fail. Expected error:
--   Database 'SNOWFLAKE_SAMPLE_DATA' does not exist or not authorized.
-- If it succeeds or returns rows, the role has more access than intended --
-- stop and fix the grants in 00_setup.sql before using this role live.
SELECT COUNT(*) FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER;

-- Same idea for INFORMATION_SCHEMA on a database the role has no USAGE on:
-- also expected to fail the same way.
SELECT COUNT(*) FROM SNOWFLAKE_SAMPLE_DATA.INFORMATION_SCHEMA.TABLES;

-- Positive control: this must succeed (confirms the role isn't just broken
-- everywhere, but specifically scoped to AI4DATA).
SELECT CURRENT_DATABASE(), CURRENT_ROLE(), CURRENT_WAREHOUSE();
