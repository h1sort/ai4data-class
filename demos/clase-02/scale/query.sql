-- query.sql
--
-- The "scale moment" analytics query: average tip percentage by pickup hour
-- and payment type, over trips with a positive fare.
--
-- This file is byte-identical SQL for both engines (SQLite via the sqlite3
-- CLI on taxi.sqlite, and DuckDB on taxi.duckdb or directly on the source
-- parquet files). It assumes a table or view named `trips` is already in
-- scope -- run.sh sets that up for each engine:
--   - sqlite3 taxi.sqlite:  `trips` is the real table built by build_sqlite.sh.
--   - duckdb taxi.duckdb:   same, `trips` is the real table.
--   - duckdb on parquet:    run.sh creates `CREATE VIEW trips AS SELECT *
--                            FROM read_parquet(...)` first, so this same
--                            query runs unmodified straight over Parquet.
--
-- Hour extraction note (verified 2026-09-25): after build_sqlite.sh loads
-- data through DuckDB's sqlite extension, tpep_pickup_datetime is stored in
-- taxi.sqlite as TEXT in ISO form 'YYYY-MM-DD HH:MM:SS' (SQLite has no
-- native timestamp type). DuckDB's own TIMESTAMP renders the same way when
-- cast to VARCHAR. So `substr(CAST(col AS VARCHAR), 12, 2)` extracts the
-- 2-digit hour identically in both engines -- no need for SQLite's
-- strftime('%H', col) vs DuckDB's strftime(col, '%H'), whose argument order
-- differs between the two dialects (that would have been the minimal
-- dialect difference otherwise).

SELECT
    CAST(substr(CAST(tpep_pickup_datetime AS VARCHAR), 12, 2) AS INTEGER) AS hora_recogida,
    payment_type AS tipo_pago,
    round(100.0 * avg(tip_amount / fare_amount), 2) AS propina_pct_promedio,
    count(*) AS n_viajes
FROM trips
WHERE fare_amount > 0
GROUP BY hora_recogida, tipo_pago
ORDER BY hora_recogida, tipo_pago;
