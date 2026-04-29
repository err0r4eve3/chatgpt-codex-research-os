# Validator Regression Cases

`tests/run_validator_cases.py` builds these cases at runtime by copying
`templates/project` into a temporary directory and applying one focused
mutation per case.

The cases prove that:

- a valid minimal project passes;
- supported claims cannot cite NotebookLM exports directly;
- verified NotebookLM exports must cite known sources;
- stale NotebookLM imports cannot support verified exports;
- supported claims must not point at missing evidence;
- manuscript `CLAIM:*` markers must reference supported claims;
- restricted NotebookLM imports require explicit human approval;
- run records must point at existing metrics files.

The fixtures are generated instead of checked in so the project template remains
the single source of truth for the valid baseline.
