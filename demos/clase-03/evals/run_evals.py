#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["langchain-anthropic>=0.3.0", "langchain-core>=0.3.0", "duckdb>=1.0.0"]
# ///
"""Suite de evals de las 3 trampas de Clase 3: pregunta -> comportamiento
esperado -> chequeo programático. Imprime una tabla roja/verde y puede correr
en modo "antes" (el bug), "después" (con la corrección) o ambos.

uv run demos/clase-03/evals/run_evals.py                # antes y después
uv run demos/clase-03/evals/run_evals.py --mode before   # solo antes (debería salir todo rojo)
uv run demos/clase-03/evals/run_evals.py --mode after    # solo después (debería salir todo verde)
uv run demos/clase-03/evals/run_evals.py --case trampa2_datos_viejos
"""
from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "agent"))
import agent  # noqa: E402
from cases import CASES, EvalCase  # noqa: E402

RED, GREEN, YELLOW, RESET = "\033[91m", "\033[92m", "\033[93m", "\033[0m"
CELL_W = 12


def label(ok: bool | None) -> str:
    return "N/A" if ok is None else ("VERDE" if ok else "ROJO")


def _color(ok: bool | None) -> str:
    return YELLOW if ok is None else (GREEN if ok else RED)


def cell(ok: bool | None) -> str:
    """Centra el texto plano primero y recién ahí lo pinta, para que los
    códigos de color no rompan el ancho visible de la columna."""
    return _color(ok) + label(ok).center(CELL_W) + RESET


def paint_inline(ok: bool | None) -> str:
    return _color(ok) + label(ok) + RESET


def run_one(case: EvalCase, mode: str) -> tuple[bool, str, dict]:
    kwargs = case.after if mode == "after" else case.before
    try:
        result = agent.run(case.pregunta, **kwargs)
    except Exception as exc:  # una falla de red/API no debe tumbar toda la suite
        return False, f"error corriendo el agente: {exc}", {"answer": "", "tool_calls": []}
    ok, detail = case.check(result)
    return ok, detail, result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=("before", "after", "both"), default="both")
    parser.add_argument("--case", help="corre solo el caso con este id")
    args = parser.parse_args()

    cases = [c for c in CASES if c.id == args.case] if args.case else CASES
    if not cases:
        print(f"error: no existe el caso {args.case!r}", file=sys.stderr)
        return 2
    modes = ["before", "after"] if args.mode == "both" else [args.mode]

    rows: dict[str, dict[str, bool]] = {}
    print(f"\n=== Evals Clase 3 · modo={args.mode} · {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M UTC} ===\n")
    for case in cases:
        print(f"--- {case.id} " + "-" * max(0, 60 - len(case.id)))
        print(f"pregunta: {case.pregunta}")
        print(f"esperado: {case.comportamiento_esperado}")
        rows[case.id] = {}
        for mode in modes:
            print(f"\n[{mode}] corriendo el agente...")
            ok, detail, result = run_one(case, mode)
            rows[case.id][mode] = ok
            print(f"[{mode}] veredicto: {paint_inline(ok)} -- {detail}")
        print()

    col_w = max(len(c.id) for c in cases) + 2
    header = "CASO".ljust(col_w) + "".join(m.upper().center(CELL_W) for m in modes)
    rule = "=" * (col_w + CELL_W * len(modes))
    print(rule)
    print(header)
    print("-" * len(rule))
    for case in cases:
        line = case.id.ljust(col_w) + "".join(cell(rows[case.id][m]) for m in modes)
        print(line)
    print(rule)

    if args.mode == "both":
        # In the teaching run, red before and green after is the expected result.
        contrast_ok = all(not r["before"] and r["after"] for r in rows.values())
        return 0 if contrast_ok else 1
    all_ok = all(v for r in rows.values() for v in r.values())
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
