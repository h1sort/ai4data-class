#!/usr/bin/env bash
# WS4 step 3: build dim_participante + fct_respuestas in the target schema.
#
# Usage:
#   ./03_model.sh <schema> <group_code_c2> <group_code_c1> [cutoff_utc]
#
#   schema:         ai4data_rehearsal | ai4data
#   group_code_c2:  Clase 2 group code
#   group_code_c1:  companion Class 1 group code (rol_declarado_c1 source)
#   cutoff_utc:     'YYYY-MM-DD HH:MM:SS' UTC, default: now

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "$SCRIPT_DIR/_lib.sh"

SCHEMA="${1:-}"
GROUP_CODE_C2="${2:-}"
GROUP_CODE_C1="${3:-}"
CUTOFF="${4:-$(date -u +'%Y-%m-%d %H:%M:%S')}"
require_arg "schema" "$SCHEMA"
require_arg "group_code_c2" "$GROUP_CODE_C2"
require_arg "group_code_c1" "$GROUP_CODE_C1"
guard_schema_group "$SCHEMA" "$GROUP_CODE_C2" "$GROUP_CODE_C1"

load_env
echo "[model] schema=$SCHEMA c2=$GROUP_CODE_C2 c1=$GROUP_CODE_C1 cutoff=$CUTOFF"
render_and_run "$SCRIPT_DIR/03_model.sql" \
  "SCHEMA=$SCHEMA" "GROUP_CODE_C2=$GROUP_CODE_C2" "GROUP_CODE_C1=$GROUP_CODE_C1" "CUTOFF=$CUTOFF"
