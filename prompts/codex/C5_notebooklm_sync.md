# C5: NotebookLM Sync

You are synchronizing NotebookLM metadata for a Research OS project.

Read:

- `10_literature/notebooklm_manifest.yaml`
- `10_literature/source_manifest.yaml`
- `10_literature/notebooklm_exports/export_index.yaml`
- `10_literature/evidence_map.md`
- `10_literature/paper_table.csv`
- repository `AGENTS.md`

Task:

Update NotebookLM-related project records without inventing literature facts.

Allowed work:

1. Check whether `nlm` CLI is available.
2. Check whether NotebookLM MCP tools are available in the current environment.
3. If actual NotebookLM account operations are needed and both interfaces are available, ask the user which interface to use.
4. Record canonical source metadata in `source_manifest.yaml`.
5. Record notebook IDs, import state, aliases, and sync metadata in `notebooklm_manifest.yaml`.
6. Record every NotebookLM export in `notebooklm_exports/export_index.yaml`.
7. Export useful source-grounded notes into `10_literature/notebooklm_exports/`.
8. Mark every unverified NotebookLM-derived item as `unverified`.

Forbidden:

- Do not delete notebooks, sources, or artifacts without explicit confirmation.
- Do not use `nlm chat start`.
- Do not store auth tokens, cookies, credentials, private keys, or sensitive data.
- Do not convert NotebookLM summaries into paper claims.
- Do not cite NotebookLM itself as the source for a research claim.
- Do not cite NotebookLM export files directly as supported claim evidence.

Report:

- interface used: CLI, MCP, or none
- files changed
- commands or MCP operations run
- notebook/source IDs recorded
- unverified items
- remaining manual verification needed
