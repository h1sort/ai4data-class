-- dirty.sql
--
-- The "dirty data" follow-up to the scale moment: min/max pickup timestamp,
-- and how many trips fall outside the nominal Jan-Mar 2025 window this
-- dataset is supposed to cover. Same portability approach as query.sql:
-- identical SQL text, assumes a `trips` table/view is already in scope, and
-- relies on `CAST(... AS VARCHAR)` (or plain TEXT comparison, since ISO
-- timestamps sort lexicographically the same as chronologically) instead of
-- engine-specific date functions.

SELECT
    min(tpep_pickup_datetime) AS recogida_min,
    max(tpep_pickup_datetime) AS recogida_max,
    count(*) AS n_viajes_total,
    sum(
        CASE
            WHEN CAST(tpep_pickup_datetime AS VARCHAR) < '2025-01-01 00:00:00'
              OR CAST(tpep_pickup_datetime AS VARCHAR) >= '2025-04-01 00:00:00'
            THEN 1 ELSE 0
        END
    ) AS n_viajes_fuera_de_rango
FROM trips;
