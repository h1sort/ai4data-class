-- ============================================================================
-- WS2 Snowflake setup: warehouse, resource monitor, database, schemas,
-- stage, and the least-privilege AI4DATA_AGENT role.
--
-- GUARDRAIL (CLASS2-PLAN.md §4.1): creating Snowflake objects with
-- ACCOUNTADMIN needs human approval, shown the SQL first. DO NOT RUN THIS
-- AUTOMATICALLY. A human reviews this file, then runs it (e.g.
-- `snow sql -c ai4data -f demos/clase-02/snowflake/00_setup.sql`, or pastes
-- it into a Snowsight worksheet).
--
-- Prerequisite: the human has already run
-- demos/clase-02/snowflake/HUMAN_run_in_snowsight.sql (registers the agent's
-- public key on H1SORT), and `snow connection test -c ai4data` succeeds.
--
-- Idempotent: every statement uses IF NOT EXISTS / OR REPLACE where safe, so
-- reruns don't fail or duplicate objects. Reruns do NOT reset the resource
-- monitor's consumed credits.
-- ============================================================================

USE ROLE ACCOUNTADMIN;

-- ----------------------------------------------------------------------------
-- 0. Region / Cortex availability check
-- ----------------------------------------------------------------------------
SELECT CURRENT_REGION();

-- Only uncomment and run if AI_CLASSIFY / Cortex functions are unavailable
-- in CURRENT_REGION() (see §3 in CLASS2-PLAN.md -- region support for
-- AI_CLASSIFY is unverified on this account). This is itself an
-- account-level change; confirm it's actually needed before running it.
-- ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';

-- ----------------------------------------------------------------------------
-- 1. Resource monitor (create before the warehouse that references it)
-- ----------------------------------------------------------------------------
CREATE RESOURCE MONITOR IF NOT EXISTS AI4DATA_RM
  WITH
    CREDIT_QUOTA = 20
    FREQUENCY = MONTHLY
    START_TIMESTAMP = IMMEDIATELY
  TRIGGERS
    ON 50 PERCENT DO NOTIFY
    ON 80 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND;

-- ----------------------------------------------------------------------------
-- 2. Warehouse
-- ----------------------------------------------------------------------------
CREATE WAREHOUSE IF NOT EXISTS AI4DATA_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  RESOURCE_MONITOR = AI4DATA_RM
  COMMENT = 'AI4Data Class 2 demo warehouse (capped by AI4DATA_RM).';

-- If the warehouse already existed without the monitor attached, this makes
-- sure it's attached (no-op if already set):
ALTER WAREHOUSE AI4DATA_WH SET RESOURCE_MONITOR = AI4DATA_RM;

-- ----------------------------------------------------------------------------
-- 3. Database and schemas
-- ----------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS AI4DATA
  COMMENT = 'AI4Data Class 2: D1 poll data modeled and judged in Snowflake.';

CREATE SCHEMA IF NOT EXISTS AI4DATA.RAW
  COMMENT = 'Landing zone: raw JSON copied from the D1 export (RAW.D1_STAGE).';
CREATE SCHEMA IF NOT EXISTS AI4DATA.ANALYTICS
  COMMENT = 'Modeled tables (dim/fct), AI_CLASSIFY and Jev judgment outputs.';
CREATE SCHEMA IF NOT EXISTS AI4DATA.REHEARSAL
  COMMENT = 'Mirror of ANALYTICS used for the Ensayo run against synthetic data.';

-- ----------------------------------------------------------------------------
-- 4. Stage + file format for the D1 JSON export
-- ----------------------------------------------------------------------------
CREATE FILE FORMAT IF NOT EXISTS AI4DATA.RAW.JSON_FF
  TYPE = JSON
  STRIP_OUTER_ARRAY = TRUE
  COMMENT = 'wrangler d1 execute --json output is a JSON array of rows.';

CREATE STAGE IF NOT EXISTS AI4DATA.RAW.D1_STAGE
  FILE_FORMAT = AI4DATA.RAW.JSON_FF
  COMMENT = 'Internal stage; `snow stage copy out/ @RAW.D1_STAGE` lands here (WS4 02_load.sql).';

-- ----------------------------------------------------------------------------
-- 5. AI4DATA_AGENT role: least privilege, scoped to AI4DATA only
-- ----------------------------------------------------------------------------
CREATE ROLE IF NOT EXISTS AI4DATA_AGENT
  COMMENT = 'Role for the live/rehearsal demo agent. No ACCOUNTADMIN, nothing outside AI4DATA.';

GRANT USAGE ON WAREHOUSE AI4DATA_WH TO ROLE AI4DATA_AGENT;

GRANT USAGE ON DATABASE AI4DATA TO ROLE AI4DATA_AGENT;

GRANT ALL ON SCHEMA AI4DATA.RAW        TO ROLE AI4DATA_AGENT;
GRANT ALL ON SCHEMA AI4DATA.ANALYTICS  TO ROLE AI4DATA_AGENT;
GRANT ALL ON SCHEMA AI4DATA.REHEARSAL  TO ROLE AI4DATA_AGENT;

-- Cover objects the pipeline (WS4) creates after this script runs, so the
-- agent role doesn't need re-granting on every new table/view/stage.
GRANT ALL ON FUTURE TABLES       IN SCHEMA AI4DATA.RAW       TO ROLE AI4DATA_AGENT;
GRANT ALL ON FUTURE VIEWS        IN SCHEMA AI4DATA.RAW       TO ROLE AI4DATA_AGENT;
GRANT ALL ON FUTURE STAGES       IN SCHEMA AI4DATA.RAW       TO ROLE AI4DATA_AGENT;
GRANT ALL ON FUTURE FILE FORMATS IN SCHEMA AI4DATA.RAW       TO ROLE AI4DATA_AGENT;
GRANT ALL ON FUTURE TABLES       IN SCHEMA AI4DATA.ANALYTICS TO ROLE AI4DATA_AGENT;
GRANT ALL ON FUTURE VIEWS        IN SCHEMA AI4DATA.ANALYTICS TO ROLE AI4DATA_AGENT;
GRANT ALL ON FUTURE TABLES       IN SCHEMA AI4DATA.REHEARSAL TO ROLE AI4DATA_AGENT;
GRANT ALL ON FUTURE VIEWS        IN SCHEMA AI4DATA.REHEARSAL TO ROLE AI4DATA_AGENT;

-- AI_CLASSIFY requires this Snowflake-owned database role.
-- Future grants don't cover objects that already exist: the stage and file format above are created
-- by ACCOUNTADMIN in this same script, so the agent role needs explicit grants on them.
GRANT READ, WRITE ON STAGE AI4DATA.RAW.D1_STAGE TO ROLE AI4DATA_AGENT;
GRANT USAGE ON FILE FORMAT AI4DATA.RAW.JSON_FF TO ROLE AI4DATA_AGENT;

GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE AI4DATA_AGENT;

-- No grants are issued on SNOWFLAKE_SAMPLE_DATA or any other database/schema:
-- by default a role sees nothing it wasn't granted, so AI4DATA_AGENT has no
-- visibility outside AI4DATA. Verified by demos/clase-02/snowflake/99_smoke_test.sql.

GRANT ROLE AI4DATA_AGENT TO USER H1SORT;

-- ----------------------------------------------------------------------------
-- Done. Next: run demos/clase-02/snowflake/99_smoke_test.sql with the
-- ai4data_agent connection.
-- ----------------------------------------------------------------------------
