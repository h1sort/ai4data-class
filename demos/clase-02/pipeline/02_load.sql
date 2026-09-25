-- WS4 step 2: load JSON landed in the Unity Catalog volume into
-- workspace.ai4data_raw raw tables. Their explicit source schema is always the same
-- regardless of rehearsal/class (CLASS2-PLAN.md §4.7 guardrail: the demo
-- writes only to workspace.ai4data_raw, workspace.ai4data and
-- workspace.ai4data_rehearsal) -- only the *modeled* layer (03_model.sql)
-- varies by target schema. Idempotent: CREATE OR REPLACE, safe to rerun.
--
-- Parameter (substituted by 02_load.sh): __RUN_ID__ -- the landing subfolder
-- written by 01_extract.sh + uploaded by `databricks fs cp` in 02_load.sh.
--
-- Run with: ./02_load.sh <run_id>   (uploads, then renders + runs this file)

CREATE OR REPLACE TABLE workspace.ai4data_raw.raw_poll_groups
COMMENT 'Raw landing (run __RUN_ID__): poll_groups rows for this run''s group codes only, typed to the stable D1 source schema.'
AS SELECT * FROM read_files(
  '/Volumes/workspace/ai4data_raw/landing/__RUN_ID__/poll_groups.ndjson',
  format => 'json',
  schema => 'id STRING, title STRING, code STRING, created_at STRING'
);

CREATE OR REPLACE TABLE workspace.ai4data_raw.raw_polls
COMMENT 'Raw landing (run __RUN_ID__): polls rows.'
AS SELECT * FROM read_files(
  '/Volumes/workspace/ai4data_raw/landing/__RUN_ID__/polls.ndjson',
  format => 'json',
  schema => 'id STRING, group_id STRING, code STRING, question STRING, kind STRING, max_length INT, status STRING, created_at STRING, updated_at STRING, opened_at STRING, closed_at STRING'
);

CREATE OR REPLACE TABLE workspace.ai4data_raw.raw_poll_options
COMMENT 'Raw landing (run __RUN_ID__): poll_options rows.'
AS SELECT * FROM read_files(
  '/Volumes/workspace/ai4data_raw/landing/__RUN_ID__/poll_options.ndjson',
  format => 'json',
  schema => 'id STRING, poll_id STRING, label STRING, position INT'
);

CREATE OR REPLACE TABLE workspace.ai4data_raw.raw_poll_votes
COMMENT 'Raw landing (run __RUN_ID__): poll_votes rows.'
AS SELECT * FROM read_files(
  '/Volumes/workspace/ai4data_raw/landing/__RUN_ID__/poll_votes.ndjson',
  format => 'json',
  schema => 'id STRING, poll_id STRING, option_id STRING, voter_hash STRING, created_at STRING'
);

CREATE OR REPLACE TABLE workspace.ai4data_raw.raw_poll_text_answers
COMMENT 'Raw landing (run __RUN_ID__): poll_text_answers rows.'
AS SELECT * FROM read_files(
  '/Volumes/workspace/ai4data_raw/landing/__RUN_ID__/poll_text_answers.ndjson',
  format => 'json',
  schema => 'id STRING, poll_id STRING, voter_hash STRING, body STRING, created_at STRING'
);
