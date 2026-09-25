#!/usr/bin/env bash
# Thin launcher for run_sql.py. See that file for behavior/flags.
# Usage: ./run_sql.sh -f file.sql | -q "SELECT 1" [--warehouse-id ID] [--catalog NAME]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/run_sql.py" "$@"
