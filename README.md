# Human-in-the-loop Research OS

This repository stores a reusable pipeline for computer-science research with ChatGPT Pro and Codex.

The system is not a paper generator. It is a human-reviewed research operating system:

```text
Pro model = research control plane
Codex = engineering execution plane
experiment logs / metrics / citations / claim trace = evidence plane
paper = compiled artifact from evidence
```

The central rule is simple:

```text
evidence first
claims second
paper last
```

Every publishable claim must be traceable back to experiment commands, logs, code commits, dataset versions, statistical checks, and literature evidence.

## Repository Layout

```text
.
  AGENTS.md                  Repository rules for Codex
  docs/                      Architecture, workflow, quality gates, references
  prompts/
    pro/                     ChatGPT Pro research-controller prompts
    codex/                   Codex engineering-executor prompts
  schemas/                   Lightweight artifact contracts
  scripts/
    new_project.py           Create a project from templates/project
    validate_artifacts.py    Validate required project files and basic contracts
  templates/project/         Auditable research project template
  projects/                  Real research projects created from the template
  .agents/skills/            Repository-specific reusable workflows
```

## Quick Start

Create a project:

```bash
python scripts/new_project.py 2026-04-graph-cache-optimization
```

On Windows environments where `python` is the Microsoft Store shim, use `py -3` instead of `python`.

Validate its structure:

```bash
python scripts/validate_artifacts.py --project projects/2026-04-graph-cache-optimization
```

Validate the project template:

```bash
python scripts/validate_artifacts.py --template
```

Then work one stage at a time:

```text
P0 topic intake
P1 literature map
P2 idea pool
P3 novelty / feasibility gate
P4 experiment design
C1 implementation
C2 baseline alignment
C3 experiment runs
P5 result audit
P6 claim trace
P7 paper draft
P8 adversarial review
P9 human final decision
```

## Core Discipline

- The human PI chooses directions, approves gates, and owns final responsibility.
- ChatGPT Pro plans, critiques, and drafts only from approved evidence.
- Codex implements, tests, runs, extracts, and reports engineering work.
- `50_runs/` stores real execution records.
- `70_claims/claims.yaml` is the authority for what may appear in the paper.
- `80_manuscript/` is generated from evidence, not used as a source of truth.
- NotebookLM is used for source-centered literature memory via `10_literature/source_manifest.yaml`, `notebooklm_manifest.yaml`, and `notebooklm_exports/export_index.yaml`; exports must be verified against underlying sources and cannot directly support `claims.yaml`.

## Minimum Viable Use

The MVP is one idea that completes the loop:

```text
research_spec -> experiment_spec -> minimal code -> smoke run -> metrics -> claims.yaml -> draft
```

Success means reproducible evidence and traceable claims, not necessarily a publishable paper.
