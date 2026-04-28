#!/usr/bin/env python3
"""Validate Research OS project structure and basic artifact contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"

REQUIRED_FILES = [
    "README.md",
    "STATUS.md",
    "00_intake/problem_brief.md",
    "00_intake/constraints.md",
    "00_intake/human_decisions.md",
    "10_literature/search_queries.md",
    "10_literature/paper_table.csv",
    "10_literature/evidence_map.md",
    "10_literature/bibtex.bib",
    "20_ideas/idea_pool.json",
    "20_ideas/idea_scores.md",
    "20_ideas/rejected_ideas.md",
    "20_ideas/selected_idea.md",
    "30_specs/research_spec.yaml",
    "30_specs/experiment_spec.yaml",
    "30_specs/baseline_spec.yaml",
    "30_specs/risk_register.md",
    "40_code/repo/AGENTS.md",
    "40_code/repo/Makefile",
    "50_runs/README.md",
    "60_analysis/aggregate_results.py",
    "60_analysis/statistical_tests.md",
    "60_analysis/result_summary.md",
    "60_analysis/failure_analysis.md",
    "70_claims/claims.yaml",
    "70_claims/claim_evidence_matrix.md",
    "70_claims/unsupported_claims.md",
    "80_manuscript/paper.tex",
    "80_manuscript/abstract.md",
    "80_manuscript/intro.md",
    "80_manuscript/related_work.md",
    "80_manuscript/method.md",
    "80_manuscript/experiments.md",
    "80_manuscript/limitations.md",
    "80_manuscript/reproducibility.md",
    "80_manuscript/ai_disclosure.md",
    "90_reviews/internal_review_round_1.md",
    "90_reviews/adversarial_review.md",
    "90_reviews/rebuttal_plan.md",
    "90_reviews/revision_log.md",
    "99_archive/README.md",
]

RESEARCH_REQUIRED = [
    "project_id",
    "field",
    "target_venue_type",
    "research_question",
    "hypothesis",
    "contribution_type",
    "non_goals",
    "success_criteria",
    "human_owner_decisions",
]

EXPERIMENT_REQUIRED = [
    "experiment_id",
    "datasets",
    "baselines",
    "method_under_test",
    "metrics",
    "controls",
    "run_matrix",
    "acceptance_checks",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Research OS project artifacts.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--project", help="Project directory to validate.")
    group.add_argument("--all", action="store_true", help="Validate all projects.")
    return parser.parse_args()


def load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "PyYAML is required for YAML validation. Install with: python -m pip install PyYAML"
        ) from exc

    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def check_required_keys(name: str, data: Any, required: list[str]) -> list[str]:
    if not isinstance(data, dict):
        return [f"{name}: expected mapping"]
    return [f"{name}: missing key '{key}'" for key in required if key not in data]


def validate_project(project: Path) -> list[str]:
    errors: list[str] = []

    if not project.exists():
        return [f"missing project directory: {project}"]

    for relative in REQUIRED_FILES:
        path = project / relative
        if not path.exists():
            errors.append(f"missing required file: {project.name}/{relative}")

    idea_pool = project / "20_ideas" / "idea_pool.json"
    if idea_pool.exists():
        try:
            json.loads(idea_pool.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{project.name}/20_ideas/idea_pool.json: invalid JSON: {exc}")

    try:
        research_spec = load_yaml(project / "30_specs" / "research_spec.yaml")
        errors.extend(check_required_keys("research_spec.yaml", research_spec, RESEARCH_REQUIRED))
    except Exception as exc:  # noqa: BLE001 - validation script should report all parse errors.
        errors.append(f"{project.name}/30_specs/research_spec.yaml: {exc}")

    try:
        experiment_spec = load_yaml(project / "30_specs" / "experiment_spec.yaml")
        errors.extend(check_required_keys("experiment_spec.yaml", experiment_spec, EXPERIMENT_REQUIRED))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{project.name}/30_specs/experiment_spec.yaml: {exc}")

    try:
        claims = load_yaml(project / "70_claims" / "claims.yaml")
        errors.extend(check_required_keys("claims.yaml", claims, ["claims"]))
        if isinstance(claims, dict) and isinstance(claims.get("claims"), list):
            for index, claim in enumerate(claims["claims"], start=1):
                if not isinstance(claim, dict):
                    errors.append(f"claims.yaml: claim {index} is not a mapping")
                    continue
                status = claim.get("status")
                if status == "supported" and not claim.get("evidence"):
                    errors.append(f"claims.yaml: supported claim {claim.get('claim_id', index)} lacks evidence")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{project.name}/70_claims/claims.yaml: {exc}")

    return errors


def project_paths(args: argparse.Namespace) -> list[Path]:
    if args.all:
        return sorted(path for path in PROJECTS.iterdir() if path.is_dir())

    path = Path(args.project)
    if not path.is_absolute():
        path = ROOT / path
    return [path]


def main() -> int:
    args = parse_args()
    errors: list[str] = []

    for project in project_paths(args):
        if project.name == ".git":
            continue
        project_errors = validate_project(project)
        if project_errors:
            errors.extend(project_errors)
        else:
            print(f"ok: {project.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

