# AGENTS.md

## Role

You are working in a Human-in-the-loop Research OS repository for computer-science research.

Treat this repository as an audit system, not a manuscript generator. Do not invent research claims, experiment results, citations, or baselines.

## Project Structure

- `docs/`: repository-level architecture, workflow, gates, and source notes.
- `prompts/pro/`: prompts for the research-control plane.
- `prompts/codex/`: prompts for the engineering-execution plane.
- `schemas/`: lightweight artifact contracts.
- `scripts/`: standard-library project tooling.
- `templates/project/`: source template for new research projects.
- `projects/`: real project instances created from the template.
- `.agents/skills/notebooklm-research/`: repository workflow for NotebookLM CLI/MCP-backed literature work.

## Common Commands

Create a project:

```bash
python scripts/new_project.py <project_id>
```

On Windows environments where `python` is the Microsoft Store shim, use `py -3` instead of `python`.

Validate a project:

```bash
python scripts/validate_artifacts.py --project projects/<project_id>
```

Validate the template:

```bash
python scripts/validate_artifacts.py --template
```

Validate all projects:

```bash
python scripts/validate_artifacts.py --all
```

## Research Rules

- Do not write a manuscript claim unless it exists in `70_claims/claims.yaml` with `status: supported`.
- Do not convert `inconclusive`, `contradicted`, or `rejected` findings into positive claims.
- Do not claim SOTA unless `claims.yaml` explicitly supports it with fair baselines and citations.
- Do not delete failed runs or negative results.
- Keep literature evidence in `10_literature/`; keep implementation outputs in `50_runs/`; keep conclusions in `70_claims/`.
- Use NotebookLM only as source-centered research memory. Verify NotebookLM answers against underlying sources before adding facts or claims.
- Keep NotebookLM notebook IDs, source IDs, aliases, and exports in `10_literature/notebooklm_manifest.yaml` and `10_literature/notebooklm_exports/`.
- Prefer small, reviewable stage transitions over broad rewrites.

## Engineering Rules

- Make minimal targeted changes.
- Prefer standard-library scripts unless the repository already declares a dependency.
- Do not add generated, vendored, or large binary artifacts unless explicitly requested.
- Do not hard-code metrics into tables or figures.
- All experiment scripts must write deterministic output directories and preserve command, config, logs, metrics, environment, and git commit.

## Validation Expectations

Before claiming repository changes are complete, run the smallest relevant check:

```bash
python scripts/validate_artifacts.py --all
```

If a project contains executable experiment code under `40_code/repo/`, also follow that sub-repository's `AGENTS.md`.

## Final Response Expectations

Report:

1. What changed.
2. Commands run and results.
3. Files changed when useful.
4. Any unverified items or remaining risks.
