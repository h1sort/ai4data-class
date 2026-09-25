# Poll aggregate through D1 MCP

For the agent demo, ask the agent to run the SQL in
[poll_aggregate.sql](poll_aggregate.sql) with the D1 MCP
`mcp__cloudflare_bindings__d1_database_query` tool against the
`h1sort-chat` database. Use database ID
`ac2b339f-8f2a-40ca-90d1-e4ec963c555c` in this configured workspace.

The query is bounded to today's immutable confidence poll and returns only
the question, option labels, and vote counts. It does not read participant
hashes or free-text answers. The direct CLI equivalent is
`uv run demos/clase-02/live.py poll` from the repository root.
