#!/usr/bin/env python3
"""Download the NYC yellow-taxi trips (Jan–Mar 2025) for the Class 2 scale demo.

Only uses the Python standard library, so it runs the same on macOS, Linux and
Windows:

    python download-data.py            # or: uv run download-data.py

Files come from the NYC Taxi & Limousine Commission's public site and land in
./data next to this script (about 181 MB). Files that are already complete are
skipped, so the script is safe to rerun.
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
DATA_DIR = Path(__file__).resolve().parent / "data"

# Expected sizes in bytes as published by TLC and measured on 2026-09-25.
# If TLC republishes a month, the size changes and the class numbers may too.
FILES = {
    "yellow_tripdata_2025-01.parquet": 59_158_238,
    "yellow_tripdata_2025-02.parquet": 60_343_086,
    "yellow_tripdata_2025-03.parquet": 69_964_745,
}

CHUNK = 1024 * 1024


def download(name: str, expected: int) -> bool:
    target = DATA_DIR / name
    if target.exists() and target.stat().st_size == expected:
        print(f"ok        {name} (ya descargado)")
        return True

    partial = target.with_suffix(target.suffix + ".part")
    url = f"{BASE_URL}/{name}"
    print(f"descargando {name} …")
    try:
        with urllib.request.urlopen(url, timeout=60) as response, partial.open("wb") as out:
            total = int(response.headers.get("Content-Length") or 0)
            done = 0
            while chunk := response.read(CHUNK):
                out.write(chunk)
                done += len(chunk)
                if total:
                    print(f"\r  {done / 1e6:6.1f} / {total / 1e6:.1f} MB", end="", flush=True)
        print()
    except OSError as error:
        partial.unlink(missing_ok=True)
        print(f"error     {name}: {error}", file=sys.stderr)
        return False

    size = partial.stat().st_size
    partial.replace(target)
    if size != expected:
        print(
            f"aviso     {name}: {size:,} bytes, se esperaban {expected:,}. "
            "TLC pudo haber republicado el archivo; los tiempos y conteos pueden diferir de la clase.",
            file=sys.stderr,
        )
    else:
        print(f"ok        {name}")
    return True


def main() -> int:
    DATA_DIR.mkdir(exist_ok=True)
    results = [download(name, size) for name, size in FILES.items()]
    if not all(results):
        print("\nAlgunas descargas fallaron. Vuelve a ejecutar el script.", file=sys.stderr)
        return 1
    print(f"\nListo: datos en {DATA_DIR}")
    print("Siguiente paso: ./build_sqlite.sh (crea taxi.sqlite y taxi.duckdb) y luego ./run.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
