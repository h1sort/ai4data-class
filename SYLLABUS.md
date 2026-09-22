# Syllabus: AI for Data, from Chats to Agents

## About the course

Practical course for data professionals (analysts, data engineers, analytics engineers, data scientists, and data team leads) who want to work with LLMs and agents in production: preparing the context, configuring the harness, connecting agents to their data systems with safeguards, and measuring whether they work.

Twelve sessions in five blocks: foundations and real-world cases, working interfaces with agents, building data products, evals and security, and a final project.

The course thesis: AI has made producing an analysis almost free, but it has not made it cheaper to agree on what is true. The data team’s work shifts from producing analyses to encoding its judgment (definitions, context, controls, evals) in infrastructure so that any agent, in any interface, reaches the same correct answer.

### Learning outcomes

By the end of the course, you will be able to:

- Explain which data systems are agent-ready and choose the right stack for your use case.
- Migrate data from a transactional system to an analytical one with the help of agents, and expose it to agents securely (read-only, MCP, semantic layer).
- Work with chats, copilots, and coding agents on real data tasks, knowing what level of autonomy to use in each case.
- Configure a data harness: instruction files, skills, MCP servers, hooks, and subagents.
- Design the context (metadata, metric definitions, semantic layer) that enables an agent to get the right answer.
- Build data products with LLM APIs, structured outputs, and decision models, both inside and outside the warehouse.
- Evaluate AI systems over data using error analysis, code evaluators, and LLM-as-judge, integrated into CI.
- Identify and mitigate security risks (prompt injection through data, tool poisoning, excessive permissions).

### Who it is for

- Analysts and analytics engineers who already write SQL and want to multiply their reach.
- Data engineers who want to use agents to build and maintain pipelines without losing control.
- Data scientists and developers who will build data products with LLMs.
- Data leaders who need to decide on the stack, policies, and adoption within their team.

Prerequisite: intermediate SQL and basic Python knowledge. No prior AI experience is required.

### Requirements and tools

- Environment: terminal, VS Code, Cursor, or Devin, git, `uv` for Python.
- Data: Postgres (local or Docker), DuckDB, and a free MotherDuck account. Optional: Snowflake trial, BigQuery sandbox, or Databricks Free Edition.
- Models and agents: ideally, at least one subscription to Claude, ChatGPT, or Gemini; a coding agent (Claude Code, Codex CLI, or Gemini CLI). Free alternatives and local models (Ollama) are indicated where viable.

## Course map

| Class | Title | Block |
| --- | --- | --- |
| 1 | How the data role has changed in the AI era | 1. The agentic era of data |
| 2 | From OLTP to a Data Warehouse with agents | 1. The agentic era of data |
| 3 | Agentic data workflows | 1. The agentic era of data |
| 4 | LLMs via chat for data: from prompts to context | 2. Interfaces: chats, copilots, and harnesses |
| 5 | Copilots and coding agents for data | 2. Interfaces: chats, copilots, and harnesses |
| 6 | Your data harness: AGENTS.md, skills, MCP, hooks, and subagents | 2. Interfaces: chats, copilots, and harnesses |
| 7 | Context for agents: semantic layer, metadata, and RAG | 3. Build: context, APIs, decisions, and products |
| 8 | APIs, structured outputs, and decision models | 3. Build: context, APIs, decisions, and products |
| 9 | AI inside the warehouse and data products | 3. Build: context, APIs, decisions, and products |
| 10 | Evals I: analyzing and measuring AI systems over data | 4. Trust: evals, security, and operations |
| 11 | Evals II, security, and operations | 4. Trust: evals, security, and operations |
| 12 | Final project and the future | 5. Final project |

## Thematic blocks

### Block 1: The agentic era of data (Classes 1–3)

- Four eras of the data stack, why consensus is now the scarce resource, and what skills are in demand.
- Fundamentals: OLTP vs. OLAP; databases vs. data warehouses vs. data lakes; what makes a system “agent-ready.”
- Stacks for working with LLMs: local, lightweight cloud, and enterprise.
- Educational OLTP → warehouse migration with agents, and use of the warehouse from agents.
- Real-world cases framed as Problem → How we evaluated it → Solution → Result.

### Block 2: Interfaces: chats, copilots, and harnesses (Classes 4–6)

- How an LLM works, just enough to use it well. From prompt engineering to context engineering.
- Chats with connectors and data agents (ChatGPT Data agent, Claude with MCP and Excel, Gemini in Sheets and BigQuery).
- Copilots and coding agents: IDEs, CLIs (Claude Code, Codex, Gemini CLI), native data agents (Snowflake CoCo, Databricks Genie Code), and notebooks (marimo, Jupyter AI).
- Harness: Agent = Model + Harness. AGENTS.md, Agent Skills, MCP, hooks, subagents, and permissions.

### Block 3: Build: context, APIs, decisions, and products (Classes 7–9)

- Semantic layer, metadata, and agent-readable artifacts as context; context engineering and RAG applied to data.
- LLM APIs, tool calling, and structured outputs. From strings to typed decisions: decision models (System One Models, e.g. Jev).
- AI functions in SQL (Snowflake, Databricks, BigQuery) and platform-managed agents.
- Reference architecture and building data products: governed NLQ, automated reports, and decision pipelines.

### Block 4: Trust: evals, security, and operations (Classes 10–11)

- The Analyze → Measure → Improve cycle (Hamel Husain and Shreya Shankar) applied to data: traces, error analysis, code evaluators, and LLM-as-judge.
- Evals over the answer and over the path; consensus divergence rate across interfaces.
- ADE-bench-style task suites, evals in CI/CD, and production monitoring.
- Data agent security: prompt injection through data, tool poisoning, least privilege, and auditing.
- Cost, team adoption, and new roles.

### Block 5: Final project (Class 12)

- Agentic data product with evals, from the OLTP source to the interface, presented and defended.

## Classes

Each class includes a practical exercise and readings. The tools are mostly free or have a free tier. The course repository includes a sample OLTP dataset that is reused from Class 2 through the final project.

### Class 1: How the data role has changed in the AI era (Block 1)

Objective: understand what has really changed, what is now expected, and the mental map we will use throughout the rest of the course.

- Review of how the role has changed: four eras, four scarce resources
  - ~2013, pre-modern stack: data in silos that could not be joined, no support for JSON, one hundred million rows brought the server down. The limit was what you could query.
  - ~2016, cloud data warehouse: all the company’s data in one place, elastic compute, native semi-structured data. The limit was reaching everything.
  - ~2020, Modern Data Stack and Reverse ETL: data from any SaaS with one click, and the results sent back to operational systems. From reporting to operating.
  - ~2026, post-AI stack: producing an analysis or dashboard costs almost nothing, and anyone can do it with a different question, a different definition, and arrive at a different number. Consensus is the scarce resource.
  - What has become commoditized (repetitive code, initial EDA, dashboards, documentation) and what has increased in value (modeling, semantics, governance, judgment).
  - From writing SQL and pipelines by hand to specifying, reviewing, and orchestrating work done by agents; from producing analyses to encoding your judgment in infrastructure so that any agent can answer correctly without you in the room.
  - The dashboard stops being a destination opened on Mondays and becomes a repository of facts and definitions that agents decompose and recombine for whoever asks.
- New skills in demand
  - The two jobs of the data team today: enable everyone to build correctly and independently with data and AI, and build and defend the single reality on which the company operates.
  - Context engineering: preparing metadata, definitions, and examples so the model gets the right answer.
  - Configuring and governing agents: instruction files, skills, MCP, permissions, and review.
  - Evals: knowing how to measure whether an AI system over data works.
  - Semantic modeling and data quality: AI amplifies both the good and the bad in your warehouse.
- Fundamental concepts for the course
  - OLTP vs. OLAP: why your production database is not where an agent should read.
  - Data Warehouses vs. Data Lakes vs. Databases (and lakehouses): what each stores, for whom, and at what cost.
  - Minimum AI vocabulary: LLM, context window, tool calling, agent, MCP, skill, harness.
- Which systems are agent-ready?
  - Criteria: queryable catalog and metadata, semantic layer, access control (RBAC, row and column security), auditing, MCP endpoint or agent API, AI functions in SQL, and cost and load isolation.
  - Operable by any agent: API and MCP as first-class interfaces, not a closed UI with its own assistant. “I don’t want to use your agent; I want to use my agent to use your tool.”
  - By family: Snowflake (Cortex, managed MCP, CoCo), Databricks (Unity Catalog, Genie), BigQuery (remote MCP, AI.GENERATE), DuckDB/MotherDuck (lightweight, local-first), Postgres (pg_duckdb, read-only MCP).
- When should you choose each one?
  - Decision matrix: volume, governance, budget, team size, latency, and where your data already lives.
- What data stacks can you use to work with LLMs?
  - Local and free: Postgres or CSV/Parquet → DuckDB → coding agent with MCP.
  - Lightweight cloud: MotherDuck + dbt + coding agent.
  - Enterprise: Snowflake, Databricks, or BigQuery with their native agents and MCP.
- Closing demo: an agent answering questions about a local warehouse via MCP. Bridge to Class 2: how to build this from scratch.

### Class 2: From OLTP to a Data Warehouse with agents (Block 1)

Objective: see, from beginning to end, an educational migration from a transactional database to a system prepared for analytics and agents, built with the help of agents and then used by agents. Covers: Migration → Use.

- Starting point: an application with Postgres (OLTP), a normalized schema, and no documentation.
- Migration
  - Destination design: DuckDB/MotherDuck because it is free and educational; the pattern is the same in Snowflake, BigQuery, or Databricks.
  - Extract and load with a coding agent: `ATTACH` Postgres from DuckDB, `CREATE OR REPLACE TABLE ... AS SELECT`, idempotent and rerunnable loads.
  - Assisted analytical modeling: from normalized tables to a star schema or “silver” layer with predictable names and explicit grain.
  - Generated and reviewed documentation: table and column descriptions that will provide context for agents.
- Agent-assisted development
  - How to request the work: plan → execute → review. What to always review and what to automate with data tests.
  - Typical agent errors in migrations (types, time zones, duplicate keys, silent filters) and how to detect them.
- How to work with agents in the data warehouse
  - Expose the warehouse through MCP with a read-only role.
  - Ask questions in natural language from chat or from the coding agent; read the generated SQL; iterate on the context until it gets the right answer.
  - First contact with the semantic layer: why “revenue” needs a definition before anyone asks about it.
- Closing demo: the same question the agent answered incorrectly at first, now answered correctly just by improving the context. Bridge to Class 3: what happens when this is applied to real-world cases.

### Class 3: Agentic data workflows (Block 1)

Objective: a talk that is both motivational and practical, with cases the instructor has applied throughout their career with AI and data, in banking and other sectors, always using the same framework so they can be replicated.

- Framework for each case
  1. Context and problem: what hurt, who it affected, and what it cost.
  2. How we evaluated it: success criteria, risks, what could not go wrong, and where the human had to be involved.
  3. Solution applying AI: architecture, tools, and level of autonomy.
  4. Result and lessons: what worked, what did not, and what we would do differently today.
- Cases (banking and other sectors)
  - Classification and enrichment of free-text records at scale.
  - Documenting and migrating legacy tables and processes with agents.
  - Reconciliations and anomaly detection in reporting.
  - Recurring reports with generated narratives and verified figures.
  - Anti-cases: where AI did not pay off and why.
- Recurring patterns
  - Human in the loop where errors are costly; full automation where the result can be verified.
  - Structured decisions before free text.
  - Context matters more than the model.
- Block wrap-up: what we will build in Classes 4–12 and how it connects with the cases covered.

### Class 4: LLMs via chat for data: from prompts to context (Block 2)

- How an LLM works, just enough to use it well: tokens, context window, reasoning models, tool calling, structured outputs; why it hallucinates and in which situations.
- Choosing a model for data: frontier (Claude, GPT, Gemini) vs. open (Llama, Qwen, DeepSeek) vs. local (Ollama). Cost, latency, privacy, and quality in SQL and Python.
- From prompt engineering to context engineering: the prompt is only one part; context (schema, definitions, examples, previous results) determines quality.
  - Techniques: schema and definitions in the context, few-shot examples, asking for the SQL before the answer, requiring explicit assumptions, and step-by-step reasoning to interpret results.
- Chats with connectors and data agents: what has changed
  - ChatGPT: Data agent with connectors to Snowflake, BigQuery, Databricks, Redshift, and others; uses dbt context and semantic layers; generates dashboards.
  - Claude: Projects, MCP connectors to your warehouse, file analysis, Claude for Excel.
  - Gemini: in Sheets (`=AI()`, Fill with Gemini) and in BigQuery.
  - When chat is enough (exploration, interpretation, communication) and when it is not (reproducibility, scale, governance).
  - Connecting a vendor’s chat directly to raw data, without a semantic layer in between, is fast for one person and a reproducibility crisis for the company: every correction you make teaches the vendor about your business instead of fixing your stack. We solve this in Class 7.
- Use in data: guided EDA, translating insights for stakeholders, generating and testing hypotheses, reviewing someone else’s SQL, and documenting.
- Privacy and security in chats: what data you upload, retention, enterprise vs. consumer plans, and anonymization.
- Exercise: the same dataset in three configurations (chat without context, chat with schema and definitions, chat with a connector). Compare SQL, answers, and errors.

### Class 5: Copilots and coding agents for data (Block 2)

- Levels of autonomy: autocomplete → chat in the IDE → agent mode → background or cloud agents. Which level for which task and what risk each assumes.
- Tools
  - IDEs: Cursor, VS Code with Copilot in agent mode, Windsurf.
  - Terminal agents: Claude Code, Codex CLI, Gemini CLI, OpenCode.
  - Native data agents: Snowflake CoCo (Snowsight, Desktop, CLI), Databricks Genie Code, Gemini in BigQuery. What they provide: catalog context, RBAC, and lineage without configuration.
  - Notebooks: marimo (reactive, `.py` files, `mo.sql`), Jupyter AI, Hex, Deepnote.
- Best practices for working with coding agents on data
  - Plan first; small, verifiable tasks; git as a safety net.
  - Read-only by default against databases; separate credentials for the agent.
  - Data tests as the definition of “done” (dbt tests, assertions).
  - Review generated SQL: grain, joins, date filters, nulls, double counting, and incorrect tables.
- Use cases: dbt models, pipelines (Airflow, Dagster), debugging slow queries, migrating SQL dialects, and bulk documentation.
- Exercise: use a coding agent to build and test a dbt model on the warehouse from Class 2 and review the diff as if it came from a colleague.

### Class 6: Your data harness: AGENTS.md, skills, MCP, hooks, and subagents (Block 2)

- Agent = Model + Harness. The harness is everything that is not the model: system prompts, instruction files, tools and MCP, skills, hooks, sandbox, orchestration, permissions, and observability.
- Guides (feedforward) vs. sensors (feedback): anticipating errors vs. detecting them and allowing the agent to correct itself. Computational (tests, linters, dbt tests) vs. inferential (LLM-as-judge, review).
- Instruction files: `AGENTS.md` / `CLAUDE.md` for a data repository: naming conventions, metric definitions, reference tables, and what not to touch.
- Agent Skills, an open standard: folders with `SKILL.md` (name, description, instructions, scripts, and references); progressive disclosure. Skills for data: how to model in our dbt, how to profile a CSV, and an SQL review checklist.
- MCP (Model Context Protocol): tools, resources, and prompts. Relevant servers for data: dbt MCP (semantic layer, `text_to_sql`), Snowflake-managed MCP (Cortex Analyst, Search, and Agents as tools), remote BigQuery MCP, and read-only DuckDB and Postgres. Local vs. remote, OAuth, permissions per tool; read the descriptions of the tools you install.
- Hooks: validate SQL before executing it, block DML/DDL, format, and run tests after every change.
- Subagents: isolate context (explore the schema, write SQL, review) and parallelize.
- Evidence: ADE-bench (dbt Labs) shows that the same model solves more tasks with skills and MCP than without them. The harness matters as much as the model.
- Exercise: set up a harness for the course repository (AGENTS.md, two skills, read-only MCP to DuckDB, and a hook that blocks writes) and measure before and after with five tasks.

### Class 7: Context for agents: semantic layer, metadata, and RAG (Block 3)

- Why text-to-SQL fails: the raw schema does not carry business meaning. Cases of “correct SQL that counts the wrong thing.”
- AI-ready “silver” layer: predictable names, prescriptive descriptions, explicit grain, and complex metrics precomputed in the correct model.
- Semantic layer: metrics, dimensions, and entities defined once for people and agents (dbt Semantic Layer, Snowflake semantic views and Cortex Analyst, metrics and Genie spaces in Databricks). How agents consume it via MCP (`list_metrics`, `query_metrics`, `get_dimensions`).
- Applied context engineering: the smallest set of high-signal tokens; just-in-time retrieval instead of loading everything; compaction; “context rot.”
- RAG in data today: retrieval over documentation, tickets, and definitions; vector search in the warehouse (Cortex Search, Vector Search) as an agent tool, not a substitute for SQL.
- Metadata as a product: catalog, lineage, owners, freshness. Everything the agent can query before answering.
- Agent-readable artifacts: each data product (dashboard, model, analysis) also published for machines: a descriptor in Markdown, retrievable SQL, cached values, owners, and how it relates to the rest of the model. The equivalent of an `llms.txt` for each data product, so that your answer appears when someone asks their agent.
- Agent-agnostic context: definitions and headless connectors so that a colleague, a coding agent, a BI tool, or a Slack bot gives the same answer. Models, harnesses, and interfaces change every quarter; do not lock your company’s intelligence into a vendor’s interface.
- Why the semantic layer reached the executive committee: every “this looks strange” and every clarification of a metric is learning that compounds within your four walls or another company’s. The semantic layer is where tribal knowledge accumulates (“TPV excludes returns after day 45”) so that every question, agent, and new person starts smarter than the previous one.
- Exercise, consensus test: define five metrics in a semantic layer and ask about each one from chat, coding agent, and API. Count how many different answers come back. If there is more than one, read the traces, fix the context, and repeat until the interface no longer changes the answer.

### Class 8: APIs, structured outputs, and decision models (Block 3)

- LLM APIs (OpenAI, Anthropic, Google, and open models through providers): SDKs, streaming, tool calling, structured outputs with JSON Schema, batch, and prompt caching. Real cost and latency.
- Patterns for data: row-level enrichment (classify, extract, normalize), SQL generation with validation, table summaries, and agents with their own tools.
- From strings to decisions: when what you need is not text but a typed decision (category, score, route, extracted field) that software can use directly.
  - “Smart if-statements” in pipelines: classify, route, score, extract, and branch where a hand-written rule is fragile.
  - Confidence thresholds: automate above the threshold and require human review below it.
- Decision models / System One Models (e.g. Jev, from TypeSafe AI): unstructured input state, typed output values with calibrated probabilities; no type errors; latencies of tens or hundreds of milliseconds and costs orders of magnitude lower. Cases: map-reduce over large volumes, real time, verification, judging, and guardrails. System 1 (fast, structured) vs. System 2 (reasoning LLM): when to use each and how to combine them.
- Fine-tuning and specialized small models: when they pay off compared with prompts with more context.
- Exercise: a pipeline that classifies and extracts fields from 10,000 free-text records using (a) an LLM and structured outputs and (b) a decision model. Compare cost, latency, agreement between the two, and calibration.

### Class 9: AI inside the warehouse and data products (Block 3)

- AI functions in SQL: Snowflake (`AI_CLASSIFY`, `AI_EXTRACT` with scores, `AI_COMPLETE`), Databricks (`ai_query` and task-specific functions), BigQuery (`AI.GENERATE` with `output_schema`). Enrich data without taking it out of the warehouse; governance and cost.
- Beyond SQL: questions that do not take the form of SQL (calls, tickets, emails, contracts). Pre-model by meaning just as you model by shape: an AI labeler runs once, offline, over the entire corpus and writes structured columns (`motivo_perdida`, `tipo_objecion`, `competidor_mencionado`) that any future analysis can filter and group. The taxonomy comes from observing what users ask; the AI functions in SQL and the decision models from Class 8 are the tool.
  - Version the prompt in your infrastructure and maintain the taxonomy as a team, reviewing it with every error. Anti-pattern: delegate labeling to a vendor whose distribution changes without notice and which you cannot reproduce, debug, or revert.
- Platform-managed agents: Snowflake Cortex Agents and Snowflake Intelligence, Databricks Genie, and data agents in BigQuery. Expose them through MCP. When to use them and when to build your own.
- Building data products with LLMs
  - NLQ over governed data with a semantic layer.
  - Automated reports with generated narratives and figures verified against the warehouse.
  - Maintenance agents: documentation, lineage, anomaly detection, and query optimization.
  - Reference architecture: source → warehouse → semantic layer → MCP/API → agent → interface (Streamlit or app) → traces.
- Observability from day one: trace every call (prompt, tools, SQL, rows, response). These traces are the input for evals.
- Exercise: prototype NLQ and an automated report over the course warehouse, with traces saved.

### Class 10: Evals I: analyzing and measuring AI systems over data (Block 4)

- Why evals: without measurement there is no improvement or trust. Error analysis is the highest-return investment. The Analyze → Measure → Improve cycle (Hamel Husain and Shreya Shankar).
- Instrumentation and traces: record everything the agent did. A simple data viewer as the main tool.
- Error analysis: read traces, annotate failures openly, group them into failure modes, and prioritize. A domain expert is worth more than a committee.
- Synthetic data for discovering errors when production logs do not yet exist.
- Types of evaluators
  - Level 1, code: valid SQL, allowed tables, correct grain, comparison of results against an answer key, and data tests.
  - Level 2, LLM-as-judge validated against human criteria (agreement, biases, and when a metric is noise).
  - Level 3, A/B tests and product metrics.
- Evaluating agents: tool calls, retrieval, and multi-turn interactions. ADE-bench as a model task suite for data (task, answer key, and tests that decide pass/fail).
- Evaluate the answer and the evidence: a correct number reached through an imperfect path is worth less, and breaks with the next model, than a correct number reached through the blessed path (read the domain document, use the semantic view, execute the canonical SQL). Normalize traces into steps (`READ_DOMAIN_DOC`, `READ_SEMANTIC_VIEW`, `EXECUTE_SQL`, `SYNTHESIZE_ANSWER`) so you can make claims about the process, not just the result.
- Assume that the model never makes mistakes: your context is underspecified. The failure taxonomy is burned into fixing docs, models, and definitions, not waiting for the next frontier model.
- Exercise: 30 traces from the Class 9 product → failure taxonomy → three evaluators, at least one evaluating the path rather than the answer.

### Class 11: Evals II, security, and operations (Block 4)

- Evals in CI/CD: a task suite that runs when the prompt, model, skill, or MCP server changes; compare experiments; avoid overfitting to the suite. Snapshot the system at every run (model, prompt, tools, code, evaluation corpus, and hash of the available knowledge) so that a failure can be reproduced weeks later.
- Consensus divergence rate: percentage of questions whose answer or path changes depending on the interface or model from which they are asked. For the metrics leadership looks at every week, the goal is zero.
- Production monitoring: drift, cost, latency, and human intervention rate.
- Data agent security
  - Prompt injection through data (rows, tickets, documents) and tool poisoning (MCP tool descriptions).
  - Excessive agency: least privilege, read-only roles, row- and column-level security, query allowlists, auditing, and human approval for writes.
  - Basic red-teaming of the product before others do it.
- Cost: tokens, caching, small or decision models for repetitive tasks, and batch.
- Teams and adoption: who maintains the AGENTS.md, skills, and semantic layer; usage policies; how to measure productivity without fooling yourself.
- Exercise: a CI pipeline with evals and an injection attempt against your own product. Fix it and run the suite again.

### Class 12: Final project and the future (Block 5)

- Final project presentations: architecture, harness, evals, and live demo.
- Discussion: platform-managed vs. custom agents, decision models, standards (MCP, Agent Skills), and the role of the data professional in two years: when leadership “reads the dashboard” without ever opening it, the work is making sure the meaning survives the edit.
- Tool and lesson recap. Certification and wrap-up.

## Final project

End-to-end agentic data product with evals:

1. OLTP source → warehouse (DuckDB/MotherDuck or cloud) with a documented analytical model.
2. Semantic layer with at least five metrics.
3. Harness: `AGENTS.md`, at least one skill, read-only MCP, and hooks.
4. One product of your choice: governed NLQ, automated report, or decision pipeline (classification/extraction with confidence thresholds).
5. Evals suite (at least 20 tasks, code evaluators, and LLM-as-judge) in CI, plus a security test.
6. Consensus test: the five metrics asked about from at least two different interfaces, with the divergence rate measured and every divergence explained and corrected.

Rubric: data correctness (30%), context and harness design (25%), evals and evidence (25%), security and governance (10%), presentation (10%).

## Assessment and certification

- Practical exercises for each class.
- Final project presented in Class 12.
- Certificate upon completing the exercises and project.

## Core readings and references

- Ian Macomber, “The Shape and Feel of the Post-AI Data Stack”: https://www.iandmacomber.com/blog/post-ai-data-stack/
- Anthropic, “Effective context engineering for AI agents”: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic, “Equipping agents for the real world with Agent Skills” and the Agent Skills specification: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills · https://github.com/agentskills/agentskills
- Birgitta Böckeler (martinfowler.com), “Harness engineering for coding agent users”: https://martinfowler.com/articles/harness-engineering.html
- Addy Osmani, “Agent Harness Engineering”: https://addyosmani.com/blog/agent-harness-engineering/
- Hamel Husain and Shreya Shankar, “LLM Evals: Everything You Need to Know” and free email course: https://hamel.dev/blog/posts/evals-faq/ · https://ai.hamel.dev/eval-course
- dbt Labs, ADE-bench and “Building a better data agent benchmark”: https://github.com/dbt-labs/ade-bench · https://docs.getdbt.com/blog/building-a-better-data-agent-benchmark
- dbt Labs, dbt MCP server: https://github.com/dbt-labs/dbt-mcp
- Snowflake, managed MCP server, CoCo, and `AI_CLASSIFY` / `AI_EXTRACT` functions: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp · https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code · https://docs.snowflake.com/en/sql-reference/functions/ai_classify
- Databricks, Genie Code and AI Functions: https://docs.databricks.com/aws/en/genie-code/ · https://docs.databricks.com/aws/en/large-language-models/ai-functions
- Google Cloud, BigQuery MCP server and `AI.GENERATE`: https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp · https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-ai-generate
- MotherDuck, replicating Postgres to DuckDB/MotherDuck and pg_duckdb: https://motherduck.com/docs/key-tasks/data-warehousing/replication/postgres/ · https://github.com/duckdb/pg_duckdb
- TypeSafe AI, “Introducing System One Models & Jev”: https://typesafe.ai/blog/introducing-system-one-models-and-jev
- OpenAI, Data agent in ChatGPT Work: https://openai.com/index/put-data-to-work
- OWASP Top 10 for LLM Applications (prompt injection, excessive agency).
- Daniel Kahneman, “Thinking, Fast and Slow” (origin of the System 1 / System 2 metaphor).
