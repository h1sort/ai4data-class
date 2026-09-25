#!/usr/bin/env bash
# WS4 step 5: ai_classify persona + categoria_tarea, one set-based statement.
#
# Usage:
#   ./05_ai_classify.sh <schema>

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "$SCRIPT_DIR/_lib.sh"

SCHEMA="${1:-}"
require_arg "schema" "$SCHEMA"

load_env
t0=$(date +%s)
render_and_run "$SCRIPT_DIR/05_ai_classify.sql" "SCHEMA=$SCHEMA"
t1=$(date +%s)
echo "[ai_classify] done in $((t1 - t0))s"
