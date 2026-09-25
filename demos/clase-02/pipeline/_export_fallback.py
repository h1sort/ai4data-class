#!/usr/bin/env python3
"""Export the pipeline's key tables/comparisons as CSV, for the live-demo
fallback (CLASS2-PLAN.md WS4 task 3: "save fallback outputs (CSV) under
demos/clase-02/pipeline/out/fallback/"). Run at the end of a successful
run_all.sh so the fallback is always fresh.

Usage:
    python3 _export_fallback.py --schema ai4data_rehearsal --out-dir out/fallback/<run_id>

Never exports voter_hash / participant_key raw values in a way that's
displayed on stage -- these CSVs are for the presenter to open locally if
the live demo breaks, same audience as the live query results would have
had.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "databricks"))
import run_sql as dbx  # noqa: E402


def query(sql: str, warehouse_id: str, catalog: str) -> tuple[list[str], list[list]]:
    result = dbx.submit_statement(sql, warehouse_id, catalog)
    result = dbx.poll_until_terminal(result)
    status = result.get("status", {})
    if status.get("state") != "SUCCEEDED":
        error = status.get("error", {})
        raise dbx.StatementError(f"{error.get('error_code', '')}: {error.get('message', status)}")
    manifest = result.get("manifest", {})
    columns = [c["name"] for c in manifest.get("schema", {}).get("columns", [])]
    if not columns:
        return [], []
    first_chunk_rows = result.get("result", {}).get("data_array", [])
    rows = dbx.fetch_remaining_chunks(result["statement_id"], manifest, first_chunk_rows)
    return columns, rows


def write_csv(path: Path, columns: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(columns)
        w.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--warehouse-id", default=dbx.DEFAULT_WAREHOUSE_ID)
    parser.add_argument("--catalog", default=dbx.DEFAULT_CATALOG)
    args = parser.parse_args()

    dbx.ensure_credentials()
    import os

    agent_token = os.environ.get("DATABRICKS_AGENT_TOKEN")
    if agent_token:
        os.environ["DATABRICKS_TOKEN"] = agent_token

    s = args.schema
    out_dir = Path(args.out_dir)

    exports = {
        "dim_participante": f"SELECT * FROM workspace.{s}.dim_participante",
        "fct_respuestas": f"SELECT * FROM workspace.{s}.fct_respuestas",
        "judgments_ai_classify": f"SELECT * FROM workspace.{s}.judgments_ai_classify",
        "judgments_jev": f"SELECT * FROM workspace.{s}.judgments_jev",
        "agreement_persona_overall": f"""
            SELECT COUNT(*) AS n,
                   SUM(CASE WHEN a.persona_dbx = j.persona THEN 1 ELSE 0 END) AS agree,
                   ROUND(100.0 * SUM(CASE WHEN a.persona_dbx = j.persona THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_agree
            FROM workspace.{s}.judgments_ai_classify a
            JOIN workspace.{s}.judgments_jev j ON j.participant_key = a.participant_key
            WHERE a.persona_dbx IS NOT NULL AND j.persona IS NOT NULL
        """,
        "agreement_persona_by_band": f"""
            SELECT
              CASE WHEN j.persona_conf >= 0.9 THEN '1) >=0.9'
                   WHEN j.persona_conf >= 0.5 THEN '2) 0.5-0.9'
                   ELSE '3) <0.5' END AS confidence_band,
              COUNT(*) AS n,
              SUM(CASE WHEN a.persona_dbx = j.persona THEN 1 ELSE 0 END) AS agree,
              ROUND(100.0 * SUM(CASE WHEN a.persona_dbx = j.persona THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_agree
            FROM workspace.{s}.judgments_ai_classify a
            JOIN workspace.{s}.judgments_jev j ON j.participant_key = a.participant_key
            WHERE a.persona_dbx IS NOT NULL AND j.persona IS NOT NULL
            GROUP BY 1 ORDER BY 1
        """,
        "routing_persona": f"""
            SELECT
              CASE WHEN persona_conf >= 0.9 THEN '1) >=0.9 -> warehouse'
                   WHEN persona_conf >= 0.5 THEN '2) 0.5-0.9 -> LLM review'
                   ELSE '3) <0.5 -> human' END AS route,
              COUNT(*) AS n
            FROM workspace.{s}.judgments_jev
            WHERE persona_conf IS NOT NULL
            GROUP BY 1 ORDER BY 1
        """,
        "injections": f"""
            SELECT d.puesto_texto, a.persona_dbx AS ai_classify_persona,
                   j.persona AS jev_persona, j.persona_conf AS jev_confidence
            FROM workspace.{s}.dim_participante d
            JOIN workspace.{s}.judgments_ai_classify a ON a.participant_key = d.participant_key
            JOIN workspace.{s}.judgments_jev j ON j.participant_key = d.participant_key
            WHERE LOWER(d.puesto_texto) LIKE '%ignora%instruc%'
               OR LOWER(d.puesto_texto) LIKE '%ignore%instruc%'
               OR LOWER(d.puesto_texto) LIKE '%olvida%regla%'
               OR LOWER(d.puesto_texto) LIKE '%olvida%anterior%'
        """,
        "payoff_confianza_by_persona": f"""
            SELECT j.persona, COUNT(*) AS n,
                   SUM(CASE WHEN d.confianza_analisis >= 4 THEN 1 ELSE 0 END) AS n_confianza_alta,
                   CASE WHEN COUNT(*) >= 5
                        THEN CONCAT(CAST(ROUND(100.0*SUM(CASE WHEN d.confianza_analisis>=4 THEN 1 ELSE 0 END)/COUNT(*),1) AS STRING), '%')
                        ELSE 'n<5, no ranking' END AS pct_confianza_alta
            FROM workspace.{s}.dim_participante d
            JOIN workspace.{s}.judgments_jev j ON j.participant_key = d.participant_key
            WHERE j.persona IS NOT NULL AND d.confianza_analisis IS NOT NULL
            GROUP BY j.persona ORDER BY n DESC
        """,
        "payoff_rol_c1_x_persona": f"""
            SELECT d.rol_declarado_c1, j.persona AS persona_jev, COUNT(*) AS n
            FROM workspace.{s}.dim_participante d
            JOIN workspace.{s}.judgments_jev j ON j.participant_key = d.participant_key
            WHERE d.rol_declarado_c1 IS NOT NULL AND j.persona IS NOT NULL
            GROUP BY d.rol_declarado_c1, j.persona ORDER BY d.rol_declarado_c1, n DESC
        """,
        "overlap_rate": f"""
            SELECT COUNT(*) AS total_participantes,
                   SUM(CASE WHEN rol_declarado_c1 IS NOT NULL THEN 1 ELSE 0 END) AS con_rol_c1,
                   ROUND(100.0*SUM(CASE WHEN rol_declarado_c1 IS NOT NULL THEN 1 ELSE 0 END)/COUNT(*),1) AS pct_overlap
            FROM workspace.{s}.dim_participante
        """,
    }

    for name, sql in exports.items():
        columns, rows = query(sql, args.warehouse_id, args.catalog)
        write_csv(out_dir / f"{name}.csv", columns, rows)
        print(f"[fallback] {name}.csv ({len(rows)} rows)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
