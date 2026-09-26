#!/usr/bin/env bash
# WS4 step 4: data-quality tests, incl. reconciliation against D1's own
# counts (fetched fresh here, at the same cutoff used by 03_model.sh, so the
# comparison is apples-to-apples even if new rehearsal answers trickle in
# between steps).
#
# Usage:
#   ./04_tests.sh <schema> <group_code_c2> <group_code_c1> <cutoff_utc> [run_id]
#
# Exits non-zero and prints a FAIL list if any test's violations > 0 (the
# two "info:" rows are exempted -- they're just NULL counts, not failures).
#
# run_id (WS0, Class 3): optional; when given, this stage's loaded_at/cutoff
# and D1 source counts are also appended to workspace.<schema>.etl_snapshots
# (05_snapshot.sql) -- the durable record the freshness demo reads, since the
# cutoff otherwise only lives in a Delta table COMMENT and the D1 counts only
# in this script's terminal output.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "$SCRIPT_DIR/_lib.sh"

SCHEMA="${1:-}"
GROUP_CODE_C2="${2:-}"
GROUP_CODE_C1="${3:-}"
CUTOFF="${4:-}"
RUN_ID="${5:-manual}"
require_arg "schema" "$SCHEMA"
require_arg "group_code_c2" "$GROUP_CODE_C2"
require_arg "group_code_c1" "$GROUP_CODE_C1"
require_arg "cutoff_utc" "$CUTOFF"
guard_schema_group "$SCHEMA" "$GROUP_CODE_C2" "$GROUP_CODE_C1"

echo "[tests] fetching D1 reconciliation counts (cutoff $CUTOFF)"
D1_COUNTS_JSON=$(cd "$D1_REPO" && npx wrangler d1 execute h1sort-chat --remote --json --command "
  SELECT
    (SELECT COUNT(*) FROM poll_votes v JOIN polls p ON p.id = v.poll_id JOIN poll_groups g ON g.id = p.group_id
     WHERE g.code = '$GROUP_CODE_C2' AND p.kind = 'choice' AND v.created_at <= '$CUTOFF') AS votes_confianza,
    (SELECT COUNT(*) FROM poll_text_answers t JOIN polls p ON p.id = t.poll_id JOIN poll_groups g ON g.id = p.group_id
     WHERE g.code = '$GROUP_CODE_C2' AND p.max_length = 120 AND t.created_at <= '$CUTOFF') AS text_puesto,
    (SELECT COUNT(*) FROM poll_text_answers t JOIN polls p ON p.id = t.poll_id JOIN poll_groups g ON g.id = p.group_id
     WHERE g.code = '$GROUP_CODE_C2' AND p.max_length = 280 AND t.created_at <= '$CUTOFF') AS text_tarea
")
read -r D1_VOTES_CONFIANZA D1_TEXT_PUESTO D1_TEXT_TAREA < <(
  echo "$D1_COUNTS_JSON" | python3 -c '
import json, sys
r = json.load(sys.stdin)[0]["results"][0]
print(r["votes_confianza"], r["text_puesto"], r["text_tarea"])
'
)
echo "[tests] D1 counts: confianza=$D1_VOTES_CONFIANZA puesto=$D1_TEXT_PUESTO tarea=$D1_TEXT_TAREA"

load_env
OUT_FILE="$(mktemp -t ws4_tests_out_XXXXXX)"
render_and_run "$SCRIPT_DIR/04_tests.sql" \
  "SCHEMA=$SCHEMA" "GROUP_CODE_C2=$GROUP_CODE_C2" "GROUP_CODE_C1=$GROUP_CODE_C1" \
  "D1_VOTES_CONFIANZA=$D1_VOTES_CONFIANZA" "D1_TEXT_PUESTO=$D1_TEXT_PUESTO" "D1_TEXT_TAREA=$D1_TEXT_TAREA" \
  | tee "$OUT_FILE"

set +e  # capture the python verdict's exit code ourselves; don't let errexit skip cleanup
python3 - "$OUT_FILE" <<'PYEOF'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
# run_sql.py prints one block per statement: "[N/M] <preview>", the aligned
# table (header, a "---+---" separator sized to the widest cell, one data
# row), then a "N row(s), ..." summary line. Column widths vary per test
# name, so locate the separator line structurally instead of guessing widths.
blocks = re.split(r"\n(?=\[\d+/\d+\] )", text)
failures = []
seen_any = False
for b in blocks:
    lines = b.splitlines()
    sep_idx = next((i for i, l in enumerate(lines) if re.match(r"^-+\+-+$", l.strip())), None)
    if sep_idx is None or sep_idx + 1 >= len(lines):
        continue
    data_line = lines[sep_idx + 1]
    if "|" not in data_line:
        continue
    name, _, count_str = data_line.rpartition("|")
    name, count_str = name.strip(), count_str.strip()
    try:
        count = int(count_str)
    except ValueError:
        continue
    seen_any = True
    if count != 0 and not name.startswith("info:"):
        failures.append((name, count))
if not seen_any:
    print("\n[tests] could not parse any test result -- treating as FAIL", file=sys.stderr)
    sys.exit(1)
if failures:
    print("\n[tests] FAIL:")
    for name, count in failures:
        print(f"  - {name}: {count}")
    sys.exit(1)
print("\n[tests] all reconciliation/uniqueness/foreign-group checks PASS")
PYEOF
status=$?

LOADED_AT="$(date -u +'%Y-%m-%d %H:%M:%S')"
STATUS_LABEL="PASS"
[[ $status -eq 0 ]] || STATUS_LABEL="FAIL"
echo "[tests] recording snapshot: run_id=$RUN_ID loaded_at=$LOADED_AT status=$STATUS_LABEL"
render_and_run "$SCRIPT_DIR/05_snapshot.sql" \
  "SCHEMA=$SCHEMA" "RUN_ID=$RUN_ID" "DATASET=class2" \
  "GROUP_CODES=$GROUP_CODE_C2,$GROUP_CODE_C1" "CUTOFF=$CUTOFF" "LOADED_AT=$LOADED_AT" \
  "D1_VOTES_CONFIANZA=$D1_VOTES_CONFIANZA" "D1_TEXT_PUESTO=$D1_TEXT_PUESTO" "D1_TEXT_TAREA=$D1_TEXT_TAREA" \
  "D1_C1_ANSWERS=NULL" "D1_C1_PARTICIPANTS=NULL" \
  "STATUS=$STATUS_LABEL"

rm -f "$OUT_FILE"
exit $status
