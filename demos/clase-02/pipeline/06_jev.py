#!/usr/bin/env python3
"""WS4 step 6: judgment column, Jev (TypeSafe System 1) side.

Usage:
    uv run 06_jev.py --schema ai4data_rehearsal
    uv run 06_jev.py --schema ai4data --concurrency 8 --warehouse-id 90f6df4041b446b7

Reads workspace.<schema>.dim_participante (participant_key, puesto_texto,
tarea_texto) through the Databricks SQL statement API, calls Jev once per
participant with BOTH classification questions batched into a single
request (persona from puesto_texto, categoria from tarea_texto -- the
"fan-out" pattern, CLASS2-PLAN.md §3), at <=8 concurrent requests with
retries, and writes persona/categoria + confidence + probabilities to
workspace.<schema>.judgments_jev. Prints total time, tokens, and an
estimated cost at $0.042 / M input tokens (output is free per the article).

Deliberately stdlib only (urllib, concurrent.futures, subprocess to shell
out to the `databricks` CLI, reusing ../databricks/run_sql.py's own
plumbing) -- no `typesafe-sdk` / `databricks-sql-connector` -- so `uv run`
never needs a package install mid-rehearsal or on stage (same philosophy as
run_sql.py). Never prints voter_hash / participant_key values or the
TypeSafe API key.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "databricks"))
import run_sql as dbx  # noqa: E402  (../databricks/run_sql.py)

JEV_URL = "https://api.typesafe.ai/v1/systemone"
JEV_MODEL = "jev-latest"
JEV_PRICE_PER_M_INPUT_TOKENS = 0.042
MAX_RETRIES = 3
RETRY_BACKOFF_S = 1.5
DEFAULT_CONCURRENCY = 8
REQUEST_TIMEOUT_S = 30

PERSONA_CRITERIA = {
    "ejecutivo": "C-level, director/a, VP, jefe/a de área",
    "manager": "lidera un equipo; gerente, product manager",
    "practitioner": "analista, ingeniero/a, científico/a de datos que ejecuta el trabajo técnico",
    "estudiante": "estudia, becario/a, en formación",
    "otro": "no es un puesto o no encaja en las anteriores",
}

CATEGORIA_CRITERIA = {
    "limpieza/calidad": "limpiar, deduplicar o validar datos; mejorar su calidad",
    "reporting/dashboards": "reportes, dashboards, KPIs, visualización",
    "ETL/pipelines": "extraer, transformar y cargar datos; pipelines, integraciones",
    "análisis/EDA": "análisis exploratorio; responder preguntas de negocio con datos",
    "ML/modelos": "entrenar, desplegar o mantener modelos de machine learning",
    "documentación": "documentar procesos, datos o decisiones",
    "otro": "no encaja claramente en las anteriores o no es una tarea de datos",
}


# --------------------------------------------------------------------------
# Databricks read/write (reusing run_sql.py's own submit/poll/fetch helpers)
# --------------------------------------------------------------------------


def dbx_query(sql: str, warehouse_id: str, catalog: str) -> list[dict]:
    result = dbx.submit_statement(sql, warehouse_id, catalog)
    result = dbx.poll_until_terminal(result)
    status = result.get("status", {})
    if status.get("state") != "SUCCEEDED":
        error = status.get("error", {})
        raise dbx.StatementError(f"{error.get('error_code', '')}: {error.get('message', status)}")
    manifest = result.get("manifest", {})
    columns = [c["name"] for c in manifest.get("schema", {}).get("columns", [])]
    if not columns:
        return []
    first_chunk_rows = result.get("result", {}).get("data_array", [])
    rows = dbx.fetch_remaining_chunks(result["statement_id"], manifest, first_chunk_rows)
    return [dict(zip(columns, row)) for row in rows]


def dbx_exec(sql: str, warehouse_id: str, catalog: str) -> None:
    result = dbx.submit_statement(sql, warehouse_id, catalog)
    result = dbx.poll_until_terminal(result)
    status = result.get("status", {})
    if status.get("state") != "SUCCEEDED":
        error = status.get("error", {})
        raise dbx.StatementError(f"{error.get('error_code', '')}: {error.get('message', status)}")


def sql_str(value: str | None) -> str:
    return "NULL" if value is None else "'" + value.replace("'", "''") + "'"


def sql_num(value: float | int | None) -> str:
    return "NULL" if value is None else repr(value)


# --------------------------------------------------------------------------
# Jev calls
# --------------------------------------------------------------------------


def build_payload(puesto: str | None, tarea: str | None) -> dict | None:
    questions: dict = {}
    if puesto:
        questions["persona"] = {
            "type": "choice",
            "instructions": "¿Qué perfil describe mejor este puesto?",
            "criteria": PERSONA_CRITERIA,
        }
    if tarea:
        questions["categoria"] = {
            "type": "choice",
            "instructions": "¿A qué categoría pertenece esta tarea de datos a automatizar?",
            "criteria": CATEGORIA_CRITERIA,
        }
    if not questions:
        return None
    state = "\n".join(
        p for p in (f"Puesto: {puesto}" if puesto else None, f"Tarea a automatizar: {tarea}" if tarea else None) if p
    )
    return {"state": state, "model": JEV_MODEL, "questions": questions}


def call_jev(api_key: str, payload: dict) -> dict:
    req = urllib.request.Request(
        JEV_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
                return json.loads(resp.read())
        except (urllib.error.URLError, TimeoutError) as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_S * attempt)
    raise RuntimeError(f"Jev call failed after {MAX_RETRIES} attempts: {last_exc}")


def classify_one(api_key: str, participant_key: str, puesto: str | None, tarea: str | None) -> dict:
    payload = build_payload(puesto, tarea)
    if payload is None:
        return {
            "participant_key": participant_key,
            "persona": None, "persona_conf": None,
            "categoria": None, "categoria_conf": None,
            "probabilities": None, "model": None,
            "input_tokens": 0, "output_tokens": 0, "latency_ms": 0,
        }
    t0 = time.monotonic()
    resp = call_jev(api_key, payload)
    latency_ms = int((time.monotonic() - t0) * 1000)
    answers = resp.get("answers", {})
    persona = answers.get("persona", {})
    categoria = answers.get("categoria", {})
    usage = resp.get("usage", {})
    probabilities = json.dumps(
        {"persona": persona.get("probabilities"), "categoria": categoria.get("probabilities")},
        ensure_ascii=False,
    )
    return {
        "participant_key": participant_key,
        "persona": persona.get("choice"),
        "persona_conf": persona.get("confidence"),
        "categoria": categoria.get("choice"),
        "categoria_conf": categoria.get("confidence"),
        "probabilities": probabilities,
        "model": resp.get("model"),
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "latency_ms": latency_ms,
    }


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--schema", required=True, help="target schema, e.g. ai4data_rehearsal or ai4data")
    parser.add_argument("--warehouse-id", default=dbx.DEFAULT_WAREHOUSE_ID)
    parser.add_argument("--catalog", default=dbx.DEFAULT_CATALOG)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--limit", type=int, default=None, help="cap participants processed (debugging)")
    args = parser.parse_args()
    concurrency = max(1, min(args.concurrency, DEFAULT_CONCURRENCY))

    dbx.ensure_credentials()
    import os

    agent_token = os.environ.get("DATABRICKS_AGENT_TOKEN")
    if agent_token:
        os.environ["DATABRICKS_TOKEN"] = agent_token  # the pipeline always runs as the scoped service principal
    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        print("error: TYPESAFE_API_KEY missing from the environment/.env (never printing it)", file=sys.stderr)
        return 2

    print(f"[jev] reading workspace.{args.schema}.dim_participante")
    sql = (
        f"SELECT participant_key, puesto_texto, tarea_texto "
        f"FROM workspace.{args.schema}.dim_participante "
        f"WHERE puesto_texto IS NOT NULL OR tarea_texto IS NOT NULL"
    )
    rows = dbx_query(sql, args.warehouse_id, args.catalog)
    if args.limit:
        rows = rows[: args.limit]
    print(f"[jev] {len(rows)} participants to classify (concurrency={concurrency})")

    t0 = time.monotonic()
    results: list[dict] = []
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {
            pool.submit(classify_one, api_key, r["participant_key"], r.get("puesto_texto"), r.get("tarea_texto")): r
            for r in rows
        }
        for fut in concurrent.futures.as_completed(futures):
            results.append(fut.result())
            done += 1
            if done % 10 == 0 or done == len(rows):
                print(f"[jev] {done}/{len(rows)} done")
    elapsed_s = time.monotonic() - t0

    total_input_tokens = sum(r["input_tokens"] for r in results)
    total_output_tokens = sum(r["output_tokens"] for r in results)
    cost = total_input_tokens / 1_000_000 * JEV_PRICE_PER_M_INPUT_TOKENS
    latencies = [r["latency_ms"] for r in results if r["latency_ms"]]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print(
        f"[jev] classified {len(results)} participants in {elapsed_s:.1f}s "
        f"(avg call latency {avg_latency:.0f}ms)"
    )
    print(
        f"[jev] tokens: {total_input_tokens} in / {total_output_tokens} out "
        f"-- est. cost ${cost:.4f} (${JEV_PRICE_PER_M_INPUT_TOKENS}/M input tokens, output free)"
    )

    print(f"[jev] writing workspace.{args.schema}.judgments_jev")
    dbx_exec(
        f"CREATE OR REPLACE TABLE workspace.{args.schema}.judgments_jev ("
        "  participant_key STRING,"
        "  persona STRING,"
        "  persona_conf DOUBLE,"
        "  categoria STRING,"
        "  categoria_conf DOUBLE,"
        "  probabilities STRING COMMENT 'JSON: {persona: {...}, categoria: {...}}',"
        "  model STRING,"
        "  input_tokens INT,"
        "  latency_ms INT"
        ") COMMENT 'Jev (TypeSafe System 1) persona/categoria_tarea judgments per participant, with confidence -- compare with judgments_ai_classify, which has no confidence.'",
        args.warehouse_id,
        args.catalog,
    )

    if results:
        values = ",\n  ".join(
            "(" + ", ".join([
                sql_str(r["participant_key"]),
                sql_str(r["persona"]),
                sql_num(r["persona_conf"]),
                sql_str(r["categoria"]),
                sql_num(r["categoria_conf"]),
                sql_str(r["probabilities"]),
                sql_str(r["model"]),
                sql_num(r["input_tokens"]),
                sql_num(r["latency_ms"]),
            ]) + ")"
            for r in results
        )
        dbx_exec(
            f"INSERT INTO workspace.{args.schema}.judgments_jev "
            "(participant_key, persona, persona_conf, categoria, categoria_conf, probabilities, model, input_tokens, latency_ms) "
            f"VALUES\n  {values}",
            args.warehouse_id,
            args.catalog,
        )
    print("[jev] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
