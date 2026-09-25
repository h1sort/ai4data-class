#!/usr/bin/env bash
# WS4: run the full pipeline end to end, timing every step.
#
# Usage:
#   ./run_all.sh                                          # rehearsal shortcut
#   ./run_all.sh <group_code_c2> <group_code_c1> <schema>  # explicit (e.g. the real class)
#
# Rehearsal shortcut uses the two Ensayo groups and workspace.ai4data_rehearsal
# (CLASS2-PLAN.md §9): Ensayo · Clase 2 = YWE57U6B8U, Ensayo · Clase 1 = R57BDNR5ZG.
# For the real class: ./run_all.sh 8P56ZUVE9Q JFQES4AF97 ai4data
#
# Reads D1 (SELECT only) and writes only to workspace.ai4data_raw / <schema>
# in Databricks, as the scoped agent service principal (DATABRICKS_AGENT_TOKEN).
# Never writes to D1. Halts on the first failing step (incl. 04_tests.sh's
# data-quality gate); pass --keep-going to run every step regardless.

set -uo pipefail  # not -e: we want to control exactly where a failure halts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "$SCRIPT_DIR/_lib.sh"

KEEP_GOING=0
ARGS=()
for a in "$@"; do
  if [[ "$a" == "--keep-going" ]]; then KEEP_GOING=1; else ARGS+=("$a"); fi
done
set -- "${ARGS[@]:-}"

ENSAYO_C2_CODE="YWE57U6B8U"
ENSAYO_C1_CODE="R57BDNR5ZG"
REAL_C2_CODE="8P56ZUVE9Q"
REAL_C1_CODE="JFQES4AF97"

if [[ -n "${1:-}" ]]; then
  GROUP_CODE_C2="$1"
  GROUP_CODE_C1="$2"
  SCHEMA="$3"
  require_arg "group_code_c2" "$GROUP_CODE_C2"
  require_arg "group_code_c1" "$GROUP_CODE_C1"
  require_arg "schema" "$SCHEMA"
else
  GROUP_CODE_C2="$ENSAYO_C2_CODE"
  GROUP_CODE_C1="$ENSAYO_C1_CODE"
  SCHEMA="ai4data_rehearsal"
fi

# Safety: never point the rehearsal schema at the real groups (or vice
# versa) -- catches a copy-paste mistake before it burns pipeline time.
if [[ "$SCHEMA" == "ai4data_rehearsal" && ( "$GROUP_CODE_C2" == "$REAL_C2_CODE" || "$GROUP_CODE_C1" == "$REAL_C1_CODE" ) ]]; then
  echo "error: schema is ai4data_rehearsal but a real group code was given -- refusing" >&2
  exit 2
fi
if [[ "$SCHEMA" == "ai4data" && ( "$GROUP_CODE_C2" == "$ENSAYO_C2_CODE" || "$GROUP_CODE_C1" == "$ENSAYO_C1_CODE" ) ]]; then
  echo "error: schema is ai4data (class) but an Ensayo group code was given -- refusing" >&2
  exit 2
fi

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
CUTOFF="$(date -u +'%Y-%m-%d %H:%M:%S')"

echo "=== WS4 run_all: run_id=$RUN_ID schema=$SCHEMA c2=$GROUP_CODE_C2 c1=$GROUP_CODE_C1 cutoff=$CUTOFF ==="
PIPELINE_T0=$(date +%s)

declare -a STEP_NAMES=()
declare -a STEP_SECONDS=()
FAILED=0

run_step() {
  local name="$1"; shift
  echo ""
  echo "--- $name ---"
  local t0 t1 rc
  t0=$(date +%s)
  "$@"
  rc=$?
  t1=$(date +%s)
  STEP_NAMES+=("$name")
  STEP_SECONDS+=("$((t1 - t0))")
  echo "--- $name done in $((t1 - t0))s (exit $rc) ---"
  if [[ $rc -ne 0 ]]; then
    FAILED=1
    if [[ $KEEP_GOING -eq 0 ]]; then
      echo "error: $name failed, halting (pass --keep-going to override)" >&2
      print_summary
      exit $rc
    fi
  fi
}

print_summary() {
  echo ""
  echo "=== timing summary ==="
  local i total=0
  for i in "${!STEP_NAMES[@]}"; do
    printf '  %-16s %ss\n' "${STEP_NAMES[$i]}" "${STEP_SECONDS[$i]}"
    total=$((total + STEP_SECONDS[i]))
  done
  printf '  %-16s %ss\n' "TOTAL" "$total"
}

run_step "01_extract"     "$SCRIPT_DIR/01_extract.sh" "$GROUP_CODE_C2,$GROUP_CODE_C1" "$RUN_ID"
run_step "02_load"        "$SCRIPT_DIR/02_load.sh" "$RUN_ID"
run_step "03_model"       "$SCRIPT_DIR/03_model.sh" "$SCHEMA" "$GROUP_CODE_C2" "$GROUP_CODE_C1" "$CUTOFF"
run_step "04_tests"       "$SCRIPT_DIR/04_tests.sh" "$SCHEMA" "$GROUP_CODE_C2" "$GROUP_CODE_C1" "$CUTOFF"
run_step "05_ai_classify" "$SCRIPT_DIR/05_ai_classify.sh" "$SCHEMA"

if command -v uv >/dev/null 2>&1; then
  run_step "06_jev" uv run "$SCRIPT_DIR/06_jev.py" --schema "$SCHEMA"
else
  run_step "06_jev" python3 "$SCRIPT_DIR/06_jev.py" --schema "$SCHEMA"
fi

run_step "07_compare" "$SCRIPT_DIR/07_compare.sh" "$SCHEMA"

echo ""
echo "--- fallback export ---"
t0=$(date +%s)
FALLBACK_DIR="$PIPELINE_DIR/out/fallback/$RUN_ID"
if command -v uv >/dev/null 2>&1; then
  uv run "$SCRIPT_DIR/_export_fallback.py" --schema "$SCHEMA" --out-dir "$FALLBACK_DIR"
else
  python3 "$SCRIPT_DIR/_export_fallback.py" --schema "$SCHEMA" --out-dir "$FALLBACK_DIR"
fi
t1=$(date +%s)
STEP_NAMES+=("fallback_export")
STEP_SECONDS+=("$((t1 - t0))")
echo "fallback CSVs -> $FALLBACK_DIR ($((t1 - t0))s)"

PIPELINE_T1=$(date +%s)
print_summary
echo ""
echo "=== WS4 run_all: total wall time $((PIPELINE_T1 - PIPELINE_T0))s (run_id=$RUN_ID) ==="
if [[ $FAILED -ne 0 ]]; then
  echo "=== one or more steps failed (ran with --keep-going) ==="
  exit 1
fi
