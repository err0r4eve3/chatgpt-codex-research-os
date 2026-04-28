.PHONY: build test smoke aggregate clean

PYTHON ?= python

build:
	@echo "No build configured yet. Replace this target when implementation starts."

test:
	$(PYTHON) -m py_compile scripts/run_experiment.py scripts/aggregate.py

smoke:
	$(PYTHON) scripts/run_experiment.py --config configs/example.yaml

aggregate:
	$(PYTHON) scripts/aggregate.py --runs results --out reports

clean:
	@echo "No clean target configured yet."
