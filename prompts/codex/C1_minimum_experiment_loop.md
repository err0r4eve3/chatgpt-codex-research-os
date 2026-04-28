# C1: Minimum Experiment Loop

You are the engineering executor for this research project.

Read:

- `AGENTS.md`
- `research_spec.yaml`
- `experiment_spec.yaml`

Task:

Implement the minimum experimental loop for `[METHOD_NAME]`.

Requirements:

1. Do not change the research claim.
2. Do not modify baselines except where explicitly required.
3. Add tests for the new implementation.
4. Add one runnable config under `configs/`.
5. Add or update `scripts/run_experiment.py` if needed.
6. Ensure every run writes:
   - `metrics.json`
   - `stdout.log`
   - `stderr.log`
   - `run_config.yaml`
   - `git_commit.txt`
7. Run the test suite.
8. Run one smoke experiment.

Report:

- files changed
- commands run
- test results
- smoke experiment result
- known failures
- whether the implementation is ready for full experiments

