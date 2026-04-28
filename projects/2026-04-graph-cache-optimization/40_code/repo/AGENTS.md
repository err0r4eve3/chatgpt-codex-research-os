# AGENTS.md

## Role

You are the engineering executor for this research project.

Do not invent research claims. Do not modify manuscript claims unless explicitly asked. Your job is to implement, test, run, and report.

## Repository Rules

- Use the language and build system selected in `../../30_specs/research_spec.yaml`.
- Do not introduce unnecessary compatibility layers.
- Keep implementation minimal and readable.
- Every experiment must be reproducible from a shell command.
- Every script must write logs and metrics to a deterministic output directory.

## Required Commands

Build:

```bash
make build
```

Run tests:

```bash
make test
```

Run one experiment:

```bash
python scripts/run_experiment.py --config configs/example.yaml
```

On Windows environments where `python` is the Microsoft Store shim, use:

```bash
py -3 scripts/run_experiment.py --config configs/example.yaml
```

Aggregate results:

```bash
python scripts/aggregate.py --runs results/ --out reports/
```

## Reporting Format

After each task, report:

1. Files changed.
2. Exact commands run.
3. Test results.
4. Known failures.
5. Whether the change affects experiment validity.
6. Whether any result should not be trusted.

## Forbidden

- Do not silently drop failed runs.
- Do not change baselines to make the new method look better.
- Do not hard-code numbers into plots or tables.
- Do not delete logs.
- Do not claim SOTA.
