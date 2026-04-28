# Manual Operation Protocol

This workflow is deliberately human-in-the-loop. Do not automate model calls across stages without human review.

## Loop

```text
1. Human gives project status and prior-stage artifacts to Pro.
2. Pro creates the next task card.
3. Human reviews, edits, accepts, or rejects the task card.
4. Human gives the approved engineering task to Codex.
5. Codex produces code diff, logs, tests, and a concise report.
6. Human gives Codex's report back to Pro.
7. Pro audits and recommends continue / revise / kill.
```

## NotebookLM Loop

Use this loop during literature-heavy stages:

```text
1. Human or Codex adds verified sources to NotebookLM.
2. Source IDs are recorded in notebooklm_manifest.yaml.
3. Pro asks focused source-grounded questions.
4. Human or Codex exports useful summaries to notebooklm_exports/.
5. Findings are checked against underlying sources.
6. Verified facts move into evidence_map.md or paper_table.csv.
```

NotebookLM output should not skip the evidence gate. Treat it as organized memory and source Q&A, not as final authority.

## Codex Task Shape

Good Codex tasks are engineering tasks:

- implement baseline A
- write `scripts/run_experiment.py`
- add `metrics.json` output
- fix memory leak
- generate main experiment table from metrics
- check failed runs are recorded

Bad Codex tasks:

- write the whole paper
- prove the method is novel
- make results look better
- create a SOTA claim

## Batch Rule

Batch ideas, not papers:

```text
30 ideas
  -> 10 literature-checked
  -> 5 novelty/feasibility-gated
  -> 3 minimum experiments
  -> 1 full experiment
  -> 0 or 1 draft
```

Every idea must be killable.
