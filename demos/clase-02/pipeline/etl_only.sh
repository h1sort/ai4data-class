#!/usr/bin/env bash
# Stage ETL for Class 1 analytics or Class 2 poll answers.
# Usage from the repository root: bash demos/clase-02/pipeline/etl_only.sh --dataset class1|class2
# Runs extract -> load -> model -> reconciliation and stops before AI/Jev.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DATASET=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dataset)
      [[ $# -ge 2 ]] || { echo "error: --dataset needs class1 or class2" >&2; exit 2; }
      DATASET="$2"
      shift 2
      ;;
    -h|--help)
      sed -n '1,8p' "$0"
      exit 0
      ;;
    *) echo "error: unknown argument $1" >&2; exit 2 ;;
  esac
done
if [[ "$DATASET" != "class1" && "$DATASET" != "class2" ]]; then
  echo "error: use --dataset class1 or --dataset class2" >&2
  exit 2
fi

C1_CODE="JFQES4AF97"
C2_CODE="8P56ZUVE9Q"
SCHEMA="ai4data"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
CUTOFF="$(date -u +'%Y-%m-%d %H:%M:%S')"

if [[ "$DATASET" == "class1" ]]; then
  GROUP_CODES="$C1_CODE"
else
  # The C2 model uses the optional declared-role overlap with Class 1.
  GROUP_CODES="$C2_CODE,$C1_CODE"
fi

echo "=== stage ETL: dataset=$DATASET schema=$SCHEMA run_id=$RUN_ID cutoff=$CUTOFF ==="
echo "[etl] D1 remains read-only; paid classifiers are not part of this run."
bash "$SCRIPT_DIR/01_extract.sh" "$GROUP_CODES" "$RUN_ID"
bash "$SCRIPT_DIR/02_load.sh" "$RUN_ID"
bash "$SCRIPT_DIR/03_c1_model.sh" "$SCHEMA" "$C1_CODE" "$CUTOFF"
bash "$SCRIPT_DIR/04_c1_tests.sh" "$SCHEMA" "$C1_CODE" "$CUTOFF"

if [[ "$DATASET" == "class2" ]]; then
  bash "$SCRIPT_DIR/03_model.sh" "$SCHEMA" "$C2_CODE" "$C1_CODE" "$CUTOFF"
  bash "$SCRIPT_DIR/04_tests.sh" "$SCHEMA" "$C2_CODE" "$C1_CODE" "$CUTOFF"
fi

echo "=== stage ETL complete: dataset=$DATASET run_id=$RUN_ID ==="
