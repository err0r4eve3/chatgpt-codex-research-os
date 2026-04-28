# C3: Experiment Matrix

You are running the experiment matrix.

Read:

- `experiment_spec.yaml`
- `configs/`

Task:

Run the full experiment matrix defined in `experiment_spec.yaml`.

Requirements:

1. Do not skip failed runs.
2. Save each run under `results/{experiment_id}/{method}/{dataset}/{seed}/`.
3. Save `command.sh`, `stdout.log`, `stderr.log`, `metrics.json`, `run_config.yaml`, `git_commit.txt`.
4. After all runs, execute `aggregate_results.py`.
5. Generate tables and figures from metrics only.
6. Report failed runs separately.

Do not interpret results beyond what the metrics show.
Do not write paper claims.

Final report:

- completed runs
- failed runs
- aggregate metrics
- generated figures/tables
- commands executed

