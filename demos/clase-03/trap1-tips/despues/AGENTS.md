# Capa semántica — Trampa 1: propinas por forma de pago

Contexto para cualquier agente (OpenCode u otro) que consulte con DuckDB los
parquet de viajes de taxi amarillo de NYC en
`demos/clase-02/scale/data/yellow_tripdata_2025-0{1,2,3}.parquet`.

## Fuente oficial

NYC Taxi & Limousine Commission, *Data Dictionary – Yellow Taxi Trip Records*
(actualizado 18 de marzo de 2025):
https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf
(verificado 2026-09-26).

## `payment_type` — códigos oficiales (citados textualmente del diccionario)

> "A numeric code signifying how the passenger paid for the trip."

| code | label (TLC, texto original) |
|---|---|
| 0 | Flex Fare trip |
| 1 | Credit card |
| 2 | Cash |
| 3 | No charge |
| 4 | Dispute |
| 5 | Unknown |
| 6 | Voided trip |

En nuestros 3 meses de datos (ene–mar 2025, 11.198.026 filas) el código `0`
son 2.263.749 filas (~20,2 % del total) — una porción demasiado grande para
ser solo "Flex Fare" real; trátalo como **cajón de sastre / calidad de dato
desconocida**, no como una categoría de pago interpretable. Repórtalo
siempre que sea material (>1 % de las filas) en vez de ignorarlo o
etiquetarlo con un nombre inventado.

## `tip_amount` — la regla que evita la trampa

> "tip_amount — Tip amount – This field is automatically populated for
> credit card tips. Cash tips are not included." (mismo diccionario TLC)

Consecuencia dura: **`tip_amount` (y por lo tanto cualquier `tip_pct`) solo
es una señal real para `payment_type = 1` (tarjeta).** Para el resto de
los códigos (0, 2, 3, 4, 5, 6) el campo es estructuralmente ~0, no porque
esos pasajeros no den propina, sino porque el dato no se captura ahí.

## Definición de métrica

- `tip_pct` = `tip_amount / fare_amount`, **definida y comparable solo
  cuando `payment_type = 1` y `fare_amount > 0`.**
- `tip_pct` (o cualquier ranking de "quién da más propina") **no está
  definida** para `payment_type` distinto de 1. No la calcules, no la
  compares, no la ordenes de mayor a menor entre formas de pago.

## Instrucciones para el agente

1. Si te preguntan qué forma de pago "deja más propina" o similar:
   responde que **solo el pago con tarjeta (`payment_type = 1`) tiene
   propina registrada** en este dataset; el resto de los códigos no son
   comparables por esta vía (cita la regla de `tip_amount` de arriba).
   No declares un "ganador" entre efectivo/tarjeta/otros basado en
   `tip_amount`.
2. Si es relevante, informa el tamaño del grupo `payment_type = 0`
   (filas y % del total) como advertencia de calidad de dato, citando el
   número exacto que arrojó tu propia consulta.
3. Antes de escribir la respuesta final, verifica que cada número que
   vas a citar en el texto aparezca literalmente en la salida de alguna
   de tus consultas SQL. Si no lo encontrás ahí, no lo escribas.
