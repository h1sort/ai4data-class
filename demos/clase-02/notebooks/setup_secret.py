#!/usr/bin/env python3
"""Copy the local TypeSafe key into the Databricks secret scope safely.

Reads TYPESAFE_API_KEY from the repository .env, never puts it in argv or
prints it, and grants the existing ai4data-agent principal READ access.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def request(host: str, token: str, path: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        host + path,
        data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Databricks request {path} failed with HTTP {exc.code}") from None


def main() -> None:
    sys.path.insert(0, str(ROOT / "demos/clase-02/databricks"))
    import run_sql  # noqa: WPS433

    run_sql.ensure_credentials()
    host = os.environ["DATABRICKS_HOST"].rstrip("/")
    admin = os.environ["DATABRICKS_TOKEN"]
    agent = os.environ.get("DATABRICKS_AGENT_TOKEN")
    value = os.environ.get("TYPESAFE_API_KEY")
    if not value:
        raise SystemExit("Set TYPESAFE_API_KEY in the repo .env first; the value is never printed.")
    if not agent:
        raise SystemExit("Set DATABRICKS_AGENT_TOKEN in the repo .env first.")

    scope = "ai4data-class2"
    scopes = request(host, admin, "/api/2.0/secrets/scopes/list").get("scopes", [])
    if scope not in {item.get("name") for item in scopes}:
        request(host, admin, "/api/2.0/secrets/scopes/create", {
            "scope": scope,
            "scope_backend_type": "DATABRICKS",
        })
    request(host, admin, "/api/2.0/secrets/put", {
        "scope": scope,
        "key": "typesafe-api-key",
        "string_value": value,
    })
    principal = request(host, agent, "/api/2.0/preview/scim/v2/Me").get("userName")
    if not principal:
        raise SystemExit("Could not resolve the Databricks agent principal for secret access.")
    request(host, admin, "/api/2.0/secrets/acls/put", {
        "scope": scope,
        "principal": principal,
        "permission": "READ",
    })
    print(f"Configured {scope}/typesafe-api-key; secret value was not displayed.")


if __name__ == "__main__":
    main()
