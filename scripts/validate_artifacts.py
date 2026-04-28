#!/usr/bin/env python3
"""Validate Research OS project structure and basic artifact contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
TEMPLATE = ROOT / "templates" / "project"

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
    "10_literature/notebooklm_manifest.yaml",
    "10_literature/notebooklm_exports/README.md",
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
    "40_code/repo/configs/example.yaml",
    "40_code/repo/scripts/run_experiment.py",
    "40_code/repo/scripts/aggregate.py",
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

BASELINE_REQUIRED = [
    "baselines",
    "fairness_checks",
]

NOTEBOOKLM_REQUIRED = [
    "notebook",
    "interface_policy",
    "source_registry",
    "export_policy",
    "sync_policy",
    "allowed_uses",
    "prohibited_uses",
]

STRUCTURED_SUFFIXES = {
    ".py",
    ".md",
    ".yaml",
    ".yml",
    ".json",
    ".tex",
}

STRUCTURED_NAMES = {
    ".gitignore",
    ".gitattributes",
    "Makefile",
    "requirements-dev.txt",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Research OS project artifacts.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--template", action="store_true", help="Validate templates/project.")
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


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def check_required_keys(name: str, data: Any, required: list[str]) -> list[str]:
    if not isinstance(data, dict):
        return [f"{name}: expected mapping"]
    return [f"{name}: missing key '{key}'" for key in required if key not in data]


def is_structured_file(path: Path) -> bool:
    return path.suffix in STRUCTURED_SUFFIXES or path.name in STRUCTURED_NAMES


def structured_files(root: Path) -> Iterable[Path]:
    ignored_parts = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    for path in root.rglob("*"):
        if not path.is_file() or any(part in ignored_parts for part in path.parts):
            continue
        if is_structured_file(path):
            yield path


def check_single_line_files(root: Path) -> list[str]:
    errors: list[str] = []
    for path in structured_files(root):
        raw = path.read_bytes()
        if not raw or b"\0" in raw:
            continue
        newline_count = raw.count(b"\n")
        if newline_count <= 1 and len(raw) > 200:
            errors.append(f"{display_path(path)}: suspicious single-line structured file")
    return errors


def check_json(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{display_path(path)}: invalid JSON: {exc}"]
    return []


def normalize_evidence_value(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from normalize_evidence_value(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from normalize_evidence_value(item)


def is_local_evidence_path(value: str) -> bool:
    stripped = value.strip()
    if not stripped or "://" in stripped or stripped.startswith("#"):
        return False
    if any(char in stripped for char in "\n\r"):
        return False
    return "/" in stripped or "\\" in stripped


def evidence_path_exists(project: Path, value: str) -> bool:
    path_text = value.split("#", 1)[0].strip().replace("\\", "/")
    if not path_text:
        return False
    return (project / path_text).exists()


def validate_claims(project: Path, claims_path: Path) -> list[str]:
    errors: list[str] = []
    claims = load_yaml(claims_path)
    errors.extend(check_required_keys(display_path(claims_path), claims, ["claims"]))

    if not isinstance(claims, dict) or not isinstance(claims.get("claims"), list):
        return errors

    for index, claim in enumerate(claims["claims"], start=1):
        label = claim.get("claim_id", index) if isinstance(claim, dict) else index
        if not isinstance(claim, dict):
            errors.append(f"{display_path(claims_path)}: claim {index} is not a mapping")
            continue

        status = claim.get("status")
        evidence = claim.get("evidence")
        if status == "supported" and not evidence:
            errors.append(f"{display_path(claims_path)}: supported claim {label} lacks evidence")
        if status in {"rejected", "contradicted"} and not claim.get("reason"):
            errors.append(f"{display_path(claims_path)}: {status} claim {label} lacks reason")

        for item in normalize_evidence_value(evidence):
            if is_local_evidence_path(item) and not evidence_path_exists(project, item):
                errors.append(f"{display_path(claims_path)}: claim {label} evidence path missing: {item}")

    return errors


def validate_notebooklm_manifest(project: Path, manifest_path: Path) -> list[str]:
    errors: list[str] = []
    manifest = load_yaml(manifest_path)
    errors.extend(check_required_keys(display_path(manifest_path), manifest, NOTEBOOKLM_REQUIRED))

    if not isinstance(manifest, dict):
        return errors

    notebook = manifest.get("notebook")
    if isinstance(notebook, dict):
        errors.extend(check_required_keys(f"{display_path(manifest_path)} notebook", notebook, ["id", "title", "cli_alias"]))
    else:
        errors.append(f"{display_path(manifest_path)}: notebook must be a mapping")

    export_policy = manifest.get("export_policy")
    if isinstance(export_policy, dict):
        directory = export_policy.get("directory")
        if isinstance(directory, str) and directory and not (project / directory).exists():
            errors.append(f"{display_path(manifest_path)}: export directory missing: {directory}")
    else:
        errors.append(f"{display_path(manifest_path)}: export_policy must be a mapping")

    source_registry = manifest.get("source_registry")
    if not isinstance(source_registry, list):
        errors.append(f"{display_path(manifest_path)}: source_registry must be a list")
    else:
        for index, source in enumerate(source_registry, start=1):
            if not isinstance(source, dict):
                errors.append(f"{display_path(manifest_path)}: source_registry item {index} is not a mapping")
                continue
            errors.extend(
                check_required_keys(
                    f"{display_path(manifest_path)} source_registry item {index}",
                    source,
                    ["source_id", "title", "source_type", "citation_status"],
                )
            )

    return errors


def validate_project(project: Path) -> list[str]:
    errors: list[str] = []

    if not project.exists():
        return [f"missing project directory: {project}"]

    for relative in REQUIRED_FILES:
        path = project / relative
        if not path.exists():
            errors.append(f"missing required file: {display_path(project / relative)}")

    errors.extend(check_single_line_files(project))
    errors.extend(check_json(project / "20_ideas" / "idea_pool.json"))

    spec_checks = [
        (project / "30_specs" / "research_spec.yaml", RESEARCH_REQUIRED),
        (project / "30_specs" / "experiment_spec.yaml", EXPERIMENT_REQUIRED),
        (project / "30_specs" / "baseline_spec.yaml", BASELINE_REQUIRED),
    ]
    for path, required in spec_checks:
        if not path.exists():
            continue
        try:
            data = load_yaml(path)
            errors.extend(check_required_keys(display_path(path), data, required))
        except Exception as exc:  # noqa: BLE001 - validation should report parse errors.
            errors.append(f"{display_path(path)}: {exc}")

    claims_path = project / "70_claims" / "claims.yaml"
    if claims_path.exists():
        try:
            errors.extend(validate_claims(project, claims_path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{display_path(claims_path)}: {exc}")

    notebooklm_path = project / "10_literature" / "notebooklm_manifest.yaml"
    if notebooklm_path.exists():
        try:
            errors.extend(validate_notebooklm_manifest(project, notebooklm_path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{display_path(notebooklm_path)}: {exc}")

    return errors


def project_paths(args: argparse.Namespace) -> list[Path]:
    if args.template:
        return [TEMPLATE]
    if args.all:
        if not PROJECTS.exists():
            return []
        return sorted(path for path in PROJECTS.iterdir() if path.is_dir())

    path = Path(args.project)
    if not path.is_absolute():
        path = ROOT / path
    return [path]


def main() -> int:
    args = parse_args()
    errors: list[str] = []

    for project in project_paths(args):
        project_errors = validate_project(project)
        if project_errors:
            errors.extend(project_errors)
        else:
            print(f"ok: {display_path(project)}")

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
