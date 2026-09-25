#!/usr/bin/env python3
"""Thin wrapper over `databricks api post /api/2.0/sql/statements`.

Usage:
    run_sql.py -f path/to/file.sql
    run_sql.py -q "SELECT 1"
    run_sql.py -f file.sql --warehouse-id <id> --catalog workspace

What it does:
  - Loads `.env` (DATABRICKS_HOST, DATABRICKS_TOKEN) by walking up from this
    script's own directory to find it, and sets it in the environment for the
    `databricks` CLI subprocess. Never prints its contents.
  - Splits a .sql file into individual statements on `;`, aware of quoted
    strings and `--` line comments, so a `;` or `--` inside a string literal
    doesn't break the split.
  - Runs each statement against the given warehouse, using a synchronous
    `wait_timeout` of 50s; if the statement is still PENDING/RUNNING after
    that, polls `GET /api/2.0/sql/statements/{id}` until it reaches a
    terminal state.
  - Prints results as a readable, aligned text table using the column names
    from `manifest.schema`. Statements with no result set (DDL) print a
    short OK line instead.
  - Prints elapsed wall time per statement (useful for latency checks).
  - On FAILED (or any other non-SUCCEEDED terminal state), prints the
    server's error message to stderr and exits non-zero. By default it stops
    at the first failing statement in a multi-statement file (like
    `ON_ERROR_STOP`); pass --keep-going to run the rest anyway.

This is meant to be used live on stage and by other agents: keep it
dependency-free (stdlib only) so it never needs a package install mid-demo.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_WAREHOUSE_ID = "90f6df4041b446b7"
DEFAULT_CATALOG = "workspace"
WAIT_TIMEOUT = "50s"
POLL_INTERVAL_S = 2.0
MAX_TOTAL_WAIT_S = 900  # safety net once we start polling past the 50s sync wait
MAX_CELL_WIDTH = 100
TERMINAL_STATES = {"SUCCEEDED", "FAILED", "CANCELED", "CLOSED"}


# --------------------------------------------------------------------------
# .env loading (silent)
# --------------------------------------------------------------------------


def find_dotenv(start: Path) -> Path | None:
    """Walk up from `start` looking for a `.env` file."""
    for directory in [start, *start.parents]:
        candidate = directory / ".env"
        if candidate.is_file():
            return candidate
    return None


def load_dotenv(path: Path) -> None:
    """Parse KEY=VALUE lines from `path` into os.environ. Never prints them.

    Does not override a variable already present in the environment (same
    convention as python-dotenv's default `override=False`). This matters
    for WS4: the pipeline scripts export DATABRICKS_TOKEN=$DATABRICKS_AGENT_TOKEN
    before calling this script (or importing it), so the demo genuinely runs
    as the scoped service principal, not the admin PAT that also lives in
    .env under the same DATABRICKS_TOKEN key.
    """
    import os

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


def ensure_credentials() -> None:
    import os

    dotenv_path = find_dotenv(Path(__file__).resolve().parent)
    if dotenv_path is not None:
        load_dotenv(dotenv_path)
    missing = [v for v in ("DATABRICKS_HOST", "DATABRICKS_TOKEN") if not os.environ.get(v)]
    if missing:
        print(
            f"error: missing {', '.join(missing)} in the environment or .env "
            "(never printing their values)",
            file=sys.stderr,
        )
        sys.exit(2)


# --------------------------------------------------------------------------
# SQL statement splitting: quote-aware, `--` comment-aware, split on `;`
# --------------------------------------------------------------------------


def split_sql(text: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    in_squote = False
    in_dquote = False
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if in_squote:
            current.append(c)
            if c == "'":
                if i + 1 < n and text[i + 1] == "'":  # escaped '' inside a string
                    current.append(text[i + 1])
                    i += 2
                    continue
                in_squote = False
            i += 1
            continue
        if in_dquote:
            current.append(c)
            if c == '"':
                in_dquote = False
            i += 1
            continue
        if c == "'":
            in_squote = True
            current.append(c)
            i += 1
            continue
        if c == '"':
            in_dquote = True
            current.append(c)
            i += 1
            continue
        if c == "-" and i + 1 < n and text[i + 1] == "-":
            nl = text.find("\n", i)
            i = n if nl == -1 else nl
            continue
        if c == ";":
            stmt = "".join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
            i += 1
            continue
        current.append(c)
        i += 1
    tail = "".join(current).strip()
    if tail:
        statements.append(tail)
    return statements


# --------------------------------------------------------------------------
# Databricks CLI wrapper
# --------------------------------------------------------------------------


class StatementError(RuntimeError):
    pass


def _run_cli(args: list[str]) -> dict:
    proc = subprocess.run(
        ["databricks", "api", *args, "-o", "json"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise StatementError(
            f"databricks CLI failed ({' '.join(args[:2])}): "
            f"{proc.stderr.strip() or proc.stdout.strip()}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise StatementError(f"could not parse databricks CLI output as JSON: {exc}") from exc


def api_post(path: str, payload: dict) -> dict:
    return _run_cli(["post", path, "--json", json.dumps(payload)])


def api_get(path: str) -> dict:
    return _run_cli(["get", path])


def submit_statement(sql: str, warehouse_id: str, catalog: str | None) -> dict:
    payload = {
        "warehouse_id": warehouse_id,
        "statement": sql,
        "wait_timeout": WAIT_TIMEOUT,
    }
    if catalog:
        payload["catalog"] = catalog
    return api_post("/api/2.0/sql/statements", payload)


def poll_until_terminal(result: dict) -> dict:
    statement_id = result.get("statement_id")
    state = result.get("status", {}).get("state")
    start = time.monotonic()
    while state not in TERMINAL_STATES:
        if time.monotonic() - start > MAX_TOTAL_WAIT_S:
            raise StatementError(
                f"statement {statement_id} still {state} after {MAX_TOTAL_WAIT_S}s, giving up"
            )
        time.sleep(POLL_INTERVAL_S)
        result = api_get(f"/api/2.0/sql/statements/{statement_id}")
        state = result.get("status", {}).get("state")
    return result


def fetch_remaining_chunks(statement_id: str, manifest: dict, first_chunk_rows: list) -> list:
    """Fetch any result chunks beyond the first, which comes inline."""
    rows = list(first_chunk_rows)
    total_chunks = manifest.get("total_chunk_count", 1)
    for chunk_index in range(1, total_chunks):
        chunk = api_get(f"/api/2.0/sql/statements/{statement_id}/result/chunks/{chunk_index}")
        rows.extend(chunk.get("data_array", []))
    return rows


# --------------------------------------------------------------------------
# Table rendering
# --------------------------------------------------------------------------


def render_table(columns: list[dict], rows: list[list]) -> str:
    headers = [col.get("name", "") for col in columns]

    def fmt_cell(value) -> str:
        if value is None:
            text = "NULL"
        else:
            text = str(value)
        if len(text) > MAX_CELL_WIDTH:
            text = text[: MAX_CELL_WIDTH - 1] + "…"
        return text

    formatted_rows = [[fmt_cell(v) for v in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in formatted_rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))

    def fmt_row(cells: list[str]) -> str:
        return " | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(cells))

    lines = [fmt_row(headers), "-+-".join("-" * w for w in widths)]
    lines.extend(fmt_row(row) for row in formatted_rows)
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Main statement execution + reporting
# --------------------------------------------------------------------------


def run_one(sql: str, warehouse_id: str, catalog: str | None, index: int, total: int) -> bool:
    """Runs one statement, prints its outcome. Returns True on success."""
    label = f"[{index}/{total}]" if total > 1 else "[stmt]"
    preview = " ".join(sql.split())
    if len(preview) > 90:
        preview = preview[:89] + "…"
    print(f"{label} {preview}")

    t0 = time.monotonic()
    try:
        result = submit_statement(sql, warehouse_id, catalog)
        result = poll_until_terminal(result)
    except StatementError as exc:
        elapsed = time.monotonic() - t0
        print(f"  error after {elapsed:.2f}s: {exc}", file=sys.stderr)
        return False
    elapsed = time.monotonic() - t0

    status = result.get("status", {})
    state = status.get("state")
    statement_id = result.get("statement_id", "?")

    if state != "SUCCEEDED":
        error = status.get("error", {})
        message = error.get("message") or json.dumps(status)
        error_code = error.get("error_code", "")
        print(f"  FAILED ({state}) after {elapsed:.2f}s [{statement_id}]", file=sys.stderr)
        print(f"  {error_code}: {message}".strip(": "), file=sys.stderr)
        return False

    manifest = result.get("manifest", {})
    schema = manifest.get("schema", {})
    columns = schema.get("columns", [])
    total_rows = manifest.get("total_row_count", 0)

    if not columns or "result" not in result:
        print(f"  OK, no result set, {elapsed:.2f}s [{statement_id}]")
        return True

    first_chunk_rows = result.get("result", {}).get("data_array", [])
    rows = fetch_remaining_chunks(statement_id, manifest, first_chunk_rows)

    print(render_table(columns, rows))
    print(f"  {total_rows} row(s), {elapsed:.2f}s [{statement_id}]")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-f", "--file", type=Path, help="path to a .sql file (split on ';')")
    source.add_argument("-q", "--query", type=str, help="a single SQL statement")
    parser.add_argument(
        "--warehouse-id",
        default=DEFAULT_WAREHOUSE_ID,
        help=f"SQL warehouse id (default: {DEFAULT_WAREHOUSE_ID}, the class Serverless Starter Warehouse)",
    )
    parser.add_argument(
        "--catalog",
        default=DEFAULT_CATALOG,
        help=f"default catalog for unqualified names (default: {DEFAULT_CATALOG})",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="run all statements in a file even if an earlier one fails",
    )
    args = parser.parse_args()

    ensure_credentials()

    if args.query is not None:
        statements = [args.query.strip().rstrip(";").strip()]
    else:
        if not args.file.is_file():
            print(f"error: no such file: {args.file}", file=sys.stderr)
            return 2
        statements = split_sql(args.file.read_text())

    if not statements:
        print("error: no statements to run", file=sys.stderr)
        return 2

    ok = True
    for idx, stmt in enumerate(statements, start=1):
        success = run_one(stmt, args.warehouse_id, args.catalog, idx, len(statements))
        if not success:
            ok = False
            if not args.keep_going:
                break

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
