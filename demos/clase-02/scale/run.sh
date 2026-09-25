#!/usr/bin/env bash
# run.sh
#
# The "scale moment" live demo. Runs the same analytics query (query.sql)
# and the dirty-data query (dirty.sql) against:
#   1) SQLite on taxi.sqlite            -- row store, no indexes
#   2) DuckDB directly on the parquet    -- columnar, reading files as-is
#   3) DuckDB on taxi.duckdb (if built)  -- columnar, materialized on disk
#
# Each combination runs 3 times with `.timer on`, so the native CLI timer
# output is what gets projected. A summary table (median of the 3 "real"
# times) prints at the end in Spanish, for stage.
#
# Requires taxi.sqlite (and, optionally, taxi.duckdb) already built by
# ./build_sqlite.sh. Reads the source parquet directly for step 2, the same
# read-only files build_sqlite.sh uses.
#
# Cache note for stage: the numbers here are WARM-cache numbers (the OS page
# cache already holds these files from the build + earlier test runs). The
# very first query against a freshly booted machine, or right after
# `sudo purge` (drops the page cache on macOS), will be slower -- that is
# the "cold-ish" run worth calling out verbally on stage. This script does
# not force a cold cache itself (that needs `sudo purge`, a password-
# prompting operation intentionally not run here); if you want a true cold
# number before class, run `sudo purge` once, then run this script.
#
# Fallback: `./run.sh --month` limits query.sql (the timed query, not
# dirty.sql, which needs the full range to find dirty dates) to January
# 2025 only, in every engine, for a lower-budget rerun if a stage laptop is
# much slower than the one this was built and measured on. Measured here
# (2026-09-25, warm cache, 3-month scope): run.sh finishes well under the
# 60s target without needing --month -- see CLASS2-PLAN.md Section 9.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${TAXI_DATA_DIR:-$SCRIPT_DIR/data}"   # download with: python download-data.py
if ! ls "$SRC_DIR"/yellow_tripdata_2025-0[123].parquet >/dev/null 2>&1; then
  echo "No se encontraron los parquet en: $SRC_DIR" >&2
  echo "Descárgalos con: python download-data.py (o define TAXI_DATA_DIR)" >&2
  exit 1
fi
SQLITE_DB="$SCRIPT_DIR/taxi.sqlite"
DUCKDB_DB="$SCRIPT_DIR/taxi.duckdb"
QUERY_SQL="$SCRIPT_DIR/query.sql"
DIRTY_SQL="$SCRIPT_DIR/dirty.sql"
RUNS=3
TIMING_LOG="$(mktemp)"
WORKDIR="$(mktemp -d)"
trap 'rm -f "$TIMING_LOG"; rm -rf "$WORKDIR"' EXIT

MONTH_MODE=0
if [ "${1:-}" = "--month" ]; then
  MONTH_MODE=1
fi

if [ "$MONTH_MODE" = "1" ]; then
  SRC_GLOB="$SRC_DIR/yellow_tripdata_2025-01.parquet"
  # query.sql's WHERE clause is `WHERE fare_amount > 0` (appears once) --
  # append the month bound onto it for the timed query only. dirty.sql is
  # left untouched: it needs the full 3-month range to find dirty dates.
  QUERY_SQL_ACTIVE="$WORKDIR/query_month.sql"
  sed 's/WHERE fare_amount > 0/WHERE fare_amount > 0 AND tpep_pickup_datetime < '"'"'2025-02-01'"'"'/' \
    "$QUERY_SQL" > "$QUERY_SQL_ACTIVE"
else
  SRC_GLOB="$SRC_DIR/yellow_tripdata_2025-0[123].parquet"
  QUERY_SQL_ACTIVE="$QUERY_SQL"
fi

hr()      { printf '=%.0s' $(seq 1 64); echo; }
section() { echo; hr; echo "  $1"; hr; }

# Runs one .sql file $RUNS times against one CLI.
# $1=cli (sqlite3|duckdb) $2=db path (empty = in-memory) $3=sql file
# $4=setup SQL run before .timer on (may be empty) $5=label for the summary
run_series() {
  local cli="$1" db="$2" sqlfile="$3" setup="$4" label="$5"
  for i in $(seq 1 "$RUNS"); do
    echo "--- $label -- corrida $i/$RUNS ---"
    local out
    if [ "$cli" = "sqlite3" ]; then
      out="$(sqlite3 "$db" <<SQL
${setup}
.timer on
$(cat "$sqlfile")
SQL
)"
    else
      out="$(duckdb ${db:+"$db"} <<SQL
${setup}
.timer on
$(cat "$sqlfile")
SQL
)"
    fi
    echo "$out"
    # Pull the wall-clock seconds out of the "Run Time ..." timer line
    # (sqlite3: "Run Time: real 0.123 ..."; duckdb: "Run Time (s): real 0.123 ...")
    # and stash it for the median summary at the end.
    local secs
    secs="$(echo "$out" | grep -o 'real [0-9.]*' | tail -1 | awk '{print $2}')"
    echo "$label|$secs" >> "$TIMING_LOG"
    echo
  done
}

median_of() {
  # $1 = label to filter on; prints the median of its recorded seconds.
  grep -F "$1|" "$TIMING_LOG" | cut -d'|' -f2 | sort -n | awk '
    { a[NR]=$1 }
    END {
      if (NR == 0) { print "n/a"; exit }
      mid = int((NR + 1) / 2)
      if (NR % 2 == 1) { printf "%.3f\n", a[mid] }
      else { printf "%.3f\n", (a[mid] + a[mid+1]) / 2 }
    }'
}

if [ "$MONTH_MODE" = "1" ]; then
  echo "Modo --month: query.sql se limita a enero 2025 en los tres motores (respaldo de bajo presupuesto)."
fi

OVERALL_START=$(date +%s)

# ---------------------------------------------------------------------
section "1/3 - SQLite sobre taxi.sqlite (row store, sin indices)"
# ---------------------------------------------------------------------
if [ ! -f "$SQLITE_DB" ]; then
  echo "No existe $SQLITE_DB. Corre ./build_sqlite.sh primero." >&2
  exit 1
fi

echo ">> propina promedio (%) por hora y tipo de pago (query.sql)"
run_series sqlite3 "$SQLITE_DB" "$QUERY_SQL_ACTIVE" "" "SQLite - query.sql"

echo ">> fechas sucias (dirty.sql, siempre rango completo)"
run_series sqlite3 "$SQLITE_DB" "$DIRTY_SQL" "" "SQLite - dirty.sql"

# ---------------------------------------------------------------------
section "2/3 - DuckDB directo sobre los Parquet (columnar, sin materializar)"
# ---------------------------------------------------------------------
PARQUET_SETUP="CREATE VIEW trips AS SELECT * FROM read_parquet('$SRC_GLOB');"
PARQUET_SETUP_FULL="CREATE VIEW trips AS SELECT * FROM read_parquet('$SRC_DIR/yellow_tripdata_2025-0[123].parquet');"

echo ">> propina promedio (%) por hora y tipo de pago (query.sql)"
run_series duckdb "" "$QUERY_SQL_ACTIVE" "$PARQUET_SETUP" "DuckDB - Parquet - query.sql"

echo ">> fechas sucias (dirty.sql, siempre rango completo)"
run_series duckdb "" "$DIRTY_SQL" "$PARQUET_SETUP_FULL" "DuckDB - Parquet - dirty.sql"

# ---------------------------------------------------------------------
if [ -f "$DUCKDB_DB" ]; then
  section "3/3 - DuckDB sobre taxi.duckdb (columnar, materializado en disco)"

  echo ">> propina promedio (%) por hora y tipo de pago (query.sql)"
  run_series duckdb "$DUCKDB_DB" "$QUERY_SQL_ACTIVE" "" "DuckDB - taxi.duckdb - query.sql"

  echo ">> fechas sucias (dirty.sql, siempre rango completo)"
  run_series duckdb "$DUCKDB_DB" "$DIRTY_SQL" "" "DuckDB - taxi.duckdb - dirty.sql"
else
  echo
  echo "(taxi.duckdb no existe -- corre ./build_sqlite.sh --with-duckdb para incluir este paso opcional)"
fi

OVERALL_END=$(date +%s)
TOTAL=$((OVERALL_END - OVERALL_START))

# ---------------------------------------------------------------------
section "RESUMEN - mediana de $RUNS corridas (segundos, tiempo real)"
# ---------------------------------------------------------------------
printf "%-38s %10s\n" "Motor / consulta" "Mediana(s)"
hr
for label in \
  "SQLite - query.sql" \
  "SQLite - dirty.sql" \
  "DuckDB - Parquet - query.sql" \
  "DuckDB - Parquet - dirty.sql" \
  "DuckDB - taxi.duckdb - query.sql" \
  "DuckDB - taxi.duckdb - dirty.sql"
do
  if grep -qF "$label|" "$TIMING_LOG"; then
    printf "%-38s %10s\n" "$label" "$(median_of "$label")"
  fi
done
hr
echo "Tiempo total de run.sh: ${TOTAL}s (objetivo: menor a 60s)"
