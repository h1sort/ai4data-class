#!/usr/bin/env bash
# Build Class 1 respondent, answer, and aggregate tables.
# Usage: ./03_c1_model.sh <schema> <group_code_c1> [cutoff_utc]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib.sh"

SCHEMA="${1:-}"
GROUP_CODE_C1="${2:-}"
CUTOFF="${3:-$(date -u +'%Y-%m-%d %H:%M:%S')}"
require_arg "schema" "$SCHEMA"
require_arg "group_code_c1" "$GROUP_CODE_C1"
if [[ ! "$SCHEMA" =~ ^(ai4data|ai4data_rehearsal)$ ]]; then
  echo "error: schema must be ai4data or ai4data_rehearsal" >&2
  exit 2
fi
if [[ ! "$GROUP_CODE_C1" =~ ^[A-Z0-9]{10}$ ]]; then
  echo "error: invalid Class 1 group code" >&2
  exit 2
fi
guard_schema_group "$SCHEMA" "$GROUP_CODE_C1"

load_env
echo "[c1_model] schema=$SCHEMA group=$GROUP_CODE_C1 cutoff=$CUTOFF"
render_and_run "$SCRIPT_DIR/03_c1_model.sql" \
  "SCHEMA=$SCHEMA" "GROUP_CODE_C1=$GROUP_CODE_C1" "CUTOFF=$CUTOFF"
