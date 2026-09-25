#!/usr/bin/env bash
# WS4 step 2: upload out/<run_id>/*.ndjson to the ai4data_raw landing volume,
# then load them into workspace.ai4data_raw raw tables via read_files().
#
# Usage:
#   ./02_load.sh <run_id>

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "$SCRIPT_DIR/_lib.sh"

RUN_ID="${1:-}"
require_arg "run_id" "$RUN_ID"

OUT_DIR="$PIPELINE_DIR/out/$RUN_ID"
if [[ ! -d "$OUT_DIR" ]]; then
  echo "error: $OUT_DIR not found -- run 01_extract.sh <group_codes> $RUN_ID first" >&2
  exit 2
fi

load_env

VOLUME_PATH="dbfs:/Volumes/workspace/ai4data_raw/landing/$RUN_ID"
echo "[load] uploading $OUT_DIR -> $VOLUME_PATH"
t0=$(date +%s)
databricks fs cp "$OUT_DIR" "$VOLUME_PATH" -r --overwrite
t1=$(date +%s)
echo "[load] upload done in $((t1 - t0))s"

echo "[load] loading raw tables from the volume"
render_and_run "$SCRIPT_DIR/02_load.sql" "RUN_ID=$RUN_ID"
t2=$(date +%s)
echo "[load] raw tables loaded in $((t2 - t1))s"
