#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Comandos de escenario: uv run demos/clase-02/live.py --help."""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sql_module():
    spec = importlib.util.spec_from_file_location("class_sql", HERE / "databricks/run_sql.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_environment():
    runner = sql_module()
    if (ROOT / ".env").is_file():
        runner.load_dotenv(ROOT / ".env")
    # Use the same scoped identity as the ETL, never silently fall back to admin.
    if os.environ.get("DATABRICKS_AGENT_TOKEN"):
        os.environ["DATABRICKS_TOKEN"] = os.environ["DATABRICKS_AGENT_TOKEN"]
    else:
        os.environ.pop("DATABRICKS_TOKEN", None)
    return runner


def run_script(relative: str, *args: str) -> int:
    path = HERE / relative
    if not path.is_file():
        print(f"Falta el script: {path.relative_to(ROOT)}", file=sys.stderr)
        return 2
    return subprocess.run(["bash", str(path), *args], cwd=ROOT).returncode


def preflight(remote: bool) -> int:
    runner = load_environment()
    checks: list[tuple[str, bool]] = []
    for binary in ("bash", "uv", "node", "npx", "databricks", "sqlite3", "duckdb"):
        checks.append((f"CLI {binary}", shutil.which(binary) is not None))
    source = Path(os.environ.get("D1_REPO", str(ROOT.parent / "h1sort-website")))
    checks.append(("checkout D1 (D1_REPO)", source.is_dir()))
    for relative in ("scale/taxi.sqlite", "scale/taxi.duckdb", "scale/query.sql"):
        path = HERE / relative
        checks.append((relative, path.is_file() and path.stat().st_size > 0))
    for key in ("DATABRICKS_HOST", "DATABRICKS_AGENT_TOKEN", "TYPESAFE_API_KEY"):
        checks.append((f"{key} configurada (valor oculto)", bool(os.environ.get(key))))
    for name in ("01_business_analytics", "02_ml_classifier", "03_llm_jev"):
        checks.append((f"notebook {name}", (HERE / "notebooks" / f"{name}.ipynb").is_file()))
    for label, good in checks:
        print(f"{'OK   ' if good else 'FALTA'} {label}", flush=True)
    ok = all(good for _, good in checks)
    if remote:
        print("\nComprobación remota: lectura D1 y SELECT 1 en Databricks.", flush=True)
        poll_ok = run_script("pipeline/poll.sh") == 0
        dbx_ok = False
        if os.environ.get("DATABRICKS_HOST") and os.environ.get("DATABRICKS_TOKEN"):
            dbx_ok = runner.run_one("SELECT 1 AS conexion", runner.DEFAULT_WAREHOUSE_ID, "workspace", 1, 1)
        ok = ok and poll_ok and dbx_ok
        print("Jev, notebook compute y Genie requieren además su ensayo específico; SELECT 1 no los valida.")
    else:
        print("\nSolo comprobación local. Añade --remote para probar D1 y Databricks sin modificar datos.")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("preflight", help="Verifica archivos, herramientas y configuración sin mostrar claves")
    p.add_argument("--remote", action="store_true", help="También prueba lecturas D1 y Databricks")
    commands.add_parser("poll", help="Distribución agregada de confianza en la encuesta de hoy")
    p = commands.add_parser("scale", help="Misma consulta NYC, un motor y un tiempo")
    p.add_argument("--engine", choices=("sqlite", "duckdb"), required=True)
    p = commands.add_parser("etl", help="Extrae, carga, modela y prueba; termina antes de clasificación")
    p.add_argument("--dataset", choices=("class1", "class2"), required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        return preflight(args.remote)
    if args.command == "poll":
        return run_script("pipeline/poll.sh")
    if args.command == "scale":
        return run_script("scale/run_engine.sh", "--engine", args.engine)
    if args.command == "etl":
        return run_script("pipeline/etl_only.sh", "--dataset", args.dataset)
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nDemo interrumpida.", file=sys.stderr)
        raise SystemExit(130)
