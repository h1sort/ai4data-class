#!/usr/bin/env bash
# WS4 step 1: extract poll data from D1, filtered by group code(s), into
# out/<run_id>/*.ndjson (gitignored). One file per allowed table (see
# CLASS2-PLAN.md §4.4): poll_groups, polls, poll_options, poll_votes,
# poll_text_answers. Never touches conversations/messages/auth tables.
#
# Usage:
#   ./01_extract.sh <group_codes_csv> <run_id>
#
# group_codes_csv: one or more poll_groups.code, comma-separated, no spaces.
#   For the payoff join you need BOTH the Clase 2 group and its companion
#   Class 1 group, e.g.:
#     rehearsal: YWE57U6B8U,R57BDNR5ZG   (Ensayo · Clase 2, Ensayo · Clase 1)
#     class:     8P56ZUVE9Q,JFQES4AF97   (Clase 2, Class 1 -- Class 1 is READ ONLY)
# run_id: a label for this extraction run, e.g. $(date -u +%Y%m%dT%H%M%SZ).
#         Used as the output subfolder and later as the Volume landing path.
#
# Output is NDJSON (one JSON object per line) so 02_load.sh can read it with
# read_files(format=>'json') without needing multiLine mode.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "$SCRIPT_DIR/_lib.sh"

GROUP_CODES="${1:-}"
RUN_ID="${2:-}"
require_arg "group_codes_csv" "$GROUP_CODES"
require_arg "run_id" "$RUN_ID"

OUT_DIR="$PIPELINE_DIR/out/$RUN_ID"
mkdir -p "$OUT_DIR"

# Build a SQL IN-list: 'A','B'. Guard against foreign-group leakage by never
# building this list from anything but the caller's explicit argument.
IFS=',' read -ra CODES <<< "$GROUP_CODES"
IN_LIST=""
for c in "${CODES[@]}"; do
  IN_LIST="${IN_LIST}'$(printf '%s' "$c" | sed "s/'/''/g")',"
done
IN_LIST="${IN_LIST%,}"

extract_table() {
  local name="$1" sql="$2"
  local outfile="$OUT_DIR/${name}.ndjson"
  echo "[extract] $name"
  (cd "$D1_REPO" && npx wrangler d1 execute h1sort-chat --remote --json --command "$sql") \
    | python3 -c '
import json, sys
data = json.load(sys.stdin)
rows = data[0]["results"]
for r in rows:
    print(json.dumps(r, ensure_ascii=False))
' > "$outfile"
  echo "  -> $outfile ($(wc -l < "$outfile" | tr -d " ") rows)"
}

t0=$(date +%s)

extract_table "poll_groups" \
  "SELECT id, title, code, created_at FROM poll_groups WHERE code IN ($IN_LIST)"

extract_table "polls" \
  "SELECT p.id, p.group_id, p.code, p.question, p.kind, p.max_length, p.status, p.created_at, p.updated_at, p.opened_at, p.closed_at
   FROM polls p JOIN poll_groups g ON g.id = p.group_id
   WHERE g.code IN ($IN_LIST)"

extract_table "poll_options" \
  "SELECT o.id, o.poll_id, o.label, o.position
   FROM poll_options o JOIN polls p ON p.id = o.poll_id JOIN poll_groups g ON g.id = p.group_id
   WHERE g.code IN ($IN_LIST)"

extract_table "poll_votes" \
  "SELECT v.id, v.poll_id, v.option_id, v.voter_hash, v.created_at
   FROM poll_votes v JOIN polls p ON p.id = v.poll_id JOIN poll_groups g ON g.id = p.group_id
   WHERE g.code IN ($IN_LIST)"

extract_table "poll_text_answers" \
  "SELECT t.id, t.poll_id, t.voter_hash, t.body, t.created_at
   FROM poll_text_answers t JOIN polls p ON p.id = t.poll_id JOIN poll_groups g ON g.id = p.group_id
   WHERE g.code IN ($IN_LIST)"

t1=$(date +%s)
echo "[extract] done in $((t1 - t0))s -> $OUT_DIR"
