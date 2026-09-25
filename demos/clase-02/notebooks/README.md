# Databricks notebooks for Clase 2

These three notebooks demonstrate aggregate business analytics, a small supervised model with a session SQL UDF, and the `ai_classify` / Jev comparison:

1. `01_business_analytics.ipynb` — Class 1 coverage, declared roles, recent AI use, and trust by role.
2. `02_ml_classifier.ipynb` — synthetic, human-labeled teaching fixture (not audience data), held-out metrics, `clasificar_persona_ml(puesto_texto)`, and bounded C2 predictions.
3. `03_llm_jev.ipynb` — the same maximum of eight titles through Databricks `ai_classify` and Jev.

Run all commands from the repository root. The C1 notebook needs the real Class 1 ETL first:

```bash
bash demos/clase-02/pipeline/etl_only.sh --dataset class1
```

Build and import the notebooks and fixture into the shared Databricks workspace:

```bash
uv run demos/clase-02/notebooks/build_notebooks.py
uv run demos/clase-02/notebooks/setup_workspace.py import
```

The import command writes notebooks to `/Shared/AI4Data/Clase2` and updates [`demo-links.json`](demo-links.json). Use a Serverless notebook. For the ML notebook, select the Standard base environment and add `scikit-learn==1.6.1` in the notebook Environment pane; the included one-time job runner configures serverless environment v5 with the pinned dependencies automatically. Serverless compute and Python UDF registration were exercised in this workspace.

After Class 2 has answers, load them before using the live portion of notebooks 02–03:

```bash
bash demos/clase-02/pipeline/etl_only.sh --dataset class2
```

The model and AI comparison use at most 50 / 8 Class 2 rows, respectively. They display aggregate class counts or class labels only; respondent text and `participant_key` are not displayed. If C2 has no job titles, notebook 03 explicitly switches to its small synthetic sample.

For notebook validation on the workspace's serverless job compute:

```bash
uv run demos/clase-02/notebooks/setup_workspace.py run-all
```

The three tasks run as the scoped `ai4data-agent` identity, report only run states, and use a Serverless Standard v5 environment. The ML task installs `scikit-learn==1.6.1`; plots use `matplotlib==3.10.0`.

## Instructor Unity Catalog access

Interactive notebook cells run as the signed-in Databricks user. Grant that
presenter table-level `SELECT` before class by running:

```bash
uv run demos/clase-02/databricks/run_sql.py -f demos/clase-02/notebooks/grant_instructor_access.sql
```

The rehearsal `SELECT` grants have already been applied for the current
presenter identity. To apply them for another instructor, run `SELECT
current_user()` in that instructor's workspace and replace
`__INSTRUCTOR_PRINCIPAL__` in the SQL file before executing it. It grants
`SELECT` only on the three C1 notebook sources and the C2 participant
dimension; it does not grant catalog- or schema-wide access.

## Jev secret

`03_llm_jev.ipynb` reads the TypeSafe key from Databricks secret scope `ai4data-class2`, key `typesafe-api-key`. Set `TYPESAFE_API_KEY` in the ignored repository `.env`, then initialize or refresh the scope with:

```bash
uv run demos/clase-02/notebooks/setup_secret.py
```

The setup script transfers the key directly into the Databricks Secrets API and never prints it, places it in a command argument, or writes it to the repository. The notebook uses the secret API, a 30-second timeout, and at most two attempts per title.

## Genie

After the Class 1 ETL creates `workspace.ai4data.c1_vw_resumen_respuestas`, create the curated Genie space and run its bounded smoke question with:

```bash
uv run demos/clase-02/notebooks/setup_genie.py
```

The space reads only the aggregate view, has five sample questions and SQL examples, and gives Genie the poll-specific denominator guidance. Its exact workspace URL and ID are recorded in `demo-links.json` after setup.

The notebooks use a shared Serverless execution environment. Databricks currently documents serverless notebook/job dependencies in its [serverless environment guide](https://docs.databricks.com/aws/en/compute/serverless/dependencies), and Python UDF registration in its [Python UDF guide](https://docs.databricks.com/aws/en/udf/python).
