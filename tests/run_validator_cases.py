#!/usr/bin/env python3
"""Regression tests for validate_artifacts.py artifact contracts."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "project"
VALIDATOR = ROOT / "scripts" / "validate_artifacts.py"


@dataclass(frozen=True)
class Case:
    name: str
    should_pass: bool
    expected: str
    mutate: Callable[[Path], None]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def noop(_: Path) -> None:
    return None


def fail_direct_notebooklm_claim(project: Path) -> None:
    write(
        project / "70_claims" / "claims.yaml",
        """claims:
  - claim_id: "C001"
    text: "NotebookLM export supports this claim."
    status: "supported"
    evidence:
      notes:
        - "10_literature/notebooklm_exports/export.md"
""",
    )
    write(project / "10_literature" / "notebooklm_exports" / "export.md", "NotebookLM summary.\n")


def fail_verified_export_without_sources(project: Path) -> None:
    write(project / "10_literature" / "notebooklm_exports" / "verified.md", "Verified export.\n")
    write(
        project / "10_literature" / "notebooklm_exports" / "export_index.yaml",
        """exports:
  - export_id: "NLM-EXP-001"
    notebook_id: "NB001"
    query: "What baselines are supported?"
    source_ids: []
    notebooklm_source_ids: []
    output_path: "10_literature/notebooklm_exports/verified.md"
    verification_status: "verified"
    allowed_for_evidence_map: true
    allowed_for_claims: false
""",
    )


def fail_stale_source_verified_export(project: Path) -> None:
    write(project / "10_literature" / "notebooklm_exports" / "verified.md", "Verified export.\n")
    write(
        project / "10_literature" / "notebooklm_manifest.yaml",
        """notebook:
  id: "NB001"
  title: "Case Notebook"
  profile: "default"
  cli_alias: "case"

interface_policy:
  preferred_for_cli: []
  preferred_for_mcp: []

imported_sources:
  - notebooklm_source_id: "NLM-SRC-001"
    source_id: "SRC-TBD"
    source_type: "other"
    import_type: "text"
    import_status: "stale"
    citation_status: "verified"
    rights_status: "permitted"
    export_paths: []

export_policy:
  directory: "10_literature/notebooklm_exports"
  index: "10_literature/notebooklm_exports/export_index.yaml"

sync_policy:
  record_every_import: true
  verify_before_claims: true

allowed_uses: []
prohibited_uses: []
""",
    )
    write(
        project / "10_literature" / "notebooklm_exports" / "export_index.yaml",
        """exports:
  - export_id: "NLM-EXP-001"
    notebook_id: "NB001"
    query: "What is established?"
    source_ids:
      - "SRC-TBD"
    notebooklm_source_ids:
      - "NLM-SRC-001"
    output_path: "10_literature/notebooklm_exports/verified.md"
    verification_status: "verified"
    allowed_for_evidence_map: true
    allowed_for_claims: false
""",
    )


def fail_missing_evidence_path(project: Path) -> None:
    write(
        project / "70_claims" / "claims.yaml",
        """claims:
  - claim_id: "C001"
    text: "Missing evidence path should fail."
    status: "supported"
    evidence:
      aggregate:
        - "60_analysis/missing_result.md"
""",
    )


def fail_unsupported_manuscript_claim(project: Path) -> None:
    write(project / "80_manuscript" / "abstract.md", "A claim appears here. [CLAIM:C999]\n")


def fail_restricted_source_imported_without_approval(project: Path) -> None:
    write(
        project / "10_literature" / "notebooklm_manifest.yaml",
        """notebook:
  id: "NB001"
  title: "Case Notebook"
  profile: "default"
  cli_alias: "case"

interface_policy:
  preferred_for_cli: []
  preferred_for_mcp: []

imported_sources:
  - notebooklm_source_id: "NLM-SRC-001"
    source_id: "SRC-TBD"
    source_type: "other"
    import_type: "text"
    import_status: "imported"
    citation_status: "unverified"
    rights_status: "restricted"
    export_paths: []

export_policy:
  directory: "10_literature/notebooklm_exports"
  index: "10_literature/notebooklm_exports/export_index.yaml"

sync_policy:
  record_every_import: true
  verify_before_claims: true

allowed_uses: []
prohibited_uses: []
""",
    )


def fail_run_record_missing_metrics(project: Path) -> None:
    run_dir = project / "50_runs" / "smoke"
    write(run_dir / "command.sh", "python scripts/run_experiment.py --config configs/example.yaml\n")
    write(run_dir / "run_config.yaml", "experiment_id: smoke\n")
    write(run_dir / "stdout.log", "ok\n")
    write(run_dir / "stderr.log", "")
    write(run_dir / "environment.txt", "python=3.11\n")
    write(
        run_dir / "run_record.yaml",
        """run_id: "smoke_001"
experiment_id: "smoke_001"
method: "placeholder"
dataset: "toy"
seed: 1
status: "completed"
command: "python scripts/run_experiment.py --config configs/example.yaml"
config_path: "run_config.yaml"
metrics_path: "metrics.json"
stdout_path: "stdout.log"
stderr_path: "stderr.log"
git_commit: "unknown"
environment_path: "environment.txt"
""",
    )


CASES = [
    Case("valid_minimal_project", True, "ok:", noop),
    Case("fail_direct_notebooklm_claim", False, "cites NotebookLM export directly", fail_direct_notebooklm_claim),
    Case("fail_verified_export_without_sources", False, "must list source_ids", fail_verified_export_without_sources),
    Case("fail_stale_source_verified_export", False, "depends on stale source_id", fail_stale_source_verified_export),
    Case("fail_missing_evidence_path", False, "evidence path missing", fail_missing_evidence_path),
    Case("fail_unsupported_manuscript_claim", False, "unsupported or unknown claim id", fail_unsupported_manuscript_claim),
    Case(
        "fail_restricted_source_imported_without_approval",
        False,
        "without upload_approved_by_human",
        fail_restricted_source_imported_without_approval,
    ),
    Case("fail_run_record_missing_metrics", False, "metrics_path missing", fail_run_record_missing_metrics),
]


def build_case(root: Path, case: Case) -> Path:
    project = root / case.name
    shutil.copytree(TEMPLATE, project)
    case.mutate(project)
    return project


def run_validator(project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--project", str(project)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="research-os-validator-") as raw_tmp:
        tmp = Path(raw_tmp)
        for case in CASES:
            project = build_case(tmp, case)
            result = run_validator(project)
            output = result.stdout + result.stderr

            passed = result.returncode == 0
            if passed != case.should_pass:
                failures.append(
                    f"{case.name}: expected pass={case.should_pass}, got returncode={result.returncode}\n{output}"
                )
                continue

            if case.expected not in output:
                failures.append(f"{case.name}: missing expected output fragment {case.expected!r}\n{output}")
                continue

            status = "PASS" if case.should_pass else "FAILS_AS_EXPECTED"
            print(f"ok: {case.name}: {status}")

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    print(f"ok: {len(CASES)} validator regression cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
