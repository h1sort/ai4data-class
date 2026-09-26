#!/usr/bin/env python3
"""Create/update the Clase 3 Trap 2 Genie space and smoke-test its question.

Same pattern as demos/clase-02/notebooks/setup_genie.py, scoped to
workspace.ai4data.c3_personas_v1 (built by 10_trap2_walkthrough.ipynb).
Answers "¿Cuántos ejecutivos hay en la clase?" -- with two classification
methods (Jev, with confidence; ai_classify, without) that can disagree, so
the space is instructed to report both rather than silently pick one.
Never surfaces participant_key.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TITLE = "Clase 3 · Personas de Clase 2 (Jev vs ai_classify)"
DESCRIPTION = (
    "Clasificación de persona (ejecutivo/manager/practitioner/estudiante/otro) por participante "
    "de Clase 2, con dos métodos independientes: Jev (con confianza) y ai_classify (sin confianza). "
    "No contiene identificadores de participante ni texto libre."
)
WAREHOUSE_ID = "90f6df4041b446b7"
PARENT_PATH = "/Shared/AI4Data/Clase3"
TABLE = "workspace.ai4data.c3_personas_v1"
SUGGESTED_QUESTION = "¿Cuántos ejecutivos hay en la clase?"


def stable_id(name: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_URL, f"ai4data-class3-genie:{name}").hex


EXAMPLES = [
    (
        SUGGESTED_QUESTION,
        f"""SELECT
  SUM(CASE WHEN persona_jev = 'ejecutivo' THEN 1 ELSE 0 END) AS ejecutivos_jev,
  SUM(CASE WHEN persona_ai_classify = 'ejecutivo' THEN 1 ELSE 0 END) AS ejecutivos_ai_classify,
  COUNT(*) AS total_clasificados
FROM {TABLE}""",
    ),
    (
        "¿Cómo se distribuyen las personas según Jev?",
        f"""SELECT persona_jev, COUNT(*) AS n
FROM {TABLE}
WHERE persona_jev IS NOT NULL
GROUP BY persona_jev
ORDER BY n DESC""",
    ),
    (
        "¿Cómo se distribuyen las personas según ai_classify?",
        f"""SELECT persona_ai_classify, COUNT(*) AS n
FROM {TABLE}
WHERE persona_ai_classify IS NOT NULL
GROUP BY persona_ai_classify
ORDER BY n DESC""",
    ),
    (
        "¿En qué porcentaje de filas coinciden Jev y ai_classify?",
        f"""SELECT
  ROUND(100.0 * SUM(CASE WHEN persona_jev = persona_ai_classify THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_acuerdo,
  COUNT(*) AS total
FROM {TABLE}
WHERE persona_jev IS NOT NULL AND persona_ai_classify IS NOT NULL""",
    ),
]


def lines(text: str) -> list[str]:
    return text.strip().splitlines(keepends=True)


def build_space() -> dict:
    serialized = {
        "version": 2,
        "config": {
            "sample_questions": [
                {"id": stable_id(question), "question": [question]}
                for question, _ in sorted(EXAMPLES, key=lambda item: stable_id(item[0]))
            ]
        },
        "data_sources": {
            "tables": [{
                "identifier": TABLE,
                "description": [
                    "Una fila por participante de Clase 2 con puesto_texto respondido. Dos "
                    "clasificaciones de persona independientes (Jev y ai_classify) sobre el mismo "
                    "texto y la misma taxonomía; pueden no coincidir. No contiene texto libre."
                ],
                "column_configs": [
                    {"column_name": "participant_key", "exclude": True},
                    {"column_name": "persona_ai_classify", "description": ["Clasificación de persona por la función ai_classify de Databricks; mismas etiquetas que persona_jev, sin confianza."]},
                    {"column_name": "persona_jev", "description": ["Clasificación de persona por Jev: ejecutivo, manager, practitioner, estudiante u otro."]},
                    {"column_name": "persona_jev_confidence", "description": ["Confianza (0-1) que Jev reporta para persona_jev."]},
                ],
            }]
        },
        "instructions": {
            "text_instructions": [{
                "id": stable_id("instructions"),
                "content": [
                    "Esta tabla tiene DOS clasificaciones de persona independientes por fila: "
                    "persona_jev y persona_ai_classify. No las combines ni promedies -- son métodos distintos.",
                    "Nunca selecciones ni muestres participant_key en una respuesta.",
                    "Si preguntan cuántos ejecutivos (o cualquier otra persona) hay sin especificar método, "
                    "reporta el conteo de persona_jev como respuesta principal y menciona también el conteo "
                    "de persona_ai_classify para comparar -- no elijas uno solo en silencio.",
                    "COUNT(*) sobre esta tabla es el total de participantes con puesto_texto clasificado, "
                    "no el total de la clase (algunos participantes no respondieron esa pregunta).",
                ],
            }],
            "example_question_sqls": [
                {
                    "id": stable_id(f"example:{question}"),
                    "question": [question],
                    "sql": lines(sql),
                }
                for question, sql in sorted(EXAMPLES, key=lambda item: stable_id(f"example:{item[0]}"))
            ],
        },
        "benchmarks": {
            "questions": [
                {
                    "id": stable_id(f"benchmark:{question}"),
                    "question": [question],
                    "answer": [{"format": "SQL", "content": lines(sql)}],
                }
                for question, sql in sorted(EXAMPLES, key=lambda item: stable_id(f"benchmark:{item[0]}"))
            ]
        },
    }
    return {
        "title": TITLE,
        "description": DESCRIPTION,
        "warehouse_id": WAREHOUSE_ID,
        "parent_path": PARENT_PATH,
        "serialized_space": json.dumps(serialized, ensure_ascii=False),
    }


def api_request(host: str, token: str, method: str, path: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        host + path,
        data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"{method} {path} failed ({exc.code}): {detail[:1200]}") from None


def query_sql(run_sql, sql: str, warehouse_id: str, catalog: str) -> list[list]:
    response = run_sql.submit_statement(sql, warehouse_id, catalog)
    response = run_sql.poll_until_terminal(response)
    if response.get("status", {}).get("state") != "SUCCEEDED":
        error = response.get("status", {}).get("error", {})
        raise RuntimeError(f"sample SQL failed: {error.get('error_code', 'UNKNOWN')}")
    manifest = response.get("manifest", {})
    return run_sql.fetch_remaining_chunks(
        response["statement_id"], manifest, response.get("result", {}).get("data_array", [])
    )


def smoke_conversation(host: str, token: str, space_id: str) -> dict:
    base = f"/api/2.0/genie/spaces/{space_id}"
    started = api_request(host, token, "POST", f"{base}/start-conversation", {
        "content": SUGGESTED_QUESTION,
        "enable_visualization": True,
    })
    message = started.get("message", {})
    conversation_id = started.get("conversation_id") or message.get("conversation_id")
    message_id = started.get("message_id") or message.get("id") or message.get("message_id")
    if not conversation_id or not message_id:
        raise RuntimeError("Genie start-conversation returned no conversation/message id.")

    message_path = f"{base}/conversations/{conversation_id}/messages/{message_id}"
    deadline = time.monotonic() + 300
    result = {}
    while time.monotonic() < deadline:
        result = api_request(host, token, "GET", message_path)
        status = result.get("status")
        if status in ("COMPLETED", "FAILED", "CANCELLED", "QUERY_RESULT_EXPIRED"):
            break
        time.sleep(3)
    status = result.get("status")
    if status != "COMPLETED":
        error = result.get("error", {})
        raise RuntimeError(f"Genie sample conversation ended {status}: {str(error)[:800]}")
    query_attachments = [
        attachment
        for attachment in result.get("attachments", [])
        if isinstance(attachment, dict) and attachment.get("query")
    ]
    text_attachments = [
        attachment.get("text", {}).get("content", "")
        for attachment in result.get("attachments", [])
        if isinstance(attachment, dict) and attachment.get("text")
    ]
    queries = [attachment["query"] for attachment in query_attachments]
    generated_sql = next((q.get("query", "") for q in queries if q.get("query")), "")
    # Genie sometimes backtick-quotes identifiers (`workspace`.`ai4data`.`c3_personas_v1`);
    # strip backticks before the containment check so that doesn't look like a miss.
    if TABLE.lower() not in generated_sql.lower().replace("`", ""):
        raise RuntimeError("Genie completed without querying c3_personas_v1.")
    result_rows = []
    columns = []
    if query_attachments:
        attachment_id = query_attachments[0].get("id")
        if attachment_id:
            result_body = api_request(
                host, token, "GET",
                f"{base}/conversations/{conversation_id}/messages/{message_id}"
                f"/attachments/{attachment_id}/query-result",
            )
            statement_response = result_body.get("statement_response", {})
            result_rows = statement_response.get("result", {}).get("data_array", [])
            columns = [
                c.get("name")
                for c in statement_response.get("manifest", {}).get("schema", {}).get("columns", [])
            ]
    return {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "generated_sql": generated_sql,
        "result_columns": columns,
        "result_rows": result_rows,
        "text_answer": " ".join(t for t in text_attachments if t) or None,
    }


def main() -> None:
    sys.path.insert(0, str(ROOT / "demos/clase-02/databricks"))
    import run_sql  # noqa: WPS433

    run_sql.ensure_credentials()
    host = os.environ["DATABRICKS_HOST"].rstrip("/")
    admin_token = os.environ["DATABRICKS_TOKEN"]
    agent_token = os.environ.get("DATABRICKS_AGENT_TOKEN", admin_token)
    payload = build_space()
    artifact = HERE / "genie/class3_genie_space.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Verify all example queries against the real table as ai4data-agent.
    os.environ["DATABRICKS_TOKEN"] = agent_token
    for question, sql in EXAMPLES:
        rows = query_sql(run_sql, sql, WAREHOUSE_ID, "workspace")
        print(f"SQL check: {question[:48]}… -> {len(rows)} row(s): {rows}")

    os.environ["DATABRICKS_TOKEN"] = admin_token
    existing = api_request(host, admin_token, "GET", "/api/2.0/genie/spaces").get("spaces", [])
    match = next((item for item in existing if item.get("title") == TITLE), None)
    serialized_payload = {
        "title": payload["title"],
        "description": payload["description"],
        "warehouse_id": payload["warehouse_id"],
        "parent_path": payload["parent_path"],
        "serialized_space": payload["serialized_space"],
    }
    if match:
        space_id = match["space_id"]
        api_request(host, admin_token, "PATCH", f"/api/2.0/genie/spaces/{space_id}", serialized_payload)
        print(f"updated Genie space {space_id}")
    else:
        created = api_request(host, admin_token, "POST", "/api/2.0/genie/spaces", serialized_payload)
        space_id = created.get("space_id")
        if not space_id:
            raise SystemExit("Databricks created no Genie space_id.")
        print(f"created Genie space {space_id}")

    os.environ["DATABRICKS_TOKEN"] = agent_token
    # A space that was just created/updated can take a few seconds to fully
    # index its serialized config before a conversation reliably uses it --
    # retry the smoke conversation rather than fail on a transient miss.
    last_exc: RuntimeError | None = None
    genie_result = None
    for attempt in range(3):
        try:
            genie_result = smoke_conversation(host, agent_token, space_id)
            break
        except RuntimeError as exc:
            if "PERMISSION_DENIED" in str(exc) or "403" in str(exc):
                genie_result = smoke_conversation(host, admin_token, space_id)
                genie_result["validated_as"] = "space owner (agent lacks Genie permission)"
                break
            last_exc = exc
            if attempt < 2:
                print(f"smoke conversation attempt {attempt + 1} did not query the table yet, retrying in 10s...")
                time.sleep(10)
    if genie_result is None:
        raise last_exc
    print(
        "Genie smoke: COMPLETED; generated SQL uses c3_personas_v1; "
        f"columns={genie_result.get('result_columns')} rows={genie_result.get('result_rows')}"
    )
    print(f"Generated SQL:\n{genie_result.get('generated_sql')}")
    if genie_result.get("text_answer"):
        print(f"Text answer: {genie_result['text_answer']}")

    links_path = HERE / "demo-links.json"
    links = json.loads(links_path.read_text(encoding="utf-8")) if links_path.exists() else {}
    workspace_url = f"{host}/genie/rooms/{space_id}"
    links["genie"] = {
        "title": TITLE,
        "space_id": space_id,
        "workspace_url": workspace_url,
        "suggested_question": SUGGESTED_QUESTION,
        "tested_sql": EXAMPLES[0][1],
        "smoke_status": "COMPLETED",
        "smoke_result_columns": genie_result.get("result_columns"),
        "smoke_result_rows": genie_result.get("result_rows"),
        "smoke_generated_sql": genie_result.get("generated_sql"),
        "smoke_text_answer": genie_result.get("text_answer"),
        "conversation_id": genie_result["conversation_id"],
    }
    links_path.write_text(json.dumps(links, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Genie URL: {workspace_url}")


if __name__ == "__main__":
    main()
