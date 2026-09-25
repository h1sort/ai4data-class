#!/usr/bin/env bash
# WS4 step 7: comparison, routing table, injections, payoff.
#
# Usage:
#   ./07_compare.sh <schema>

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "$SCRIPT_DIR/_lib.sh"

SCHEMA="${1:-}"
require_arg "schema" "$SCHEMA"

load_env
render_and_run "$SCRIPT_DIR/07_compare.sql" "SCHEMA=$SCHEMA"
