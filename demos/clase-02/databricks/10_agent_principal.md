# Least-privilege agent principal for Class 2 (Databricks)

**Status: EXECUTED 2026-09-25 by the orchestrator with human approval** (see CLASS2-PLAN.md §10). The extra step needed was `PATCH /api/2.0/permissions/authorization/tokens` granting the SP `CAN_USE`, before `create-obo-token` would work. Original notes follow. Per CLASS2-PLAN.md
§4 guardrail 1 and §6 WS2, creating the service principal, granting it
anything, and minting its token all require human approval first. This file
is that approval request: the exact commands, in order, ready to paste.

## Feasibility: likely yes, not yet proven by an actual create

Investigated 2026-09-25 without creating anything, using read-only probes:

| Check | Result | What it tells us |
|---|---|---|
| `databricks service-principals list -o json` | `[]` (200 OK, empty — 0 principals exist yet) | The workspace-level SCIM `ServicePrincipals` API is reachable and enabled for this token. If the feature were disabled for this workspace/edition, this call would typically error rather than return an empty list. |
| `SELECT DISTINCT sku_name FROM system.billing.usage` | `PREMIUM_ALL_PURPOSE_SERVERLESS_COMPUTE_US_EAST_OHIO`, `PREMIUM_DATABRICKS_STORAGE_US_EAST_OHIO`, `PREMIUM_JOBS_SERVERLESS_COMPUTE_US_EAST_OHIO`, `PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_US_EAST_OHIO`, `PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST_OHIO`, `PUBLIC_CONNECTIVITY_DATA_PROCESSED_US_EAST_OHIO`, `INTER_REGION_EGRESS_FROM_US_EAST_OHIO` | All SKUs are `PREMIUM_*`. This is a Premium-tier workspace (a trial, per §3), **not** the stripped-down Databricks Free Edition, which is the edition known to block service-principal creation and several admin APIs. |
| `databricks current-user me` → `groups` | member of `admins` (id `82454096856631`) | The account is a workspace admin, which is the permission level `service-principals create`, `token-management create-obo-token`, and `warehouses update-permissions` all require. |
| `databricks warehouses get-permissions 90f6df4041b446b7` | `carlosharo17@gmail.com` → `IS_OWNER` | Confirms admin/owner rights on the warehouse we'd grant `CAN_USE` on. |
| `databricks account service-principals list` | `Error: invalid Databricks Account configuration - host incorrect or account_id missing` | Expected and harmless: that's the **account-level** command, which needs separate account-console credentials we don't have configured. It does **not** block the **workspace-level** `databricks service-principals create` command below, which is a different API (workspace SCIM) and is what we actually need — a principal scoped to this one workspace. |
| `SHOW GRANTS ON CATALOG workspace` | 0 rows | Clean slate: no stray grants to account for before adding the agent's. |

**Conclusion:** every signal available without actually creating the object points
to "this will work" — Premium tier, SCIM reachable, admin rights confirmed, no
edition-restriction errors anywhere. The only way to be 100% certain is to run
`service-principals create`, which is exactly the step gated on human approval.

## Plan: what the agent principal can and can't do

- Scope: **only** `workspace.ai4data_raw`, `workspace.ai4data`,
  `workspace.ai4data_rehearsal` (`USE CATALOG` on `workspace` is required by
  Unity Catalog to reach any schema in it, but no catalog-wide read/write/create
  privilege is granted — only the three schemas get `USE SCHEMA` +
  `CREATE TABLE` + `SELECT` + `MODIFY`, and only `ai4data_raw` gets volume
  read/write, since `landing` is the only volume in scope).
- Compute: `CAN_USE` on warehouse `90f6df4041b446b7` only (no `CAN_MANAGE`, so
  it can't change the warehouse's own config or size).
- Everything else in the workspace (other catalogs, other warehouses,
  workspace settings, users/groups, tokens) stays out of reach — it never gets
  `admins` group membership or any account-level role.
- The smoke test in `99_smoke_test.sql` includes a probe that the resulting
  token **cannot** read `workspace.default` or `samples`, to verify the grants
  actually constrain it (not just that they were issued).

## Commands, in order (pending human approval)

### 1. Create the service principal

```bash
set -a; source .env; set +a
databricks service-principals create --display-name "ai4data-agent" -o json
```

Capture two fields from the JSON response: `applicationId` (a UUID — used in
every `GRANT`/permission call below) and `id` (the numeric SCIM id, only
needed if we later want to `databricks service-principals get/delete` it by
id). Neither is secret; they're identifiers, not credentials.

### 2. Grant Unity Catalog privileges, schema by schema

Run via `./run_sql.sh -q "..."` (or a small `.sql` file), substituting the
real `applicationId` for `<APP_ID>`:

```sql
GRANT USE CATALOG ON CATALOG workspace TO `<APP_ID>`;

GRANT USE SCHEMA, CREATE TABLE, SELECT, MODIFY
  ON SCHEMA workspace.ai4data_raw TO `<APP_ID>`;
GRANT USE SCHEMA, CREATE TABLE, SELECT, MODIFY
  ON SCHEMA workspace.ai4data TO `<APP_ID>`;
GRANT USE SCHEMA, CREATE TABLE, SELECT, MODIFY
  ON SCHEMA workspace.ai4data_rehearsal TO `<APP_ID>`;

-- Volume I/O: only ai4data_raw has a volume (landing).
GRANT READ VOLUME, WRITE VOLUME
  ON SCHEMA workspace.ai4data_raw TO `<APP_ID>`;
```

(Schema-level grants cascade to tables/volumes created later in that schema,
which is what lets `02_load.sh`'s `CREATE OR REPLACE TABLE` work without a
fresh grant on every new object.)

### 3. Grant `CAN_USE` on the warehouse

The current ACL (`databricks warehouses get-permissions 90f6df4041b446b7`) has
the owner (`carlosharo17@gmail.com`, `IS_OWNER`), group `users`
(`CAN_USE`, inherited), and group `admins` (`CAN_MANAGE`, inherited). Use
`update-permissions` (merges into the existing ACL), not `set-permissions`
(replaces it wholesale), so we don't touch those entries:

```bash
databricks warehouses update-permissions 90f6df4041b446b7 --json '{
  "access_control_list": [
    {"service_principal_name": "<APP_ID>", "permission_level": "CAN_USE"}
  ]
}'
```

`service_principal_name` takes the application id (same `<APP_ID>` as above).
Worth a `get-permissions` re-check right after, to confirm the new entry
landed as `CAN_USE` and everything else is unchanged.

### 4. Mint the token

```bash
databricks token-management create-obo-token <APP_ID> \
  --comment "ai4data-agent — Class 2 live demo, scoped to workspace.ai4data* schemas" \
  --lifetime-seconds 604800 \
  -o json
```

604800 s = 7 days, enough to cover rehearsals and the live class with margin,
short enough to not be a standing liability after. Adjust if the schedule
slips. **The response's `token_value` is shown exactly once** — Databricks
does not let you retrieve it again. Immediately:

1. Append it to `.env` as `DATABRICKS_AGENT_TOKEN=<value>` (never print it,
   never echo the command that set it, never put it in a commit).
2. Do not paste it into chat/terminal output beyond the one command that
   writes it to `.env` — pipe it there directly rather than copy-pasting a
   value you saw on screen, e.g. capture the JSON to a local file with `-o
   json > /tmp/…json`, read `token_value` out of it with `jq`, append to
   `.env`, then delete the temp file.

### 5. Verify isolation (part of `99_smoke_test.sql`)

With `DATABRICKS_TOKEN` swapped for `DATABRICKS_AGENT_TOKEN` (a separate env,
not the admin one), confirm:
- `SELECT 1 FROM workspace.ai4data.<any table>` (or a schema-listing query)
  succeeds.
- `SHOW TABLES IN workspace.default` and `SHOW TABLES IN samples.*` fail with
  a permission-denied error, not just an empty result.

## Rollback (if we need to undo this later)

```bash
databricks token-management list -o json          # find the token id for APP_ID
databricks token-management delete <token-id>
databricks service-principals delete <numeric id from step 1>
```

Revoking the token or deleting the principal invalidates
`DATABRICKS_AGENT_TOKEN` immediately; remove it from `.env` at the same time.

## If this turns out not to be allowed

If `service-principals create` fails once a human runs it (e.g. an
edition/entitlement error we couldn't see from read-only probes), the fallback
is exactly what guardrail §4.7 already anticipates: run the on-stage demo with
the admin PAT (`DATABRICKS_TOKEN`) and say explicitly on stage that the token
belongs to the admin account and why — no schema-scoped enforcement, so the
`ai4data*`-only boundary would then be "we only write there" by convention and
code review, not by grant. Nothing in `00_setup.sql` or `run_sql.sh` depends
on the service principal existing, so this doesn't block anything else in WS2
or WS4.
