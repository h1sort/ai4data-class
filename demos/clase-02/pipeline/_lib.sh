#!/usr/bin/env bash
# Shared helpers for the WS4 pipeline scripts. Source, don't execute:
#   source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_lib.sh"
#
# Provides:
#   PIPELINE_DIR   absolute path of demos/clase-02/pipeline
#   DATABRICKS_DIR absolute path of demos/clase-02/databricks (run_sql.sh lives there)
#   D1_REPO        checkout of h1sort-website (defaults to a sibling repo)
#   load_env       finds and sources the repo-root .env, then forces
#                   DATABRICKS_TOKEN=$DATABRICKS_AGENT_TOKEN -- the whole
#                   pipeline runs as the scoped service principal, exactly
#                   like the live demo (CLASS2-PLAN.md: "Run the whole
#                   pipeline with the agent token"). Never echoes any value.

PIPELINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATABRICKS_DIR="$(cd "$PIPELINE_DIR/../databricks" && pwd)"
CLASS_REPO="$(cd "$PIPELINE_DIR/../../.." && pwd)"
D1_REPO="${D1_REPO:-$(dirname "$CLASS_REPO")/h1sort-website}"

load_env() {
  local dir="$PIPELINE_DIR"
  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/.env" ]]; then
      set -a
      # shellcheck disable=SC1091
      source "$dir/.env"
      set +a
      break
    fi
    dir="$(dirname "$dir")"
  done
  if [[ -z "${DATABRICKS_HOST:-}" || -z "${DATABRICKS_AGENT_TOKEN:-}" ]]; then
    echo "error: DATABRICKS_HOST / DATABRICKS_AGENT_TOKEN not found in .env (never printing values)" >&2
    exit 2
  fi
  # The pipeline always runs as the agent service principal, not the admin PAT
  # that also lives in .env under DATABRICKS_TOKEN.
  export DATABRICKS_TOKEN="$DATABRICKS_AGENT_TOKEN"
}

# run_sql <file.sql> [--catalog X] [--warehouse-id X] [--keep-going]
run_sql() {
  "$DATABRICKS_DIR/run_sql.sh" "$@"
}

# render_and_run <template.sql> KEY=VALUE [KEY=VALUE ...]
# Substitutes every __KEY__ token in the template with VALUE, writes the
# result to a scratch temp file, runs it with run_sql, then deletes the
# scratch file (the template itself is never modified).
render_and_run() {
  local template="$1"; shift
  local tmp
  tmp="$(mktemp -t "ws4_$(basename "$template" .sql)_XXXXXX").sql"
  cp "$template" "$tmp"
  local kv key value esc_value
  for kv in "$@"; do
    key="${kv%%=*}"
    value="${kv#*=}"
    esc_value="$(printf '%s' "$value" | sed -e 's/[&/\]/\\&/g')"
    sed "s/__${key}__/${esc_value}/g" "$tmp" > "${tmp}.new" && mv "${tmp}.new" "$tmp"
  done
  local status=0
  run_sql -f "$tmp" || status=$?
  rm -f "$tmp"
  return $status
}

require_arg() {
  local name="$1" value="$2"
  if [[ -z "$value" ]]; then
    echo "error: missing required argument: $name" >&2
    exit 2
  fi
}
