#!/usr/bin/env python3
"""Validate Research OS project structure and basic artifact contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - reported as a validation error.
    Draft202012Validator = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
TEMPLATE = ROOT / "templates" / "project"
SCHEMAS = ROOT / "schemas"

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
    "10_literature/source_manifest.yaml",
    "10_literature/notebooklm_manifest.yaml",
    "10_literature/notebooklm_exports/README.md",
    "10_literature/notebooklm_exports/export_index.yaml",
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
    "imported_sources",
    "export_policy",
    "sync_policy",
    "allowed_uses",
    "prohibited_uses",
]

SOURCE_MANIFEST_REQUIRED = [
    "sources",
]

EXPORT_INDEX_REQUIRED = [
    "exports",
]

SOURCE_TYPE_VALUES = {
    "paper",
    "official_repo",
    "benchmark_doc",
    "dataset_doc",
    "official_doc",
    "web_url",
    "youtube",
    "google_drive",
    "local_file",
    "human_note",
    "other",
}

CITATION_STATUS_VALUES = {
    "unverified",
    "verified",
    "rejected",
}

RIGHTS_STATUS_VALUES = {
    "open_access",
    "owned",
    "licensed",
    "unknown",
    "permitted",
    "restricted",
    "public",
    "internal_only",
    "do_not_upload",
}

IMPORT_TYPE_VALUES = {
    "url",
    "drive",
    "text",
    "file",
    "youtube",
    "audio",
    "other",
}

IMPORT_STATUS_VALUES = {
    "pending",
    "imported",
    "stale",
    "removed",
    "failed",
}

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

DATA_SUFFIXES = {".yaml", ".yml", ".json"}

PROJECT_SCHEMA_FILES = {
    "10_literature/source_manifest.yaml": "source_manifest.schema.json",
    "10_literature/notebooklm_manifest.yaml": "notebooklm_manifest.schema.json",
    "10_literature/notebooklm_exports/export_index.yaml": "notebooklm_export_index.schema.json",
    "30_specs/research_spec.yaml": "research_spec.schema.json",
    "30_specs/experiment_spec.yaml": "experiment_spec.schema.json",
    "30_specs/baseline_spec.yaml": "baseline_spec.schema.json",
    "70_claims/claims.yaml": "claims.schema.json",
}

RUN_RECORD_SCHEMA = "run_record.schema.json"
RISKY_NOTEBOOKLM_RIGHTS = {"restricted", "internal_only", "do_not_upload"}
PUBLICATION_RISK_RIGHTS = {"unknown", "restricted", "internal_only", "do_not_upload"}
CLAIM_ID_RE = re.compile(r"CLAIM:([A-Za-z0-9_.:-]+)")


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


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def check_required_keys(name: str, data: Any, required: list[str]) -> list[str]:
    if not isinstance(data, dict):
        return [f"{name}: expected mapping"]
    return [f"{name}: missing key '{key}'" for key in required if key not in data]


def validate_schema_files() -> list[str]:
    errors: list[str] = []
    if Draft202012Validator is None:
        return ["jsonschema is required. Install with: python -m pip install -r requirements-dev.txt"]

    for schema_path in sorted(SCHEMAS.glob("*.schema.json")):
        try:
            schema = load_json(schema_path)
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # noqa: BLE001 - validation should report schema errors.
            errors.append(f"{display_path(schema_path)}: invalid schema: {exc}")
    return errors


def load_artifact(path: Path) -> Any:
    if path.suffix in {".yaml", ".yml"}:
        return load_yaml(path)
    if path.suffix == ".json":
        return load_json(path)
    raise ValueError(f"unsupported schema-validated artifact type: {path.suffix}")


def validate_instance_with_schema(instance_path: Path, schema_name: str) -> list[str]:
    if Draft202012Validator is None:
        return ["jsonschema is required. Install with: python -m pip install -r requirements-dev.txt"]

    schema_path = SCHEMAS / schema_name
    if not schema_path.exists():
        return [f"{display_path(instance_path)}: missing schema: {display_path(schema_path)}"]

    try:
        schema = load_json(schema_path)
        data = load_artifact(instance_path)
        validator = Draft202012Validator(schema)
        validation_errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    except Exception as exc:  # noqa: BLE001 - validation should report parse errors.
        return [f"{display_path(instance_path)}: schema validation failed: {exc}"]

    errors: list[str] = []
    for error in validation_errors:
        location = "/".join(str(part) for part in error.path)
        suffix = f" at {location}" if location else ""
        errors.append(f"{display_path(instance_path)}: schema validation failed{suffix}: {error.message}")
    return errors


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
        if b"\r" in raw:
            errors.append(f"{display_path(path)}: contains CR bytes; expected LF-only line endings")
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


def validate_structured_data_files(root: Path) -> list[str]:
    errors: list[str] = []
    ignored_parts = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in ignored_parts for part in path.parts):
            continue
        if path.suffix not in DATA_SUFFIXES:
            continue
        try:
            if path.suffix == ".json":
                load_json(path)
            else:
                load_yaml(path)
        except Exception as exc:  # noqa: BLE001 - validation should report parse errors.
            errors.append(f"{display_path(path)}: structured data parse failed: {exc}")
    return errors


def validate_gitattributes() -> list[str]:
    path = ROOT / ".gitattributes"
    required_lines = {
        "* text=auto eol=lf",
        "*.py text eol=lf",
        "*.md text eol=lf",
        "*.yaml text eol=lf",
        "*.yml text eol=lf",
        "*.json text eol=lf",
        "*.tex text eol=lf",
        "Makefile text eol=lf",
    }
    if not path.exists():
        return ["missing .gitattributes"]
    lines = {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}
    return [f".gitattributes: missing line: {line}" for line in sorted(required_lines - lines)]


def validate_github_actions() -> list[str]:
    path = ROOT / ".github" / "workflows" / "validate.yml"
    required_fragments = [
        "python -m py_compile",
        "python tests/run_validator_cases.py",
        "python scripts/check_line_endings.py",
        "python scripts/validate_artifacts.py --template",
        "python scripts/new_project.py 2026-04-smoke-test --force",
        "python scripts/validate_artifacts.py --project projects/2026-04-smoke-test",
        "make test",
        "make smoke",
        "make aggregate",
        "python scripts/validate_artifacts.py --all",
    ]
    if not path.exists():
        return ["missing .github/workflows/validate.yml"]
    text = path.read_text(encoding="utf-8")
    return [f"{display_path(path)}: missing workflow command fragment: {fragment}" for fragment in required_fragments if fragment not in text]


def validate_repository_files() -> list[str]:
    errors: list[str] = []
    errors.extend(check_single_line_files(ROOT))
    errors.extend(validate_structured_data_files(ROOT))
    errors.extend(validate_gitattributes())
    errors.extend(validate_github_actions())
    errors.extend(validate_schema_files())
    return errors


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


def load_source_registry(project: Path) -> dict[str, dict[str, Any]]:
    source_manifest = project / "10_literature" / "source_manifest.yaml"
    if not source_manifest.exists():
        return {}
    data = load_yaml(source_manifest)
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        return {}
    return {
        str(source.get("source_id")): source
        for source in data["sources"]
        if isinstance(source, dict) and source.get("source_id")
    }


def load_source_ids(project: Path) -> set[str]:
    return set(load_source_registry(project))


def load_notebooklm_imports(project: Path) -> dict[str, list[dict[str, Any]]]:
    manifest_path = project / "10_literature" / "notebooklm_manifest.yaml"
    if not manifest_path.exists():
        return {}
    manifest = load_yaml(manifest_path)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("imported_sources"), list):
        return {}

    imports: dict[str, list[dict[str, Any]]] = {}
    for source in manifest["imported_sources"]:
        if not isinstance(source, dict) or not source.get("source_id"):
            continue
        imports.setdefault(str(source["source_id"]), []).append(source)
    return imports


def check_enum(path: Path, label: str, value: Any, allowed: set[str]) -> list[str]:
    if value not in allowed:
        return [f"{display_path(path)}: {label} has invalid value '{value}'"]
    return []


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
            normalized = item.replace("\\", "/")
            if status == "supported" and "10_literature/notebooklm_exports/" in normalized:
                errors.append(
                    f"{display_path(claims_path)}: supported claim {label} cites NotebookLM export directly: {item}"
                )
            if status == "supported" and normalized.lower() in {
                "notebooklm answer",
                "notebooklm generated summary",
                "notebooklm summary",
            }:
                errors.append(f"{display_path(claims_path)}: supported claim {label} cites NotebookLM output as final evidence")
            if is_local_evidence_path(item) and not evidence_path_exists(project, item):
                errors.append(f"{display_path(claims_path)}: claim {label} evidence path missing: {item}")

    return errors


def validate_source_manifest(project: Path, source_path: Path) -> list[str]:
    errors: list[str] = []
    manifest = load_yaml(source_path)
    errors.extend(check_required_keys(display_path(source_path), manifest, SOURCE_MANIFEST_REQUIRED))

    if not isinstance(manifest, dict):
        return errors

    sources = manifest.get("sources")
    if not isinstance(sources, list):
        return [*errors, f"{display_path(source_path)}: sources must be a list"]

    seen: set[str] = set()
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            errors.append(f"{display_path(source_path)}: source {index} is not a mapping")
            continue
        label = f"{display_path(source_path)} source {index}"
        errors.extend(
            check_required_keys(
                label,
                source,
                ["source_id", "title", "source_type", "locator", "rights_status", "citation_status"],
            )
        )
        source_id = str(source.get("source_id", ""))
        if source_id in seen:
            errors.append(f"{display_path(source_path)}: duplicate source_id '{source_id}'")
        seen.add(source_id)
        errors.extend(check_enum(source_path, f"{source_id}.source_type", source.get("source_type"), SOURCE_TYPE_VALUES))
        errors.extend(
            check_enum(
                source_path,
                f"{source_id}.citation_status",
                source.get("citation_status"),
                CITATION_STATUS_VALUES,
            )
        )
        errors.extend(
            check_enum(source_path, f"{source_id}.rights_status", source.get("rights_status"), RIGHTS_STATUS_VALUES)
        )
        if source.get("source_of_truth") is True and source.get("citation_status") == "rejected":
            errors.append(f"{display_path(source_path)}: source_of_truth source {source_id} has rejected citation_status")
        if source.get("publication_critical") is True and source.get("rights_status") in PUBLICATION_RISK_RIGHTS:
            if source.get("publication_approved_by_human") is not True:
                errors.append(
                    f"{display_path(source_path)}: publication-critical source {source_id} has unsafe rights_status "
                    "without publication_approved_by_human: true"
                )

    return errors


def validate_notebooklm_manifest(project: Path, manifest_path: Path) -> list[str]:
    errors: list[str] = []
    manifest = load_yaml(manifest_path)
    errors.extend(check_required_keys(display_path(manifest_path), manifest, NOTEBOOKLM_REQUIRED))
    source_registry = load_source_registry(project)
    source_ids = set(source_registry)

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

    imported_sources = manifest.get("imported_sources")
    if not isinstance(imported_sources, list):
        errors.append(f"{display_path(manifest_path)}: imported_sources must be a list")
    else:
        for index, source in enumerate(imported_sources, start=1):
            if not isinstance(source, dict):
                errors.append(f"{display_path(manifest_path)}: imported_sources item {index} is not a mapping")
                continue
            source_id = str(source.get("source_id", ""))
            errors.extend(
                check_required_keys(
                    f"{display_path(manifest_path)} imported_sources item {index}",
                    source,
                    [
                        "notebooklm_source_id",
                        "source_id",
                        "source_type",
                        "import_type",
                        "import_status",
                        "citation_status",
                        "rights_status",
                    ],
                )
            )
            if source_ids and source_id not in source_ids:
                errors.append(f"{display_path(manifest_path)}: imported source_id not in source_manifest.yaml: {source_id}")
            errors.extend(
                check_enum(manifest_path, f"{source_id}.source_type", source.get("source_type"), SOURCE_TYPE_VALUES)
            )
            errors.extend(
                check_enum(manifest_path, f"{source_id}.import_type", source.get("import_type"), IMPORT_TYPE_VALUES)
            )
            errors.extend(
                check_enum(manifest_path, f"{source_id}.import_status", source.get("import_status"), IMPORT_STATUS_VALUES)
            )
            errors.extend(
                check_enum(
                    manifest_path,
                    f"{source_id}.citation_status",
                    source.get("citation_status"),
                    CITATION_STATUS_VALUES,
                )
            )
            errors.extend(
                check_enum(manifest_path, f"{source_id}.rights_status", source.get("rights_status"), RIGHTS_STATUS_VALUES)
            )
            if source.get("import_status") == "imported" and source.get("rights_status") in RISKY_NOTEBOOKLM_RIGHTS:
                if source.get("upload_approved_by_human") is not True:
                    errors.append(
                        f"{display_path(manifest_path)}: imported source {source_id} has restricted rights "
                        "without upload_approved_by_human: true"
                    )
            canonical = source_registry.get(source_id)
            if canonical:
                if canonical.get("citation_status") == "rejected" and source.get("citation_status") == "verified":
                    errors.append(
                        f"{display_path(manifest_path)}: imported source {source_id} is verified but canonical source is rejected"
                    )
                if canonical.get("rights_status") == "do_not_upload" and source.get("import_status") in {"imported", "stale"}:
                    if source.get("upload_approved_by_human") is not True:
                        errors.append(
                            f"{display_path(manifest_path)}: source {source_id} is do_not_upload but appears in NotebookLM imports"
                        )

    return errors


def validate_notebooklm_export_index(project: Path, index_path: Path) -> list[str]:
    errors: list[str] = []
    index = load_yaml(index_path)
    errors.extend(check_required_keys(display_path(index_path), index, EXPORT_INDEX_REQUIRED))
    source_registry = load_source_registry(project)
    source_ids = set(source_registry)
    imported_sources = load_notebooklm_imports(project)

    if not isinstance(index, dict):
        return errors

    exports = index.get("exports")
    if not isinstance(exports, list):
        return [*errors, f"{display_path(index_path)}: exports must be a list"]

    for item_index, export in enumerate(exports, start=1):
        if not isinstance(export, dict):
            errors.append(f"{display_path(index_path)}: export {item_index} is not a mapping")
            continue
        export_id = str(export.get("export_id", item_index))
        errors.extend(
            check_required_keys(
                f"{display_path(index_path)} export {export_id}",
                export,
                [
                    "export_id",
                    "notebook_id",
                    "query",
                    "source_ids",
                    "output_path",
                    "verification_status",
                    "allowed_for_evidence_map",
                    "allowed_for_claims",
                ],
            )
        )
        errors.extend(
            check_enum(
                index_path,
                f"{export_id}.verification_status",
                export.get("verification_status"),
                CITATION_STATUS_VALUES,
            )
        )
        if export.get("allowed_for_claims") is True:
            errors.append(f"{display_path(index_path)}: export {export_id} must not be allowed_for_claims")
        verification_status = export.get("verification_status")
        if export.get("allowed_for_evidence_map") is True and verification_status != "verified":
            errors.append(f"{display_path(index_path)}: export {export_id} cannot be allowed_for_evidence_map unless verified")
        listed_source_ids = export.get("source_ids")
        if not isinstance(listed_source_ids, list):
            errors.append(f"{display_path(index_path)}: export {export_id} source_ids must be a list")
        else:
            if verification_status == "verified" and not listed_source_ids:
                errors.append(f"{display_path(index_path)}: verified export {export_id} must list source_ids")
            for source_id in listed_source_ids:
                if source_ids and source_id not in source_ids:
                    errors.append(f"{display_path(index_path)}: export {export_id} unknown source_id: {source_id}")
                    continue
                canonical = source_registry.get(str(source_id))
                if canonical:
                    if canonical.get("citation_status") == "rejected":
                        errors.append(f"{display_path(index_path)}: export {export_id} cites rejected source_id: {source_id}")
                    if verification_status == "verified" and canonical.get("rights_status") == "do_not_upload":
                        errors.append(f"{display_path(index_path)}: verified export {export_id} cites do_not_upload source_id: {source_id}")
                    if export.get("publication_critical") is True and canonical.get("rights_status") in PUBLICATION_RISK_RIGHTS:
                        if canonical.get("publication_approved_by_human") is not True:
                            errors.append(
                                f"{display_path(index_path)}: publication-critical export {export_id} cites source {source_id} "
                                "with unsafe rights_status"
                            )
                if verification_status == "verified":
                    stale_imports = [
                        item
                        for item in imported_sources.get(str(source_id), [])
                        if item.get("import_status") == "stale"
                    ]
                    if stale_imports:
                        errors.append(f"{display_path(index_path)}: verified export {export_id} depends on stale source_id: {source_id}")
        output_path = export.get("output_path")
        if verification_status == "verified" and output_path in {"", "TBD", None}:
            errors.append(f"{display_path(index_path)}: verified export {export_id} must have an output_path")
        if isinstance(output_path, str) and output_path not in {"", "TBD"} and not (project / output_path).exists():
            errors.append(f"{display_path(index_path)}: export {export_id} output_path missing: {output_path}")

    return errors


def validate_run_records(project: Path) -> list[str]:
    errors: list[str] = []
    search_roots = [
        project / "50_runs",
        project / "40_code" / "repo" / "results",
    ]

    for root in search_roots:
        if not root.exists():
            continue
        for record_path in sorted(root.rglob("run_record.yaml")):
            errors.extend(validate_instance_with_schema(record_path, RUN_RECORD_SCHEMA))
            try:
                record = load_yaml(record_path)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{display_path(record_path)}: {exc}")
                continue
            if not isinstance(record, dict):
                errors.append(f"{display_path(record_path)}: expected mapping")
                continue

            for key in ["config_path", "metrics_path", "stdout_path", "stderr_path", "environment_path"]:
                value = record.get(key)
                if isinstance(value, str) and value and not (record_path.parent / value).exists():
                    errors.append(f"{display_path(record_path)}: {key} missing: {value}")

    return errors


def supported_claim_ids(project: Path) -> set[str]:
    claims_path = project / "70_claims" / "claims.yaml"
    if not claims_path.exists():
        return set()
    claims = load_yaml(claims_path)
    if not isinstance(claims, dict) or not isinstance(claims.get("claims"), list):
        return set()
    return {
        str(claim.get("claim_id"))
        for claim in claims["claims"]
        if isinstance(claim, dict) and claim.get("claim_id") and claim.get("status") == "supported"
    }


def check_manuscript_claim_ids(project: Path) -> list[str]:
    manuscript = project / "80_manuscript"
    if not manuscript.exists():
        return []

    valid_claims = supported_claim_ids(project)
    errors: list[str] = []
    for path in sorted(manuscript.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".tex"}:
            continue
        text = path.read_text(encoding="utf-8")
        for match in CLAIM_ID_RE.finditer(text):
            claim_id = match.group(1)
            if claim_id not in valid_claims:
                errors.append(f"{display_path(path)}: manuscript references unsupported or unknown claim id: {claim_id}")
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

    for relative, schema_name in PROJECT_SCHEMA_FILES.items():
        path = project / relative
        if path.exists():
            errors.extend(validate_instance_with_schema(path, schema_name))

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

    source_manifest_path = project / "10_literature" / "source_manifest.yaml"
    if source_manifest_path.exists():
        try:
            errors.extend(validate_source_manifest(project, source_manifest_path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{display_path(source_manifest_path)}: {exc}")

    notebooklm_path = project / "10_literature" / "notebooklm_manifest.yaml"
    if notebooklm_path.exists():
        try:
            errors.extend(validate_notebooklm_manifest(project, notebooklm_path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{display_path(notebooklm_path)}: {exc}")

    export_index_path = project / "10_literature" / "notebooklm_exports" / "export_index.yaml"
    if export_index_path.exists():
        try:
            errors.extend(validate_notebooklm_export_index(project, export_index_path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{display_path(export_index_path)}: {exc}")

    errors.extend(validate_run_records(project))
    errors.extend(check_manuscript_claim_ids(project))

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
    errors: list[str] = validate_repository_files()

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
