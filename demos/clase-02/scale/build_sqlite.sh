#!/usr/bin/env bash
# build_sqlite.sh
#
# Builds demos/clase-02/scale/taxi.sqlite (and, optionally, taxi.duckdb) from
# the NYC yellow taxi parquet files in ./data (download them first with
# `python download-data.py`; override the folder with TAXI_DATA_DIR). The
# parquet files are only read; all derived artifacts land in this folder.
#
# Source (11,198,026 rows across 3 months, ~181 MB of parquet):
#   ./data/yellow_tripdata_2025-0{1,2,3}.parquet
#
# Approach: DuckDB's sqlite extension. We ATTACH a .sqlite file (TYPE sqlite)
# and CREATE TABLE ... AS SELECT straight from read_parquet(). This lets
# DuckDB do the heavy lifting of the Parquet scan while writing rows out in
# SQLite's own file format, so the resulting taxi.sqlite is a completely
# normal, standalone SQLite database -- exactly what sqlite3 CLI opens later.
#
# IMPORTANT / intentional: the `trips` table gets NO indexes. This is the
# whole point of the "scale moment" demo -- taxi.sqlite plays the role of an
# OLTP-ish row store (a plain heap table, row-oriented, untuned) that then
# gets scanned end-to-end for an analytics query. That's the exact failure
# mode we want on stage: a full table scan reading every column of every
# row, contrasted with DuckDB's columnar scan (and Parquet's own columnar
# layout + compression) reading only the columns the query touches.
#
# Usage:
#   ./build_sqlite.sh              # builds taxi.sqlite only
#   ./build_sqlite.sh --with-duckdb  # also builds taxi.duckdb the same way
#
# Both builds are deterministic and can be re-run any time before class;
# they take a few minutes on a laptop for 11.2M rows.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${TAXI_DATA_DIR:-$SCRIPT_DIR/data}"   # download with: python download-data.py
SRC_GLOB="$SRC_DIR/yellow_tripdata_2025-0[123].parquet"
SQLITE_DB="$SCRIPT_DIR/taxi.sqlite"
DUCKDB_DB="$SCRIPT_DIR/taxi.duckdb"

WITH_DUCKDB=0
if [ "${1:-}" = "--with-duckdb" ]; then
  WITH_DUCKDB=1
fi

# Sanity check: the parquet files must be downloaded first.
if ! ls "$SRC_DIR"/yellow_tripdata_2025-0[123].parquet >/dev/null 2>&1; then
  echo "No se encontraron los parquet en: $SRC_DIR" >&2
  echo "Descárgalos con: python download-data.py (o define TAXI_DATA_DIR)" >&2
  exit 1
fi

# The columns kept below are a realistic subset for a row store: the trip
# identity/timing columns, the location and payment dimensions, and the full
# fare breakdown -- enough to run real analytics and joins, not a slimmed
# down "just the columns the demo query needs" table. Two rarely-populated
# surcharge columns (Airport_fee, cbd_congestion_fee) are dropped to keep
# the table realistic-but-trimmed rather than SELECT *.
COLUMNS="
    VendorID,
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    passenger_count,
    trip_distance,
    RatecodeID,
    store_and_fwd_flag,
    PULocationID,
    DOLocationID,
    payment_type,
    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    improvement_surcharge,
    total_amount,
    congestion_surcharge
"

echo "== Building taxi.sqlite =="
rm -f "$SQLITE_DB"
time duckdb <<SQL
INSTALL sqlite;
LOAD sqlite;

ATTACH '$SQLITE_DB' AS sq (TYPE sqlite);

CREATE TABLE sq.trips AS
SELECT $COLUMNS
FROM read_parquet('$SRC_GLOB');

-- No indexes created on purpose -- see header comment above. taxi.sqlite is
-- meant to behave like an untuned OLTP row store, not a warehouse table.
SQL

echo
echo "taxi.sqlite row count:"
sqlite3 "$SQLITE_DB" "SELECT count(*) FROM trips;"
echo "taxi.sqlite file size:"
ls -lh "$SQLITE_DB" | awk '{print $5, $9}'

if [ "$WITH_DUCKDB" = "1" ]; then
  echo
  echo "== Building taxi.duckdb (optional, same columns) =="
  rm -f "$DUCKDB_DB"
  time duckdb "$DUCKDB_DB" <<SQL
CREATE TABLE trips AS
SELECT $COLUMNS
FROM read_parquet('$SRC_GLOB');
SQL
  echo
  echo "taxi.duckdb row count:"
  duckdb "$DUCKDB_DB" -csv -c "SELECT count(*) FROM trips;" | tail -1
  echo "taxi.duckdb file size:"
  ls -lh "$DUCKDB_DB" | awk '{print $5, $9}'
fi

echo
echo "Done."
