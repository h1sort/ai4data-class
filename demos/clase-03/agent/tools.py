"""Herramientas del agente (import-only, no `uv run` aquí -- lo usa agent.py).

Dos herramientas, tal como las describe CLASE3-PLAN.md WS5:
  1. duckdb_query -- SQL de solo lectura sobre demos/clase-02/scale/data/*.parquet
  2. check_freshness -- compara el conteo vivo en D1 (wrangler, solo lectura,
     igual que demos/clase-02/pipeline/_lib.sh) contra el snapshot cargado en
     Databricks. El lado Databricks lee `workspace.ai4data.etl_snapshots`
     (WS0, ver demos/clase-03/reports/WS0.md): la fila más reciente con
     `status='PASS'` para el dataset pedido, sumando sus tres contadores de
     fuente D1 (confianza + puesto + tarea) para comparar manzanas con
     manzanas contra el conteo vivo de _d1_live_count(). Si la tabla o la
     fila no existen todavía (p.ej. dataset sin ETL corrido), cae a un STUB
     claramente marcado en vez de inventar un número -- misma interfaz que
     antes, editada por WS3 (CLASE3-PLAN.md §WS3, "Freshness").
"""
from __future__ import annotations

import datetime
import importlib.util
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # repo root: ai4data-class/
TAXI_GLOB = str(ROOT / "demos/clase-02/scale/data/*.parquet")
D1_GROUP_C2 = "8P56ZUVE9Q"  # Clase 2 (ver demos/clase-02/data-contract.md)
SNAPSHOT_TABLE = "workspace.ai4data.etl_snapshots"  # WS0's append-only ETL run log (demos/clase-02/pipeline/05_snapshot.sql)


def load_anthropic_key(dev_vars: Path) -> None:
    """Carga ANTHROPIC_API_KEY desde .dev.vars al entorno. Nunca la imprime."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return
    if not dev_vars.is_file():
        raise RuntimeError(f"no se encontró {dev_vars}")
    for line in dev_vars.read_text().splitlines():
        line = line.strip()
        if line.startswith("ANTHROPIC_API_KEY="):
            value = line.split("=", 1)[1].strip().strip("'\"")
            if value:
                os.environ["ANTHROPIC_API_KEY"] = value
                return
    raise RuntimeError(f"ANTHROPIC_API_KEY vacía o ausente en {dev_vars}")


_FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|copy|attach|pragma|call|export)\b", re.I)


def duckdb_query(sql: str) -> str:
    """SQL de solo lectura sobre los viajes de taxi NYC ene-mar 2025 (vista `trips`)."""
    import duckdb

    if _FORBIDDEN.search(sql):
        return "error: solo se permiten consultas de lectura (SELECT) sobre `trips`"
    con = duckdb.connect(":memory:")
    con.execute(f"CREATE VIEW trips AS SELECT * FROM read_parquet('{TAXI_GLOB}')")
    try:
        con.execute(sql)
        rows = con.fetchall()
        cols = [d[0] for d in con.description]
    except Exception as exc:  # se lo devolvemos al modelo como observación, no lo tumbamos
        return f"error ejecutando SQL: {exc}"
    preview = "\n".join(str(r) for r in rows[:20])
    more = "" if len(rows) <= 20 else f"\n... ({len(rows) - 20} filas más)"
    return f"columnas: {cols}\n{preview}{more}"


def _d1_live_count() -> tuple[int, str]:
    """Conteo vivo (votos + respuestas de texto) del grupo Clase 2 en D1, solo lectura."""
    d1_repo = Path(os.environ.get("D1_REPO", str(ROOT.parent / "h1sort-website")))
    sql = (
        "SELECT "
        "(SELECT COUNT(*) FROM poll_votes v JOIN polls p ON p.id = v.poll_id "
        f"JOIN poll_groups g ON g.id = p.group_id WHERE g.code = '{D1_GROUP_C2}') + "
        "(SELECT COUNT(*) FROM poll_text_answers t JOIN polls p ON p.id = t.poll_id "
        f"JOIN poll_groups g ON g.id = p.group_id WHERE g.code = '{D1_GROUP_C2}') AS n"
    )
    proc = subprocess.run(
        ["npx", "wrangler", "d1", "execute", "h1sort-chat", "--remote", "--json", "--command", sql],
        cwd=d1_repo, capture_output=True, text=True, timeout=60,
    )
    payload = json.loads(proc.stdout)
    n = int(payload[0]["results"][0]["n"] or 0)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return n, now


def _databricks_snapshot_count() -> tuple[int, str, bool]:
    """(conteo, loaded_at, es_stub). Intenta la tabla real de WS3; si no existe, hace stub."""
    try:
        if not (os.environ.get("DATABRICKS_HOST") and (os.environ.get("DATABRICKS_TOKEN") or os.environ.get("DATABRICKS_AGENT_TOKEN"))):
            raise RuntimeError("Databricks no configurado")
        spec = importlib.util.spec_from_file_location(
            "class2_run_sql", ROOT / "demos/clase-02/databricks/run_sql.py"
        )
        run_sql = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_sql)
        run_sql.ensure_credentials()
        result = run_sql.poll_until_terminal(
            run_sql.submit_statement(
                f"SELECT COUNT(*) AS n, MAX(loaded_at) AS loaded_at FROM {SNAPSHOT_TABLE}",
                run_sql.DEFAULT_WAREHOUSE_ID,
                "workspace",
            )
        )
        if result.get("status", {}).get("state") != "SUCCEEDED":
            raise RuntimeError("consulta a Databricks no tuvo éxito")
        row = result["result"]["data_array"][0]
        return int(row[0]), str(row[1]), False
    except Exception:
        # WS3/WS0 (CLASE3-PLAN.md) todavía no publican la tabla de snapshot.
        # Interfaz clara de reemplazo: cuando exista, esta rama deja de usarse sola.
        return 0, "STUB -- WS3 aún no publica workspace.ai4data.c3_personas_v1", True


def extract_text(content) -> str:
    """El SDK devuelve bloques (thinking + texto) cuando piensa; nos quedamos con el texto."""
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text").strip()


def check_freshness(dataset: str = "class2") -> str:
    """Compara el conteo vivo en D1 contra el snapshot cargado en Databricks."""
    live_n, live_at = _d1_live_count()
    snap_n, snap_at, is_stub = _databricks_snapshot_count()
    note = " [snapshot STUB, ver TODO(WS3) en tools.py]" if is_stub else ""
    estado = "hay respuestas nuevas sin cargar" if live_n > snap_n else "está al día"
    return (
        f"a fecha {snap_at}, el snapshot tiene {snap_n} de {live_n} filas que hay ahora mismo "
        f"en D1 (consultado {live_at}); {estado}.{note}"
    )
