#!/usr/bin/env bash
# Read-only CLI view of today's bounded Clase 2 confidence poll aggregate.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib.sh"

command -v npx >/dev/null 2>&1 || { echo "error: npx is required" >&2; exit 2; }
command -v python3 >/dev/null 2>&1 || { echo "error: python3 is required" >&2; exit 2; }
if [[ ! -d "$D1_REPO" ]]; then
  echo "error: D1 repository not found: set D1_REPO or check the sibling h1sort-website checkout" >&2
  exit 2
fi

SQL="$(cat "$SCRIPT_DIR/poll_aggregate.sql")"
echo "[poll] read-only D1 aggregate (group 8P56ZUVE9Q, poll XF97N39)"
RESULT="$(cd "$D1_REPO" && npx wrangler d1 execute h1sort-chat --remote --json --command "$SQL")"
python3 - "$RESULT" <<'PY'
import json
import sys

try:
    payload = json.loads(sys.argv[1])
    rows = payload[0]["results"]
except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
    print(f"error: could not parse Wrangler D1 response: {exc}", file=sys.stderr)
    sys.exit(2)

if not rows:
    print("No poll options found for this poll code.")
    sys.exit(1)

print(rows[0]["pregunta"])
print("opción | votos")
print("-------+------")
total = 0
for row in rows:
    count = int(row["votos"] or 0)
    total += count
    print("{} | {}".format(row["opcion"], count))
print(f"Total de respuestas: {total}")
PY
