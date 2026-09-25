#!/usr/bin/env python3
"""Create/update the curated Class 1 Genie space and smoke-test its question."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TITLE = "Clase 1 · Analytics de encuesta"
DESCRIPTION = (
    "Explora resultados agregados de la encuesta de la clase 1. "
    "Cada opción muestra conteos y porcentajes con el denominador específico de su pregunta."
)
WAREHOUSE_ID = "90f6df4041b446b7"
PARENT_PATH = "/Workspace/Shared/AI4Data/Clase2"
TABLE = "workspace.ai4data.c1_vw_resumen_respuestas"
QUESTION_ROLE = "¿Cuál describe mejor tu trabajo principal?"
QUESTION_AI_USE = "¿Usaste IA para una tarea de datos en los últimos 7 días?"
QUESTION_TRUST = "¿Qué tanta confianza tienes en un análisis generado por IA? (1 = ninguna confianza; 5 = mucha confianza)"
QUESTION_VALIDATION = (
    "Cuando una IA te entrega SQL, ¿cómo lo validas normalmente? "
    "Selecciona la comprobación más rigurosa que haces habitualmente."
)
SUGGESTED_QUESTION = (
    "¿Cómo se distribuyen las respuestas a «¿Cuál describe mejor tu trabajo principal?»?"
)


def stable_id(name: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_URL, f"ai4data-class2-genie:{name}").hex


EXAMPLES = [
    (
        SUGGESTED_QUESTION,
        f"""SELECT respuesta, n_respuestas, porcentaje
FROM {TABLE}
WHERE pregunta = '{QUESTION_ROLE}'
ORDER BY n_respuestas DESC""",
    ),
    (
        "¿Qué porcentaje usó IA para una tarea de datos en los últimos 7 días?",
        f"""SELECT respuesta, n_respuestas, porcentaje
FROM {TABLE}
WHERE pregunta = '{QUESTION_AI_USE}'
ORDER BY posicion_opcion""",
    ),
    (
        "¿Cómo se distribuye la confianza en un análisis generado por IA?",
        f"""SELECT respuesta, n_respuestas, porcentaje
FROM {TABLE}
WHERE pregunta = '{QUESTION_TRUST}'
ORDER BY posicion_opcion""",
    ),
    (
        "¿Qué preguntas recibieron más respuestas?",
        f"""SELECT pregunta, MAX(denominador_pregunta) AS n_respuestas
FROM {TABLE}
GROUP BY pregunta
ORDER BY n_respuestas DESC""",
    ),
    (
        "¿Qué opciones de validación de SQL fueron más frecuentes?",
        f"""SELECT respuesta, n_respuestas, porcentaje
FROM {TABLE}
WHERE pregunta = '{QUESTION_VALIDATION}'
ORDER BY n_respuestas DESC""",
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
                    "Resultados agregados de seis preguntas de la encuesta de la clase 1; "
                    "cada fila corresponde a una opción dentro de una pregunta. "
                    "No contiene identificadores ni respuestas de texto libre."
                ],
                "column_configs": [
                    {"column_name": "denominador_pregunta", "description": ["Total de respuestas a esa pregunta; se repite en cada opción."]},
                    {"column_name": "n_respuestas", "description": ["Conteo de esta opción dentro de la pregunta."]},
                    {"column_name": "poll_code", "exclude": True},
                    {"column_name": "porcentaje", "description": ["Porcentaje de esta opción sobre el denominador de su propia pregunta."]},
                    {"column_name": "pregunta", "description": ["Texto de la pregunta de la encuesta."]},
                    {"column_name": "respuesta", "description": ["Opción de respuesta elegida."]},
                ],
            }]
        },
        "instructions": {
            "text_instructions": [{
                "id": stable_id("instructions"),
                "content": [
                    "Responde sobre la encuesta de la clase 1 y usa exclusivamente esta vista agregada.",
                    "Cada pregunta tiene varias filas, una por opción. Para contar una distribución usa n_respuestas por opción.",
                    "Usa porcentaje directamente para la fracción de una opción dentro de su pregunta.",
                    "denominador_pregunta es específico de cada pregunta y se repite en cada opción: no lo sumes entre filas.",
                    "No combines conteos de preguntas distintas en un mismo denominador. No inventes causalidad ni generalices fuera de quienes respondieron.",
                    "Filtra por texto de pregunta exacto cuando la persona pregunte por una pregunta concreta.",
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
    queries = [attachment["query"] for attachment in query_attachments]
    generated_sql = next((q.get("query", "") for q in queries if q.get("query")), "")
    if TABLE.lower() not in generated_sql.lower():
        raise RuntimeError("Genie completed without querying the curated C1 aggregate view.")
    result_rows = []
    if query_attachments:
        attachment_id = query_attachments[0].get("id")
        if attachment_id:
            result_body = api_request(
                host,
                token,
                "GET",
                f"{base}/conversations/{conversation_id}/messages/{message_id}"
                f"/attachments/{attachment_id}/query-result",
            )
            result_rows = (
                result_body.get("statement_response", {})
                .get("result", {})
                .get("data_array", [])
            )
    return {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "generated_sql": generated_sql,
        "query_row_count": len(result_rows) or next(
            (q.get("query_result_metadata", {}).get("row_count") for q in queries if q.get("query_result_metadata")),
            None,
        ),
    }


def main() -> None:
    sys.path.insert(0, str(ROOT / "demos/clase-02/databricks"))
    import run_sql  # noqa: WPS433

    run_sql.ensure_credentials()
    host = os.environ["DATABRICKS_HOST"].rstrip("/")
    admin_token = os.environ["DATABRICKS_TOKEN"]
    agent_token = os.environ.get("DATABRICKS_AGENT_TOKEN", admin_token)
    payload = build_space()
    artifact = HERE / "genie/class1_genie_space.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Verify the five known-answer queries against real C1 data as ai4data-agent.
    os.environ["DATABRICKS_TOKEN"] = agent_token
    for question, sql in EXAMPLES:
        rows = query_sql(run_sql, sql, WAREHOUSE_ID, "workspace")
        print(f"SQL check: {question[:48]}… -> {len(rows)} rows")

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

    # Use the service principal for the actual Genie query, just as for SQL/Jobs.
    os.environ["DATABRICKS_TOKEN"] = agent_token
    try:
        genie_result = smoke_conversation(host, agent_token, space_id)
    except RuntimeError as exc:
        # The admin owner can validate a freshly created space if the agent has
        # SQL rights but no Genie permission; don't mask query or configuration errors.
        if "PERMISSION_DENIED" not in str(exc) and "403" not in str(exc):
            raise
        genie_result = smoke_conversation(host, admin_token, space_id)
        genie_result["validated_as"] = "space owner (agent lacks Genie permission)"
    print(
        "Genie smoke: COMPLETED; generated SQL uses c1_vw_resumen_respuestas; "
        f"row_count={genie_result.get('query_row_count')}"
    )

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
        "smoke_row_count": genie_result.get("query_row_count"),
        "conversation_id": genie_result["conversation_id"],
    }
    links_path.write_text(json.dumps(links, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Genie URL: {workspace_url}")


if __name__ == "__main__":
    main()
