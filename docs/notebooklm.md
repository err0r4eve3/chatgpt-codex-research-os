# NotebookLM Integration

NotebookLM is a first-class part of the Evidence / Trace layer. It is useful for source-centered research memory, literature Q&A, cross-source synthesis, source import, and generated study artifacts.

NotebookLM is not the source of truth for implementation behavior, experiment results, or final paper claims.

## Role In Research OS

Use NotebookLM for:

- organizing literature sources for a project
- asking source-grounded questions during P1 literature mapping
- comparing paper claims, baselines, datasets, and limitations
- exporting source summaries into `10_literature/notebooklm_exports/`
- preserving NotebookLM notebook IDs, source IDs, aliases, and sync notes in `10_literature/notebooklm_manifest.yaml`

Do not use NotebookLM for:

- replacing current repository code inspection
- replacing experiment logs or metrics
- creating unsupported manuscript claims
- storing secrets, private credentials, cookies, sensitive production details, or confidential raw datasets
- treating uncited summaries as facts

## Interface Policy

Two interfaces are supported.

CLI:

```bash
nlm --version
nlm login
nlm notebook list
nlm notebook create "<project title>"
nlm alias set <project_id> <notebook_id>
nlm source add <notebook_id> --url "https://example.com/paper"
nlm notebook query <notebook_id> "What baselines does this source justify?"
```

MCP:

- Use MCP tools when the current Codex environment exposes NotebookLM tools and the task benefits from structured tool calls.
- Use CLI when the task needs notebook creation, source management, artifact generation, aliases, profile switching, or commands not exposed by the current MCP tools.

When both are available and the task will operate on the user's NotebookLM account, ask which interface to use before taking action.

## Project Manifest

Each project must maintain:

```text
10_literature/notebooklm_manifest.yaml
10_literature/notebooklm_exports/
```

The manifest records:

- NotebookLM notebook ID and title
- preferred profile or account label
- CLI alias
- source registry
- export directory
- sync policy
- allowed and prohibited uses

The manifest is metadata. It should not contain auth tokens, cookies, private keys, or sensitive notes.

## Evidence Rules

NotebookLM output can be used as a lead, not final evidence.

Before adding a claim to `70_claims/claims.yaml`, verify it against:

- the underlying paper, benchmark, repository, or official source
- the local experiment record when the claim concerns results
- the checked-in source code when the claim concerns implementation behavior

When NotebookLM contributes to a literature claim, cite the underlying source in `10_literature/evidence_map.md`, not "NotebookLM said so."

## Recommended P1 Flow

1. Create or identify the NotebookLM notebook.
2. Add only relevant first-party sources: papers, official benchmark pages, official repositories, official docs, and human notes.
3. Record every source in `notebooklm_manifest.yaml`.
4. Ask focused questions such as:

```text
Which papers define the closest baselines?
Which datasets are repeatedly used for evaluation?
What claims are author claims rather than demonstrated facts?
Which limitations would a skeptical reviewer raise?
```

5. Export summaries into `10_literature/notebooklm_exports/`.
6. Convert verified findings into `paper_table.csv` and `evidence_map.md`.
7. Mark unverified or weak items explicitly.

## Safety

- Re-run `nlm login` if sessions expire.
- Do not use interactive `nlm chat start` from Codex; use one-shot `nlm notebook query`.
- Do not delete notebooks, sources, or artifacts without explicit confirmation.
- Do not run generation commands that require `--confirm` unless the user explicitly asked for that artifact.

See `docs/notebooklm-protocol.md` for source limits, sync rules, privacy boundaries, and citation rules.
