#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["langchain-anthropic>=0.3.0", "langchain-core>=0.3.0", "duckdb>=1.0.0"]
# ///
"""El loop de la diapositiva 4, en código:
GOAL -> MODEL -> TOOL REQUEST -> HARNESS EXECUTES -> OBSERVATION (y repite).

uv run demos/clase-03/agent/agent.py "¿Cuántos viajes hay en el dataset de taxis?"
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tools  # noqa: E402  (duckdb_query, check_freshness, extract_text viven ahí)

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

tools.load_anthropic_key(tools.ROOT.parent / "h1sort-website" / ".dev.vars")

# IDs vigentes (skill claude-api): claude-sonnet-5 es el default por velocidad en
# vivo; sube a claude-opus-5 o claude-opus-5-5 si necesitas más profundidad.
MODEL_ID = "claude-sonnet-5"


@tool
def duckdb_query(sql: str) -> str:
    """SQL de solo lectura sobre los viajes de taxi NYC (vista `trips`)."""
    return tools.duckdb_query(sql)


@tool
def check_freshness(dataset: str = "class2") -> str:
    """Compara el conteo vivo en D1 contra el snapshot cargado en Databricks."""
    return tools.check_freshness(dataset)


ALL_TOOLS = {"duckdb_query": duckdb_query, "check_freshness": check_freshness}
SYSTEM = (
    "Eres un agente de datos. Usa duckdb_query para consultar los viajes de taxi "
    "y check_freshness para saber si tus datos están al día. No inventes números. "
    "Si reportas frescura, usa siempre el patrón exacto 'a fecha X, N de M filas'."
)


def run(goal: str, *, system: str = SYSTEM, system_suffix: str = "", model: str = MODEL_ID,
        tool_names=("duckdb_query", "check_freshness")) -> dict:
    """Corre el loop hasta la respuesta final. `system_suffix` es cómo los evals
    inyectan una corrección (capa semántica, defensa) sin reescribir el prompt base."""
    active = {name: ALL_TOOLS[name] for name in tool_names}
    llm = ChatAnthropic(model=model, max_tokens=1024).bind_tools(list(active.values()))
    full_system = f"{system}\n\n{system_suffix}" if system_suffix else system
    messages = [SystemMessage(full_system), HumanMessage(goal)]
    print(f"GOAL > {goal}")
    calls_made: list[str] = []
    for _ in range(6):
        response = llm.invoke(messages)  # MODEL piensa y decide
        messages.append(response)
        if not response.tool_calls:  # no pidió herramientas -> respuesta final
            answer = tools.extract_text(response.content)
            print(f"OBSERVATION FINAL > {answer}")
            return {"answer": answer, "tool_calls": calls_made}
        for call in response.tool_calls:  # TOOL REQUEST
            print(f"TOOL REQUEST > {call['name']}({call['args']})")
            calls_made.append(call["name"])
            result = active[call["name"]].invoke(call["args"])  # HARNESS EXECUTES
            print(f"OBSERVATION > {str(result)[:200]}")
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    return {"answer": "(se acabaron los turnos del loop)", "tool_calls": calls_made}


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "¿Cuántos viajes hay en el dataset de taxis?")
