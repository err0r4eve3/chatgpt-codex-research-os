# Pipeline Workflow

## Stage Machine

```text
P0 topic intake
  -> P1 literature map
  -> P2 idea pool
  -> P3 novelty / feasibility gate
  -> P4 experiment design
  -> C1 Codex implementation
  -> C2 baseline alignment
  -> C3 experiment runs
  -> P5 result audit
  -> P6 claim trace
  -> P7 paper draft
  -> P8 adversarial review
  -> P9 human final decision
```

`P` stages are handled by the Pro research controller.

`C` stages are handled by the Codex engineering executor.

## Stage Contracts

| Stage | Goal | Main Owner | Key Output | Gate |
| --- | --- | --- | --- | --- |
| P0 | Define research boundary | Pro + human | `00_intake/problem_brief.md` | Question is measurable |
| P1 | Avoid duplicate work | Pro + NotebookLM | `10_literature/paper_table.csv`, `evidence_map.md`, `notebooklm_manifest.yaml` | Core baselines covered |
| P2 | Generate candidates | Pro | `20_ideas/idea_pool.json` | Ideas are experimentally testable |
| P3 | Filter weak ideas | Pro + human | `20_ideas/selected_idea.md` | 1-3 ideas remain |
| P4 | Freeze experiment protocol | Pro + Codex feasibility check | `30_specs/experiment_spec.yaml` | Experiment is reproducible |
| C1 | Implement method | Codex | code diff, tests | Unit tests pass |
| C2 | Align baselines | Codex | `30_specs/baseline_spec.yaml`, baseline code | Same data, budget, metrics |
| C3 | Run matrix | Codex | `50_runs/*` | Logs complete |
| P5 | Audit results | Pro + human | `60_analysis/result_summary.md` | Conclusions have evidence |
| P6 | Bind claims to evidence | Pro | `70_claims/claims.yaml` | No unsupported claims |
| P7 | Draft paper | Pro | `80_manuscript/*` | Draft stays within evidence |
| P8 | Simulate review | Pro | `90_reviews/adversarial_review.md` | Major holes can be answered |
| P9 | Decide | human | `99_archive/final_package/` | Human accepts responsibility |

## Daily Operating Rule

Advance one state transition per work session when possible. Avoid asking Codex to implement an entire paper system in one task.

## NotebookLM Checkpoints

- P1: create or link a NotebookLM notebook, ingest verified literature sources, and record IDs in `10_literature/notebooklm_manifest.yaml`.
- P3: query the notebook for novelty and baseline risks, then verify against underlying sources.
- P5: use NotebookLM only to audit written summaries against sources; use repository logs and metrics for experimental truth.
- P7: draft only from `claims.yaml`, `result_summary.md`, and source-grounded literature notes.
