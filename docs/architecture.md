# Architecture

The repository implements a five-layer Human-in-the-loop Research OS.

## Layers

```text
Human PI layer
  Chooses direction, accepts or rejects ideas, controls compute use, owns final authorship.

Pro Research Controller layer
  Performs literature synthesis, problem framing, idea generation, experiment design,
  adversarial review, and manuscript organization.

Codex Engineering Executor layer
  Implements code, integrates baselines, writes scripts and tests, runs commands,
  extracts results, and cleans repositories.

Evidence / Trace layer
  Stores literature evidence, experiment logs, seeds, configs, metrics, figures,
  statistical tests, and claim-to-evidence mappings.

Manuscript Compiler layer
  Compiles draft sections, appendix material, reproducibility notes, and AI disclosure
  from approved evidence.
```

## Design Constraint

Separate writing ability from research truth.

Correct order:

```text
evidence -> claim -> paper
```

Incorrect order:

```text
paper -> retrofitted evidence
```

## Plane Model

```text
Pro model = research control plane
Codex = engineering execution plane
experiment logs / metrics / citations / claim trace = evidence plane
paper = compiled artifact from evidence
```

## Traceability Requirement

Every paper conclusion must trace to:

- experiment command
- stdout and stderr logs
- run config
- metrics file
- environment record
- code commit
- dataset or benchmark version
- statistical or repeated-run evidence
- relevant literature evidence

