# C2: Baseline Integration

You are integrating baselines for a fair comparison.

Read:

- `baseline_spec.yaml`
- `experiment_spec.yaml`
- `AGENTS.md`

Task:

Implement or connect the following baselines:

```text
[BASELINE_LIST]
```

Fairness requirements:

1. Same input preprocessing.
2. Same compiler flags.
3. Same hardware assumptions.
4. Same metrics.
5. Same logging format.
6. No baseline-specific shortcuts unless documented.

Add tests that verify:

- each baseline can run on the toy dataset
- `metrics.json` schema is identical across methods
- failed runs are logged

Run:

- `make test`
- one smoke run for each baseline

Report exact commands and outputs.

