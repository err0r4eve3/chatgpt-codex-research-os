---
name: notebooklm-research
description: Use NotebookLM CLI or MCP as the project literature memory layer for Research OS projects. Applies when adding sources, querying literature, exporting NotebookLM summaries, updating notebook manifests, or auditing evidence maps.
---

# NotebookLM Research Workflow

Use this skill for Research OS literature and evidence tasks that involve NotebookLM.

## Role

NotebookLM is a source-centered research memory layer. It helps organize and query literature sources, but it does not replace primary sources, repository code, experiment logs, or `claims.yaml`.

## Interface Selection

Before operating on a user's NotebookLM account:

1. Check whether MCP tools are available.
2. Check whether `nlm` CLI is available.
3. If both are available, ask the user which interface to use.
4. If only one is available, use that interface.

For local repository edits that only document or validate NotebookLM workflow, do not operate on the NotebookLM account.

## Required Project Files

Each project should contain:

```text
10_literature/notebooklm_manifest.yaml
10_literature/notebooklm_exports/README.md
```

The manifest records notebook ID, title, CLI alias, source registry, export policy, sync policy, allowed uses, and prohibited uses.

## Standard CLI Commands

Authenticate:

```bash
nlm login
nlm login --check
```

Create or inspect notebooks:

```bash
nlm notebook list
nlm notebook create "<project title>"
nlm alias set <project_id> <notebook_id>
```

Add and inspect sources:

```bash
nlm source add <notebook_id> --url "https://example.com"
nlm source list <notebook_id>
nlm source describe <source_id>
nlm source content <source_id> -o 10_literature/notebooklm_exports/<source>.txt
```

Ask one-shot source-grounded questions:

```bash
nlm notebook query <notebook_id> "Which baselines are supported by these sources?"
```

Do not use `nlm chat start` from Codex because it opens an interactive REPL.

## Evidence Rules

- Record every imported source in `notebooklm_manifest.yaml`.
- Export useful summaries to `10_literature/notebooklm_exports/`.
- Move only verified facts into `evidence_map.md`.
- Cite the underlying paper, benchmark, official repository, or official docs.
- Never cite a NotebookLM answer as the final source for a paper claim.
- Do not put auth tokens, cookies, credentials, or sensitive data in the repository.

## Deletion Safety

NotebookLM delete operations are irreversible. Do not delete notebooks, sources, notes, or generated artifacts unless the user explicitly confirms the exact item and scope.

