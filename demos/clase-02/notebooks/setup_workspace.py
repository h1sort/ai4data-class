#!/usr/bin/env python3
"""Import and run the Clase 2 notebooks in the shared Databricks workspace.

Usage from the repository root:
    uv run demos/clase-02/notebooks/setup_workspace.py import
    uv run demos/clase-02/notebooks/setup_workspace.py run 02_ml_classifier
    uv run demos/clase-02/notebooks/setup_workspace.py run-all

Workspace writes use DATABRICKS_TOKEN from .env. One-time serverless runs use
DATABRICKS_AGENT_TOKEN. The script never prints either token or notebook cell
outputs; it reports only notebook task state and the dbutils notebook exit value.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REMOTE_DIR = "/Shared/AI4Data/Clase2"
NOTEBOOKS = (
    "01_business_analytics",
    "02_ml_classifier",
    "03_llm_jev",
)
DEPENDENCIES = {
    "01_business_analytics": ["matplotlib==3.10.0"],
    "02_ml_classifier": ["scikit-learn==1.6.1", "matplotlib==3.10.0"],
    "03_llm_jev": [],
}


def load_credentials() -> tuple[str, str, str]:
    sys.path.insert(0, str(ROOT / "demos/clase-02/databricks"))
    import run_sql  # noqa: WPS433

    run_sql.ensure_credentials()
    host = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
    admin_token = os.environ.get("DATABRICKS_TOKEN", "")
    agent_token = os.environ.get("DATABRICKS_AGENT_TOKEN", "")
    if not host or not admin_token:
        raise SystemExit("Missing DATABRICKS_HOST or DATABRICKS_TOKEN in .env/environment.")
    return host, admin_token, agent_token


def run_cli(args: list[str], token: str, *, timeout: int = 1200) -> str:
    env = os.environ.copy()
    env["DATABRICKS_TOKEN"] = token
    proc = subprocess.run(args, capture_output=True, text=True, env=env, timeout=timeout)
    if proc.returncode:
        # CLI errors may contain remote SQL details; show only the first safe line.
        line = next((s for s in proc.stderr.splitlines() if s.strip()), "Databricks CLI request failed")
        print(f"error: {line[:240]}", file=sys.stderr)
        raise SystemExit(proc.returncode)
    return proc.stdout


def import_all(host: str, admin_token: str) -> None:
    run_cli(["databricks", "workspace", "mkdirs", f"{REMOTE_DIR}/training"], admin_token)
    for name in NOTEBOOKS:
        source = HERE / f"{name}.ipynb"
        run_cli([
            "databricks", "workspace", "import", f"{REMOTE_DIR}/{name}",
            "--format", "JUPYTER", "--language", "PYTHON", "--overwrite",
            "--file", str(source),
        ], admin_token)
        print(f"imported {source.relative_to(ROOT)}")
    fixture = HERE / "training/persona_labels.csv"
    run_cli([
        "databricks", "workspace", "import", f"{REMOTE_DIR}/training/persona_labels.csv",
        "--format", "RAW", "--overwrite", "--file", str(fixture),
    ], admin_token)
    print("imported notebooks/training/persona_labels.csv")

    def workspace_url(path: str) -> str:
        return f"{host}/#workspace{path}"

    links = {
        "workspace_host": host,
        "notebooks": {
            name: {
                "source": f"demos/clase-02/notebooks/{name}.ipynb",
                "workspace_path": f"{REMOTE_DIR}/{name}",
                "workspace_url": workspace_url(f"{REMOTE_DIR}/{name}"),
            }
            for name in NOTEBOOKS
        },
        "training_fixture": {
            "source": "demos/clase-02/notebooks/training/persona_labels.csv",
            "workspace_path": f"{REMOTE_DIR}/training/persona_labels.csv",
        },
    }
    # Importing notebooks again must not erase the separately managed Genie link.
    links_path = HERE / "demo-links.json"
    if links_path.exists():
        previous = json.loads(links_path.read_text(encoding="utf-8"))
        if isinstance(previous.get("genie"), dict):
            links["genie"] = previous["genie"]
    links_path.write_text(json.dumps(links, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {links_path}")


def run_notebook(host: str, agent_token: str, name: str) -> None:
    if name not in NOTEBOOKS:
        raise SystemExit(f"Unknown notebook {name!r}; choose from {', '.join(NOTEBOOKS)}")
    if not agent_token:
        raise SystemExit("Missing DATABRICKS_AGENT_TOKEN; notebook jobs must run as ai4data-agent.")
    payload = {
        "run_name": f"clase2-{name.replace('_', '-')}",
        "tasks": [{
            "task_key": "notebook",
            "notebook_task": {"notebook_path": f"{REMOTE_DIR}/{name}"},
            "environment_key": "class2",
            "timeout_seconds": 1800,
        }],
        "environments": [{
            "environment_key": "class2",
            "spec": {
                "environment_version": "5",
                "dependencies": DEPENDENCIES[name],
            },
        }],
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as request:
        json.dump(payload, request)
        request.flush()
        response = run_cli([
            "databricks", "jobs", "submit", "--json", f"@{request.name}",
            "--timeout", "30m", "-o", "json",
        ], agent_token, timeout=1900)
    run = json.loads(response)
    run_id = run.get("run_id")
    state = run.get("state", {})
    if run_id is None:
        raise SystemExit("Databricks accepted no run_id for the submitted notebook task.")
    if state.get("life_cycle_state") not in (None, "TERMINATED") or state.get("result_state") not in (None, "SUCCESS"):
        current = json.loads(run_cli(["databricks", "jobs", "get-run", str(run_id), "-o", "json"], agent_token))
        state = current.get("state", {})
        if state.get("life_cycle_state") != "TERMINATED" or state.get("result_state") != "SUCCESS":
            raise SystemExit(f"{name}: run {run_id} ended {state.get('life_cycle_state')} / {state.get('result_state')}")
        tasks = current.get("tasks", [])
    else:
        tasks = run.get("tasks", [])
    task_run_id = next((task.get("run_id") for task in tasks if task.get("task_key") == "notebook"), None)
    evidence = ""
    if task_run_id:
        output_text = run_cli([
            "databricks", "jobs", "get-run-output", str(task_run_id), "-o", "json"
        ], agent_token)
        output = json.loads(output_text)
        result = output.get("notebook_output", {}).get("result", "")
        if isinstance(result, str) and result.startswith(("C1_BUSINESS_COMPLETE|", "ML_COMPLETE|", "AI_JEV_COMPLETE|")):
            evidence = f" · {result}"
    print(f"{name}: TERMINATED SUCCESS (run {run_id}){evidence}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("import", help="import all notebooks and fixtures")
    run_parser = subparsers.add_parser("run", help="run one notebook on serverless compute")
    run_parser.add_argument("notebook", choices=NOTEBOOKS)
    subparsers.add_parser("run-all", help="run all notebooks in teaching order")
    args = parser.parse_args()
    host, admin_token, agent_token = load_credentials()
    if args.command == "import":
        import_all(host, admin_token)
    elif args.command == "run":
        run_notebook(host, agent_token, args.notebook)
    else:
        for name in NOTEBOOKS:
            run_notebook(host, agent_token, name)


if __name__ == "__main__":
    main()
