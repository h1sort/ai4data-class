#!/usr/bin/env python3
"""Build 10_trap2_walkthrough.ipynb from readable cell sources (WS3, Clase 3).

Same pattern as demos/clase-02/notebooks/build_notebooks.py: plain Python
strings -> nbformat 4.5 JSON, so the notebook source is reviewable as text
and reproducible. Run with `python3 build_10_notebook.py` from this
directory; overwrites 10_trap2_walkthrough.ipynb.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent


def cell(kind: str, source: str) -> dict:
    common = {"metadata": {}, "source": textwrap.dedent(source).strip().splitlines(keepends=True)}
    if kind == "markdown":
        return {"cell_type": "markdown", **common}
    return {"cell_type": "code", "execution_count": None, "outputs": [], **common}


CELLS = [
    cell("markdown", r'''
    # 10 · Trampa 2: Jev en vivo y `ai_classify` sobre Clase 2 real

    Este notebook lee y escribe *solo* `workspace.ai4data` (encuesta Clase 2,
    grupo D1 `8P56ZUVE9Q`). La primera celda de código lo deja explícito en
    pantalla y se niega a correr (`assert`) si alguien cambia `SCHEMA` a otra
    cosa.

    Flujo: muestra de datos → resultados ML (pre-calculados, sin reentrenar en
    vivo) → **Jev en vivo** sobre *todos* los `puesto_texto` reales de Clase 2
    (165 filas, sin el límite de 8 de `demos/clase-02/notebooks/03_llm_jev.ipynb`)
    → `ai_classify` v1 (misma taxonomía que
    `demos/clase-02/pipeline/05_ai_classify.sql`) → tabla `c3_personas_v1` →
    "¿cuántos ejecutivos?" (puente a Genie, y luego a Trampa 3).
    '''),
    cell("code", r'''
    from pyspark.sql import functions as F
    import pandas as pd
    import re

    CATALOG = "workspace"
    SCHEMA = "ai4data"
    DIM = f"{CATALOG}.{SCHEMA}.dim_participante"
    SNAPSHOTS = f"{CATALOG}.{SCHEMA}.etl_snapshots"

    assert SCHEMA == "ai4data", "este notebook sólo usa workspace.ai4data"
    print("Fuente: workspace.ai4data · encuesta Clase 2 (8P56ZUVE9Q)")

    snap = spark.sql(
        f"SELECT * FROM {SNAPSHOTS} WHERE dataset = 'class2' AND status = 'PASS' "
        "ORDER BY loaded_at_utc DESC LIMIT 1"
    ).collect()
    if snap:
        r = snap[0]
        print(
            f"Último snapshot ETL: run_id={r['run_id']} cutoff={r['cutoff_utc']} "
            f"cargado={r['loaded_at_utc']} (confianza={r['d1_votes_confianza']}, "
            f"puesto={r['d1_text_puesto']}, tarea={r['d1_text_tarea']})"
        )
    else:
        print("etl_snapshots no tiene filas PASS para class2 todavía -- corre el ETL antes de seguir.")
    '''),
    cell("markdown", r'''
    ## 1 · Muestra de datos

    Miramos algunas filas reales de `dim_participante`, incluida la basura --
    es el puente hacia Trampa 3. Redactamos automáticamente lo que parezca
    correo, teléfono, URL o nombre propio (regla de privacidad de la clase,
    ver `CLASE3-PLAN.md` regla 6); nunca se muestra `participant_key`.
    '''),
    cell("code", r'''
    def redact(text):
        """Best-effort redaction for on-screen display -- not a data-quality tool."""
        if text is None:
            return None
        t = re.sub(r"\S+@\S+", "[correo]", text)
        t = re.sub(r"https?://\S+", "[url]", t)
        t = re.sub(r"\b\d[\d\-\s]{6,}\d\b", "[numero]", t)
        t = re.sub(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\b", "[nombre]", t)
        return t

    n_total = spark.table(DIM).count()
    n_puesto = spark.table(DIM).where(F.col("puesto_texto").isNotNull()).count()
    n_tarea = spark.table(DIM).where(F.col("tarea_texto").isNotNull()).count()
    print(f"{DIM}: {n_total} participantes, {n_puesto} con puesto_texto, {n_tarea} con tarea_texto.")

    sample_rows = (
        spark.table(DIM)
        .where(F.col("puesto_texto").isNotNull())
        .select("puesto_texto")
        .orderBy("participant_key")
        .limit(10)
        .collect()
    )
    display(pd.DataFrame({"puesto_texto (redactado)": [redact(r["puesto_texto"]) for r in sample_rows]}))
    print("Muestra de 10 de 165; nada de participant_key. Ver también demos/clase-03/data/samples.md.")
    '''),
    cell("markdown", r'''
    ## 2 · ML: resultados pre-calculados (no se reentrena en vivo)

    Mismo código, mismo fixture y mismo split fijo que
    `demos/clase-02/notebooks/02_ml_classifier.ipynb`
    (`training/persona_labels.csv`, `TfidfVectorizer` + `LogisticRegression`,
    `random_state=42`). Reentrenar en vivo no aporta nada nuevo a la clase y
    consume tiempo del segmento -- por eso el resultado ya viene calculado.
    '''),
    cell("code", r'''
    # Pre-calculado hoy con el mismo código/fixture que notebook 02 (no se
    # reentrena aquí): uv run --with pandas,scikit-learn ml_prerun.py
    # -> train=60 holdout=25 accuracy=0.880  (medido 2026-09-26, ver reports/WS3.md)
    ML_TRAIN_N = 60
    ML_HOLDOUT_N = 25
    ML_ACCURACY = 0.880
    print(f"Accuracy didáctica en holdout: {ML_ACCURACY:.0%} ({ML_HOLDOUT_N} ejemplos, {ML_TRAIN_N} de entrenamiento)")
    print("Cinco clases, unas decenas de ejemplos sintéticos: ilustra el flujo, no da precisión de producción.")
    '''),
    cell("markdown", r'''
    ## 3 · Jev en vivo -- **todos** los `puesto_texto` reales (sin límite de 8)

    Mismo criterio de `persona` que
    `demos/clase-02/pipeline/06_jev.py` y
    `demos/clase-02/notebooks/03_llm_jev.ipynb`, pero sobre las 165 respuestas
    reales completas -- con `concurrent.futures` (mismo patrón de 06_jev.py)
    para no esperar una llamada a la vez. El secreto vive en el scope de
    Databricks `ai4data-class2` (`dbutils.secrets`) y nunca se imprime ni se
    persiste en una celda de salida.
    '''),
    cell("code", r'''
    import concurrent.futures
    import json
    import time
    import urllib.error
    import urllib.request

    PERSONA_LABELS = ["ejecutivo", "manager", "practitioner", "estudiante", "otro"]
    PERSONA_CRITERIA = {  # same taxonomy as 06_jev.py / notebook 03_llm_jev.ipynb
        "ejecutivo": "C-level, director/a, VP, jefe/a de área",
        "manager": "lidera un equipo; gerente, product manager",
        "practitioner": "analista, ingeniero/a, científico/a de datos que ejecuta el trabajo técnico",
        "estudiante": "estudia, becario/a, en formación",
        "otro": "no es un puesto o no encaja en las anteriores",
    }
    JEV_URL = "https://api.typesafe.ai/v1/systemone"
    API_KEY = dbutils.secrets.get(scope="ai4data-class2", key="typesafe-api-key")
    CONCURRENCY = 8  # same cap as 06_jev.py

    participants = [
        (r["participant_key"], r["puesto_texto"])
        for r in spark.table(DIM).where(F.col("puesto_texto").isNotNull()).collect()
    ]
    print(f"Jev en vivo sobre {len(participants)} títulos reales (sin límite de 8) -- concurrencia {CONCURRENCY}")

    def ask_jev(puesto):
        payload = {
            "state": f"Puesto: {puesto}",
            "model": "jev-latest",
            "questions": {
                "persona": {
                    "type": "choice",
                    "instructions": "¿Qué perfil describe mejor este puesto?",
                    "criteria": PERSONA_CRITERIA,
                }
            },
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        last_error = None
        for attempt in range(3):
            req = urllib.request.Request(
                JEV_URL, data=body,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    result = json.loads(response.read())
                answer = result.get("answers", {}).get("persona", {})
                return answer.get("choice"), answer.get("confidence")
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"Jev falló tras 3 intentos: {last_error}")

    t0 = time.time()
    jev_results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = {pool.submit(ask_jev, puesto): key for key, puesto in participants}
        done = 0
        for fut in concurrent.futures.as_completed(futures):
            key = futures[fut]
            jev_results[key] = fut.result()
            done += 1
            if done % 20 == 0 or done == len(participants):
                print(f"Jev: {done}/{len(participants)}")
    elapsed = time.time() - t0
    print(f"Jev en vivo: {len(jev_results)} clasificados en {elapsed:.1f}s (sin límite de 8 filas).")
    '''),
    cell("markdown", r'''
    ## 4 · `ai_classify` v1 -- una sola consulta set-based

    Misma taxonomía que
    `demos/clase-02/pipeline/05_ai_classify.sql` (`persona_dbx`), en **un**
    `SELECT` sobre las 165 filas -- no una llamada por fila. `ai_classify` no
    da confianza; por eso comparamos con Jev.
    '''),
    cell("code", r'''
    labels_sql = ", ".join("'" + label.replace("'", "''") + "'" for label in PERSONA_LABELS)
    ai_classify_df = spark.sql(f"""
        SELECT participant_key,
               ai_classify(puesto_texto, array({labels_sql})) AS persona_ai_classify
        FROM {DIM}
        WHERE puesto_texto IS NOT NULL
    """)
    ai_classify_df.createOrReplaceTempView("ai_classify_v1")
    n_ai = ai_classify_df.count()
    print(f"ai_classify v1: {n_ai} participantes clasificados en una sola consulta set-based.")
    '''),
    cell("markdown", r'''
    ## 5 · Tabla `c3_personas_v1`

    Combinamos Jev (con confianza) y `ai_classify` (sin confianza) por
    `participant_key`. WS4 construye v2 (defensa contra inyección) encima de
    esta misma tabla, reusando estos nombres de columna.
    '''),
    cell("code", r'''
    jev_rows = [
        (key, choice, float(conf) if conf is not None else None)
        for key, (choice, conf) in jev_results.items()
    ]
    jev_df = spark.createDataFrame(jev_rows, ["participant_key", "persona_jev", "persona_jev_confidence"])
    jev_df.createOrReplaceTempView("jev_v1")

    spark.sql(f"""
        CREATE OR REPLACE TABLE {CATALOG}.{SCHEMA}.c3_personas_v1
        COMMENT 'Trampa 2 (Clase 3): persona por participante via Jev (persona_jev, con confianza)
                 y ai_classify (persona_ai_classify, sin confianza), sobre TODO puesto_texto real de
                 Clase 2 (sin limite de 8). WS4 construye v2 encima -- mismas columnas.'
        AS
        SELECT
          COALESCE(j.participant_key, a.participant_key) AS participant_key,
          j.persona_jev,
          j.persona_jev_confidence,
          a.persona_ai_classify
        FROM jev_v1 j
        FULL OUTER JOIN ai_classify_v1 a ON a.participant_key = j.participant_key
    """)
    n_final = spark.table(f"{CATALOG}.{SCHEMA}.c3_personas_v1").count()
    print(f"{CATALOG}.{SCHEMA}.c3_personas_v1: {n_final} filas escritas (participant_key, persona_jev, persona_jev_confidence, persona_ai_classify).")
    '''),
    cell("markdown", r'''
    ## 6 · ¿Cuántos ejecutivos hay en la clase? (puente a Genie)

    Dos métodos, misma taxonomía, **números distintos** -- eso ya es parte de
    la lección: una etiqueta no es una decisión correcta por sí sola. Genie
    (siguiente paso, fuera de este notebook) responde esta misma pregunta
    sobre esta tabla.
    '''),
    cell("code", r'''
    counts = spark.sql(f"""
        SELECT
          SUM(CASE WHEN persona_jev = 'ejecutivo' THEN 1 ELSE 0 END) AS ejecutivos_jev,
          SUM(CASE WHEN persona_ai_classify = 'ejecutivo' THEN 1 ELSE 0 END) AS ejecutivos_ai_classify,
          COUNT(*) AS total
        FROM {CATALOG}.{SCHEMA}.c3_personas_v1
    """).collect()[0]
    print(f"Ejecutivos según Jev: {counts['ejecutivos_jev']} / {counts['total']}")
    print(f"Ejecutivos según ai_classify: {counts['ejecutivos_ai_classify']} / {counts['total']}")
    print("Bridge: '¿y cuántos de esos ejecutivos son reales?' -- eso es Trampa 3 (notebook 20_injection_v2).")

    dbutils.notebook.exit(
        f"TRAP2_COMPLETE|n={counts['total']}|ejecutivos_jev={counts['ejecutivos_jev']}|"
        f"ejecutivos_ai_classify={counts['ejecutivos_ai_classify']}"
    )
    '''),
]


def main() -> None:
    notebook = {
        "cells": CELLS,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out = HERE / "10_trap2_walkthrough.ipynb"
    out.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
