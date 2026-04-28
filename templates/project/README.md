# __PROJECT_TITLE__

Project id: `__PROJECT_ID__`

This directory is a research audit workspace. The manuscript is not the source of truth.

## Current Stage

Update `STATUS.md` after each stage transition.

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

## Source of Truth

- Research boundary: `00_intake/`
- Literature evidence: `10_literature/`
- NotebookLM literature memory: `10_literature/notebooklm_manifest.yaml`
- Canonical source registry: `10_literature/source_manifest.yaml`
- Idea selection: `20_ideas/`
- Experiment contract: `30_specs/`
- Engineering work: `40_code/repo/`
- Actual runs: `50_runs/`
- Analysis: `60_analysis/`
- Claim trace: `70_claims/`
- Manuscript draft: `80_manuscript/`
- Reviews and revisions: `90_reviews/`
- Final or rejected packages: `99_archive/`
