# Datos del momento de escala (Clase 2)

Esta carpeta está vacía en el repositorio a propósito: los archivos pesan unos 181 MB y no van en git.

Aquí van los viajes de taxi amarillo de Nueva York de enero a marzo de 2025 (11,198,026 viajes en formato Parquet), publicados por la [NYC Taxi & Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page).

## Cómo conseguirlos

Desde `demos/clase-02/scale/`:

```bash
python download-data.py
```

Solo usa la biblioteca estándar de Python, así que funciona en macOS, Linux y Windows. Puedes volver a ejecutarlo: se salta los archivos que ya están completos.

Al terminar, esta carpeta tiene:

```
yellow_tripdata_2025-01.parquet
yellow_tripdata_2025-02.parquet
yellow_tripdata_2025-03.parquet
```

## Y después

```bash
./build_sqlite.sh   # crea taxi.sqlite (almacenamiento por filas) y taxi.duckdb
./run.sh            # la misma consulta en SQLite y en DuckDB, con tiempos
```

`build_sqlite.sh` y `run.sh` necesitan bash y el CLI de `duckdb`. En Windows, usa WSL o Git Bash.

Si guardaste los archivos en otra carpeta, indícala con `TAXI_DATA_DIR=/ruta/a/tus/parquet ./run.sh`.
