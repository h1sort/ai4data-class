#!/usr/bin/env bash
# Reconcile the C1 models against a same-cutoff D1 aggregate without returning
# participant identifiers. Usage:
#   ./04_c1_tests.sh <schema> <group_code_c1> <cutoff_utc> [run_id]
#
# run_id (WS0, Class 3): optional; when given, this stage's loaded_at/cutoff
# and D1 source counts are also appended to workspace.<schema>.etl_snapshots
# (05_snapshot.sql) -- the durable record the freshness demo reads, since the
# cutoff otherwise only lives in a Delta table COMMENT and the D1 counts only
# in this script's terminal output.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib.sh"

SCHEMA="${1:-}"
GROUP_CODE_C1="${2:-}"
CUTOFF="${3:-}"
RUN_ID="${4:-manual}"
require_arg "schema" "$SCHEMA"
require_arg "group_code_c1" "$GROUP_CODE_C1"
require_arg "cutoff_utc" "$CUTOFF"
if [[ ! "$SCHEMA" =~ ^(ai4data|ai4data_rehearsal)$ ]]; then
  echo "error: schema must be ai4data or ai4data_rehearsal" >&2
  exit 2
fi
if [[ ! "$GROUP_CODE_C1" =~ ^[A-Z0-9]{10}$ ]]; then
  echo "error: invalid Class 1 group code" >&2
  exit 2
fi
if [[ ! "$CUTOFF" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}[[:space:]][0-9]{2}:[0-9]{2}:[0-9]{2}$ ]]; then
  echo "error: cutoff must be UTC 'YYYY-MM-DD HH:MM:SS'" >&2
  exit 2
fi
guard_schema_group "$SCHEMA" "$GROUP_CODE_C1"

echo "[c1_tests] fetching D1 response and participant counts at cutoff $CUTOFF"
D1_COUNTS_JSON="$(cd "$D1_REPO" && npx wrangler d1 execute h1sort-chat --remote --json --command "
  WITH answers AS (
    SELECT v.voter_hash FROM poll_votes v
    JOIN polls p ON p.id = v.poll_id JOIN poll_groups g ON g.id = p.group_id
    WHERE g.code = '$GROUP_CODE_C1' AND v.created_at <= '$CUTOFF'
    UNION ALL
    SELECT t.voter_hash FROM poll_text_answers t
    JOIN polls p ON p.id = t.poll_id JOIN poll_groups g ON g.id = p.group_id
    WHERE g.code = '$GROUP_CODE_C1' AND t.created_at <= '$CUTOFF'
  )
  SELECT COUNT(*) AS answer_count, COUNT(DISTINCT voter_hash) AS participant_count
  FROM answers
")"
read -r D1_ANSWER_COUNT D1_PARTICIPANT_COUNT < <(
  python3 -c '
import json, sys
payload = json.load(sys.stdin)
row = payload[0]["results"][0]
print(int(row["answer_count"]), int(row["participant_count"]))
' <<< "$D1_COUNTS_JSON"
)
echo "[c1_tests] D1 answers=$D1_ANSWER_COUNT participants=$D1_PARTICIPANT_COUNT"

load_env
OUT_FILE="$(mktemp -t c1_tests_out_XXXXXX)"
trap 'rm -f "$OUT_FILE"' EXIT
render_and_run "$SCRIPT_DIR/04_c1_tests.sql" \
  "SCHEMA=$SCHEMA" \
  "D1_ANSWER_COUNT=$D1_ANSWER_COUNT" \
  "D1_PARTICIPANT_COUNT=$D1_PARTICIPANT_COUNT" | tee "$OUT_FILE"

set +e
python3 - "$OUT_FILE" <<'PYEOF'
import re
import sys

text = open(sys.argv[1], encoding="utf-8").read()
blocks = re.split(r"\n(?=\[\d+/\d+\] )", text)
failures = []
seen = 0
for block in blocks:
    lines = block.splitlines()
    sep_idx = next((i for i, line in enumerate(lines) if re.match(r"^-+\+-+$", line.strip())), None)
    if sep_idx is None or sep_idx + 1 >= len(lines) or "|" not in lines[sep_idx + 1]:
        continue
    name, _, value = lines[sep_idx + 1].rpartition("|")
    try:
        violations = int(value.strip())
    except ValueError:
        continue
    seen += 1
    if violations:
        failures.append((name.strip(), violations))
if not seen:
    print("[c1_tests] could not parse any test result; treating as FAIL", file=sys.stderr)
    sys.exit(1)
if failures:
    print("[c1_tests] FAIL:")
    for name, count in failures:
        print(f"  - {name}: {count}")
    sys.exit(1)
print("[c1_tests] all C1 reconciliation, uniqueness, and aggregate checks PASS")
PYEOF
TEST_STATUS=$?
set -e

LOADED_AT="$(date -u +'%Y-%m-%d %H:%M:%S')"
STATUS_LABEL="PASS"
[[ $TEST_STATUS -eq 0 ]] || STATUS_LABEL="FAIL"
echo "[c1_tests] recording snapshot: run_id=$RUN_ID loaded_at=$LOADED_AT status=$STATUS_LABEL"
render_and_run "$SCRIPT_DIR/05_snapshot.sql" \
  "SCHEMA=$SCHEMA" "RUN_ID=$RUN_ID" "DATASET=class1" \
  "GROUP_CODES=$GROUP_CODE_C1" "CUTOFF=$CUTOFF" "LOADED_AT=$LOADED_AT" \
  "D1_VOTES_CONFIANZA=NULL" "D1_TEXT_PUESTO=NULL" "D1_TEXT_TAREA=NULL" \
  "D1_C1_ANSWERS=$D1_ANSWER_COUNT" "D1_C1_PARTICIPANTS=$D1_PARTICIPANT_COUNT" \
  "STATUS=$STATUS_LABEL"

exit $TEST_STATUS
