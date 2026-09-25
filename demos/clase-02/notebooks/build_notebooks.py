#!/usr/bin/env python3
"""Build the versioned Jupyter teaching notebooks from readable cell sources."""

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


NOTEBOOKS = {
    "01_business_analytics.ipynb": [
        cell("markdown", r'''
        # 1 · Business analytics: la encuesta de la clase 1

        **Pregunta:** ¿quién respondió, qué roles hay en la sala y cómo cambia la confianza según el rol?

        Ejecuta `bash demos/clase-02/pipeline/etl_only.sh --dataset class1` desde la raíz del repo antes de abrir este notebook. El ETL escribe las respuestas completas y una vista agregada sin identificadores. Aquí las gráficas usan esa vista; el cruce se agrega antes de mostrar resultados y nunca dibuja `participant_key`.

        Las seis preguntas y sus opciones se leen de los metadatos reales de D1. Los selectores encuentran las preguntas por texto y fallan con una instrucción clara si el wording cambia.
        '''),
        cell("code", r'''
        from pyspark.sql import functions as F
        import matplotlib.pyplot as plt
        import pandas as pd

        CATALOG = "workspace"
        SCHEMA = "ai4data"
        DIM = f"{CATALOG}.{SCHEMA}.c1_dim_participante"
        FACT = f"{CATALOG}.{SCHEMA}.c1_fct_respuestas"
        SUMMARY = f"{CATALOG}.{SCHEMA}.c1_vw_resumen_respuestas"

        def require_table(full_name):
            catalog, schema, table = full_name.split(".")
            names = {r.tableName for r in spark.sql(f"SHOW TABLES IN {catalog}.{schema}").collect()}
            if table not in names:
                raise RuntimeError(
                    f"Falta {full_name}. Ejecuta desde el repo: "
                    "bash demos/clase-02/pipeline/etl_only.sh --dataset class1"
                )

        for table in (DIM, FACT, SUMMARY):
            require_table(table)

        dim = spark.table(DIM)
        fact = spark.table(FACT)
        summary = spark.table(SUMMARY)
        n_respondents = dim.count()
        print(f"Personas únicas en la clase 1: {n_respondents:,}")
        '''),
        cell("markdown", r'''
        ## Cobertura de respuestas

        Primero contamos participantes por pregunta y usamos el total del grupo como denominador de cobertura. La barra representa respuestas recibidas; el `n` encima de cada barra hace visible el tamaño.
        '''),
        cell("code", r'''
        coverage = (
            summary.groupBy("poll_code", "pregunta")
            .agg(F.max("denominador_pregunta").alias("n_respuestas"))
            .orderBy("poll_code")
        )
        coverage_pd = coverage.toPandas()
        coverage_pd["cobertura_pct"] = 100 * coverage_pd["n_respuestas"] / n_respondents
        display(coverage_pd[["pregunta", "n_respuestas", "cobertura_pct"]].round({"cobertura_pct": 1}))

        fig, ax = plt.subplots(figsize=(11, 5))
        bars = ax.barh(coverage_pd["pregunta"], coverage_pd["n_respuestas"], color="#6c5ce7")
        ax.invert_yaxis()
        ax.set_xlabel("Respuestas")
        ax.set_title("Cobertura de las preguntas de la clase 1")
        ax.set_xlim(0, max(n_respondents, int(coverage_pd["n_respuestas"].max())) * 1.12)
        for bar, n in zip(bars, coverage_pd["n_respuestas"]):
            ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2, f"{int(n)}", va="center")
        fig.tight_layout()
        display(fig)
        plt.close(fig)
        '''),
        cell("markdown", r'''
        ## Distribución de roles declarados

        La pregunta y las categorías vienen de D1. Solo representamos la vista agregada.
        '''),
        cell("code", r'''
        questions = [r.pregunta for r in fact.select("pregunta").distinct().collect()]

        def find_question(fragment):
            matches = [q for q in questions if fragment.casefold() in q.casefold()]
            if len(matches) != 1:
                raise ValueError(
                    f"Esperaba una pregunta que contenga {fragment!r}; encontré {len(matches)}. "
                    f"Preguntas disponibles: {questions}"
                )
            return matches[0]

        role_q = find_question("trabajo principal")
        role_pd = (
            summary.where(F.col("pregunta") == role_q)
            .select("respuesta", "n_respuestas", "porcentaje")
            .orderBy(F.desc("n_respuestas"))
            .toPandas()
        )
        display(role_pd)

        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.bar(role_pd["respuesta"], role_pd["n_respuestas"], color="#00b894")
        ax.set_ylabel("Personas")
        ax.set_title("Trabajo principal declarado")
        ax.tick_params(axis="x", labelrotation=25)
        for bar, pct in zip(bars, role_pd["porcentaje"]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"{pct:.1f}%", ha="center", fontsize=9)
        fig.tight_layout()
        display(fig)
        plt.close(fig)
        '''),
        cell("markdown", r'''
        ## ¿Cambia la confianza por rol?

        Unimos tres respuestas de la misma persona dentro del cómputo distribuido y agregamos antes de traer nada al notebook. La tabla y las gráficas solo contienen grupos: cada `n` cuenta personas con las tres respuestas.
        '''),
        cell("code", r'''
        ai_use_q = find_question("últimos 7 días")
        trust_q = find_question("en un análisis generado por IA")
        role_q = find_question("trabajo principal")

        selected = fact.where(F.col("pregunta").isin(role_q, ai_use_q, trust_q))
        by_person = selected.groupBy("participant_key").agg(
            F.max(F.when(F.col("pregunta") == role_q, F.col("respuesta"))).alias("rol"),
            F.max(F.when(F.col("pregunta") == ai_use_q, F.col("respuesta"))).alias("uso_ia_7d"),
            F.max(F.when(F.col("pregunta") == trust_q, F.col("respuesta").cast("double"))).alias("confianza"),
        )
        complete = by_person.where(
            F.col("rol").isNotNull() & F.col("uso_ia_7d").isNotNull() & F.col("confianza").isNotNull()
        )
        by_role = (
            complete.groupBy("rol")
            .agg(
                F.count("*").alias("n"),
                F.round(100 * F.avg(F.when(F.lower("uso_ia_7d") == "sí", 1.0).otherwise(0.0)), 1)
                 .alias("uso_ia_7d_pct"),
                F.round(F.avg("confianza"), 2).alias("confianza_media"),
            )
            .orderBy(F.desc("n"))
        )
        by_role_pd = by_role.toPandas()
        display(by_role_pd)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        axes[0].bar(by_role_pd["rol"], by_role_pd["uso_ia_7d_pct"], color="#fdcb6e")
        axes[0].set_title("Usó IA en los últimos 7 días")
        axes[0].set_ylabel("Personas (%)")
        axes[0].set_ylim(0, 100)
        axes[1].bar(by_role_pd["rol"], by_role_pd["confianza_media"], color="#74b9ff")
        axes[1].set_title("Confianza en análisis generado por IA")
        axes[1].set_ylabel("Promedio (1–5)")
        axes[1].set_ylim(0, 5)
        for ax in axes:
            ax.tick_params(axis="x", labelrotation=25)
            for label in ax.get_xticklabels():
                label.set_ha("right")
        fig.suptitle("Misma cohorte con rol, uso reciente y confianza · n por rol en la tabla")
        fig.tight_layout()
        display(fig)
        plt.close(fig)
        print("Listo. Casi: buenas métricas requieren definiciones acordadas y capacidad de actuar.")
        dbutils.notebook.exit(
            f"C1_BUSINESS_COMPLETE|respondents={n_respondents}|questions={len(coverage_pd)}|"
            f"roles={len(role_pd)}|cross_tab_roles={len(by_role_pd)}"
        )
        '''),
    ],
    "02_ml_classifier.ipynb": [
        cell("markdown", r'''
        # 2 · ML: una columna nueva para clasificar puestos

        Entrenamos un clasificador de texto pequeño y legible con ejemplos de enseñanza etiquetados por una persona. El split `train/test` está fijado en el fixture, así que la evaluación no cambia entre ejecuciones. Son títulos sintéticos, no respuestas etiquetadas por un modelo; cinco clases y unas decenas de ejemplos solo ilustran el flujo, no dan precisión de producción.

        Al final registramos la función Python como `clasificar_persona_ml(puesto_texto)` dentro de la sesión Spark y la invocamos desde SQL contra títulos sintéticos y, si ya existe, contra la encuesta C2. El texto de participantes no se muestra; la consulta final devuelve solo conteos por clase.

        **Compute:** Serverless notebook con `scikit-learn==1.6.1` y `matplotlib==3.10.0`. En el panel *Environment*, agrega `scikit-learn==1.6.1` antes de ejecutar; el runner del repo ya lo instala en la tarea.
        '''),
        cell("code", r'''
        import pandas as pd
        import matplotlib.pyplot as plt
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay
        from sklearn.pipeline import Pipeline

        FIXTURE = "/Workspace/Shared/AI4Data/Clase2/training/persona_labels.csv"
        CATALOG = "workspace"
        SCHEMA = "ai4data"
        DIM = f"{CATALOG}.{SCHEMA}.dim_participante"

        labels = pd.read_csv(FIXTURE)
        train = labels.loc[labels["split"] == "train"].copy()
        holdout = labels.loc[labels["split"] == "test"].copy()
        classes = ["ejecutivo", "manager", "practitioner", "estudiante", "otro"]
        assert set(train["persona_esperada"]) == set(classes)
        assert set(holdout["persona_esperada"]) == set(classes)
        assert set(train["puesto_texto"]).isdisjoint(set(holdout["puesto_texto"]))
        print(f"Ejemplos etiquetados: {len(train)} train + {len(holdout)} holdout, por diseño humano")

        model = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True, strip_accents="unicode")),
            ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)),
        ])
        model.fit(train["puesto_texto"], train["persona_esperada"])
        holdout["prediccion"] = model.predict(holdout["puesto_texto"])
        accuracy = accuracy_score(holdout["persona_esperada"], holdout["prediccion"])
        report_raw = classification_report(
            holdout["persona_esperada"], holdout["prediccion"], labels=classes,
            output_dict=True, zero_division=0
        )
        report = pd.DataFrame.from_dict(
            {key: value for key, value in report_raw.items() if isinstance(value, dict)},
            orient="index"
        )
        print(f"Accuracy didáctica en holdout: {accuracy:.0%} ({len(holdout)} ejemplos)")
        display(report.loc[classes, ["precision", "recall", "f1-score", "support"]].round(2))
        fig, ax = plt.subplots(figsize=(7, 6))
        ConfusionMatrixDisplay.from_predictions(
            holdout["persona_esperada"], holdout["prediccion"], labels=classes,
            display_labels=classes, xticks_rotation=30, cmap="Purples", ax=ax, colorbar=False
        )
        ax.set_title("Holdout sintético · no es precisión de producción")
        fig.tight_layout()
        display(fig)
        plt.close(fig)
        display(holdout[["puesto_texto", "persona_esperada", "prediccion"]].sort_values("persona_esperada"))
        '''),
        cell("markdown", r'''
        ## Publicar la predicción como función SQL de sesión

        Esta es una UDF de Python registrada para la sesión actual. No crea una función permanente en el catálogo.
        '''),
        cell("code", r'''
        from pyspark.sql import functions as F
        from pyspark.sql.types import StringType

        def predict_persona(text):
            if text is None or not text.strip():
                return None
            # The fitted teaching model is small enough to serialize with the UDF.
            # Serverless notebooks do not expose SparkContext/broadcast variables.
            return str(model.predict([text])[0])

        clasificar_persona_udf = F.udf(predict_persona, StringType())
        spark.udf.register("clasificar_persona_ml", clasificar_persona_udf)
        print("Función de sesión lista: clasificar_persona_ml(puesto_texto)")

        spark.createDataFrame(
            [(str(title),) for title in holdout["puesto_texto"].tolist()], ["puesto_texto"]
        ).createOrReplaceTempView("titulos_holdout")
        sql_preview = spark.sql("""
            SELECT puesto_texto, clasificar_persona_ml(puesto_texto) AS persona_predicha
            FROM titulos_holdout
            ORDER BY puesto_texto
        """)
        display(sql_preview)
        '''),
        cell("markdown", r'''
        ## Aplicarlo a C2

        Cuando el ETL de C2 ya haya creado `workspace.ai4data.dim_participante`, esta consulta clasifica como máximo 50 títulos y solo muestra conteos. Si el poll todavía no tiene respuestas o falta el ETL, la función queda demostrada con el holdout sintético de arriba.
        '''),
        cell("code", r'''
        live_title_count = 0
        try:
            catalog, schema, table = DIM.split(".")
            available = {r.tableName for r in spark.sql(f"SHOW TABLES IN {catalog}.{schema}").collect()}
            if table not in available:
                print("C2 todavía no tiene tabla modelada. Ejecuta: bash demos/clase-02/pipeline/etl_only.sh --dataset class2")
            else:
                live = (
                    spark.table(DIM)
                    .where(F.col("puesto_texto").isNotNull())
                    .select("puesto_texto")
                    .limit(50)
                    .withColumn("persona_ml", F.expr("clasificar_persona_ml(puesto_texto)"))
                )
                live_rows = live.groupBy("persona_ml").count().orderBy(F.desc("count")).collect()
                live_title_count = sum(row["count"] for row in live_rows)
                if live_title_count:
                    display(spark.createDataFrame(live_rows))
                    print("Muestra limitada a 50; no se mostraron títulos ni identificadores.")
                else:
                    print("C2 tiene 0 títulos todavía; la UDF se validó con el holdout etiquetado de arriba.")
        except Exception as exc:
            if "TABLE_OR_VIEW_NOT_FOUND" in str(exc) or "SCHEMA_NOT_FOUND" in str(exc):
                print("C2 aún no está cargada; la demo SQL con el fixture sí quedó ejecutada arriba.")
            else:
                raise
        print("Una etiqueta no es una decisión correcta por sí sola: necesitamos más ejemplos representativos y una persona responsable del modelo.")
        dbutils.notebook.exit(
            f"ML_COMPLETE|train={len(train)}|holdout={len(holdout)}|accuracy={accuracy:.3f}|"
            f"live_titles={live_title_count}"
        )
        '''),
    ],
    "03_llm_jev.ipynb": [
        cell("markdown", r'''
        # 3 · ai_classify y Jev: pedir una decisión con el mismo criterio

        Comparamos la función de Databricks `ai_classify` con Jev sobre los **mismos ocho títulos como máximo** y la misma taxonomía. Si el poll C2 aún no tiene títulos, el notebook declara que usa el pequeño conjunto sintético de enseñanza. Las respuestas de participantes se procesan de forma acotada y nunca aparecen en una salida; el cuadro enseña solo clase, confianza y latencia.

        Jev usa el secreto de Databricks `ai4data-class2 / typesafe-api-key`. Para crear o reemplazarlo desde `.env`, ejecuta `uv run demos/clase-02/notebooks/setup_secret.py`. El notebook nunca imprime ni persiste el valor.

        La coincidencia entre sistemas no es exactitud. Sin etiquetas humanas independientes solo medimos acuerdo, cobertura, confianza y tiempo.
        '''),
        cell("code", r'''
        import json
        import time
        import urllib.error
        import urllib.request
        import pandas as pd
        from pyspark.sql import functions as F

        CATALOG = "workspace"
        SCHEMA = "ai4data"
        DIM = f"{CATALOG}.{SCHEMA}.dim_participante"
        MAX_SAMPLE = 8
        PERSONA_LABELS = ["ejecutivo", "manager", "practitioner", "estudiante", "otro"]
        PERSONA_CRITERIA = {
            "ejecutivo": "C-level, director/a, VP, jefe/a de área",
            "manager": "lidera un equipo; gerente, product manager",
            "practitioner": "analista, ingeniero/a, científico/a de datos que ejecuta trabajo técnico",
            "estudiante": "estudia, becario/a, en formación",
            "otro": "no es un puesto o no encaja en las anteriores",
        }

        synthetic_titles = [
            "VP de Data", "Gerente de producto digital", "Ingeniera de datos",
            "Estudiante de estadística", "Diseñador gráfico", "Jefa de analítica",
            "Machine Learning Engineer", "Médico internista",
        ]
        titles = []
        try:
            catalog, schema, table = DIM.split(".")
            available = {r.tableName for r in spark.sql(f"SHOW TABLES IN {catalog}.{schema}").collect()}
            if table in available:
                titles = [
                    r.puesto_texto for r in (
                        spark.table(DIM)
                        .where(F.col("puesto_texto").isNotNull() & (F.length(F.trim("puesto_texto")) > 0))
                        .orderBy("participant_key")
                        .select("puesto_texto")
                        .limit(MAX_SAMPLE)
                        .collect()
                    )
                ]
        except Exception as exc:
            if "TABLE_OR_VIEW_NOT_FOUND" not in str(exc) and "SCHEMA_NOT_FOUND" not in str(exc):
                raise

        if titles:
            SAMPLE_SOURCE = "C2 · respuestas en vivo (muestra acotada)"
        else:
            titles = synthetic_titles[:MAX_SAMPLE]
            SAMPLE_SOURCE = "fixture sintético · el poll C2 sigue vacío o no se ha cargado"
        print(f"Fuente: {SAMPLE_SOURCE}; títulos procesados: {len(titles)}")
        '''),
        cell("markdown", r'''
        ## Primera decisión: `ai_classify`

        Ejecutamos una sola consulta sobre la muestra. No seleccionamos el texto al resultado visible.
        '''),
        cell("code", r'''
        inputs = spark.createDataFrame(
            [(i + 1, title) for i, title in enumerate(titles)],
            ["muestra", "puesto_texto"]
        )
        labels_sql = ", ".join("'" + label.replace("'", "''") + "'" for label in PERSONA_LABELS)
        ai_rows = (
            inputs.select(
                "muestra",
                F.expr(f"ai_classify(puesto_texto, array({labels_sql}))").alias("ai_classify"),
            )
            .orderBy("muestra")
            .collect()
        )
        ai_by_sample = {int(r.muestra): r.ai_classify for r in ai_rows}
        display(pd.DataFrame([
            {"muestra": i, "ai_classify": ai_by_sample.get(i)}
            for i in range(1, len(titles) + 1)
        ]))
        '''),
        cell("markdown", r'''
        ## Segunda decisión: Jev

        La llamada está limitada a ocho títulos, tiene timeout y hasta dos reintentos. El secreto no entra en la celda de salida.
        '''),
        cell("code", r'''
        API_URL = "https://api.typesafe.ai/v1/systemone"
        API_KEY = dbutils.secrets.get(scope="ai4data-class2", key="typesafe-api-key")

        def ask_jev(title):
            payload = {
                "state": f"Puesto: {title}",
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
            for attempt in range(2):
                req = urllib.request.Request(API_URL, data=body, headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                }, method="POST")
                started = time.perf_counter()
                try:
                    with urllib.request.urlopen(req, timeout=30) as response:
                        result = json.loads(response.read())
                    answer = result.get("answers", {}).get("persona", {})
                    return {
                        "persona_jev": answer.get("choice"),
                        "confianza_jev": answer.get("confidence"),
                        "latencia_jev_ms": round((time.perf_counter() - started) * 1000),
                        "modelo_jev": result.get("model"),
                    }
                except (urllib.error.URLError, TimeoutError) as exc:
                    last_error = exc
                    if attempt == 0:
                        time.sleep(1)
            raise RuntimeError(f"Jev falló después de dos intentos: {last_error}")

        jev_rows = [ask_jev(title) for title in titles]
        '''),
        cell("markdown", r'''
        ## Comparación de resultados

        Mostramos solo etiquetas y medidas operativas: ningún título ni clave de participante sale en la tabla.
        '''),
        cell("code", r'''
        comparison = pd.DataFrame([
            {
                "muestra": i,
                "ai_classify": ai_by_sample.get(i),
                "Jev": jev_rows[i - 1]["persona_jev"],
                "confianza Jev": jev_rows[i - 1]["confianza_jev"],
                "latencia Jev (ms)": jev_rows[i - 1]["latencia_jev_ms"],
            }
            for i in range(1, len(titles) + 1)
        ])
        comparison["acuerdo"] = comparison["ai_classify"] == comparison["Jev"]
        display(comparison)
        agreement = comparison["acuerdo"].mean() if len(comparison) else float("nan")
        print(f"Acuerdo entre métodos: {agreement:.0%}. Esto no mide exactitud.")
        print("Para medir exactitud necesitamos títulos con etiquetas independientes, representativos de la población y revisados por personas.")
        dbutils.notebook.exit(
            f"AI_JEV_COMPLETE|source={SAMPLE_SOURCE}|n={len(comparison)}|agreement={agreement:.3f}"
        )
        '''),
    ],
}


def main() -> None:
    for filename, cells in NOTEBOOKS.items():
        notebook = {
            "cells": cells,
            "metadata": {
                "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                "language_info": {"name": "python"},
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        path = HERE / filename
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {path.relative_to(HERE)} ({len(cells)} cells)")


if __name__ == "__main__":
    main()
