# Runs

Each run directory must contain:

- `run_config.yaml`
- `command.sh`
- `stdout.log`
- `stderr.log`
- `metrics.json`
- `environment.txt`
- `git_commit.txt`
- `figures/` when applicable

Failed runs must be kept and labeled. Do not silently delete them.

`40_code/repo/results/` may contain local smoke outputs while implementation is being developed. Audited experiment records should be copied or written here once they are part of the research evidence.
