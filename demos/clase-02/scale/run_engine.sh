#!/usr/bin/env bash
# One read-only execution of the shared query on one engine.
# Usage: bash demos/clase-02/scale/run_engine.sh --engine sqlite|duckdb
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ENGINE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --engine)
      [[ $# -ge 2 ]] || { echo "error: --engine needs sqlite or duckdb" >&2; exit 2; }
      ENGINE="$2"
      shift 2
      ;;
    -h|--help)
      sed -n '1,5p' "$0"
      exit 0
      ;;
    *) echo "error: unknown argument $1" >&2; exit 2 ;;
  esac
done
if [[ "$ENGINE" != "sqlite" && "$ENGINE" != "duckdb" ]]; then
  echo "error: use --engine sqlite or --engine duckdb" >&2
  exit 2
fi

QUERY="$SCRIPT_DIR/query.sql"
case "$ENGINE" in
  sqlite)
    DB="$SCRIPT_DIR/taxi.sqlite"
    CLI="$(command -v sqlite3 || true)"
    ;;
  duckdb)
    DB="$SCRIPT_DIR/taxi.duckdb"
    CLI="$(command -v duckdb || true)"
    ;;
esac
if [[ -z "$CLI" ]]; then
  echo "error: $ENGINE CLI is not installed" >&2
  exit 2
fi
if [[ ! -s "$DB" ]]; then
  echo "error: database is missing: $DB (see scale/data/README.md)" >&2
  exit 2
fi
if [[ ! -s "$QUERY" ]]; then
  echo "error: shared query is missing: $QUERY" >&2
  exit 2
fi

echo "=== $ENGINE · read-only snapshot · one execution ==="
echo "SQL: $QUERY"
echo "Database: $DB"
if [[ "$ENGINE" == "sqlite" ]]; then
  /usr/bin/time -p "$CLI" -readonly -header -column -cmd ".timer on" "$DB" < "$QUERY"
else
  /usr/bin/time -p "$CLI" -readonly -header -column -cmd ".timer on" "$DB" < "$QUERY"
fi
