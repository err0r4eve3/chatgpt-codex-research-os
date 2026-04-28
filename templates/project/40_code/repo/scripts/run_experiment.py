#!/usr/bin/env python3
"""Deterministic placeholder experiment runner.

This runner exists so a new project has an executable smoke path before real
research code is implemented. Replace the placeholder metrics during C1.
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a deterministic smoke experiment.")
    parser.add_argument("--config", required=True, help="Path to a YAML run config.")
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PyYAML is required. Install with: python -m pip install -r requirements-dev.txt") from exc

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"expected mapping config: {path}")
    return data


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def command_line() -> str:
    return " ".join([Path(sys.executable).name, *sys.argv])


def environment_text() -> str:
    lines = [
        f"python={sys.version.split()[0]}",
        f"platform={platform.platform()}",
        f"machine={platform.machine()}",
        f"processor={platform.processor()}",
        f"cwd={Path.cwd()}",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml(config_path)

    output_dir = Path(str(config.get("output_dir", "results/smoke")))
    output_dir.mkdir(parents=True, exist_ok=True)

    commit = git_commit()
    command = command_line()
    run_id = str(config.get("experiment_id", "smoke_001"))
    method = str(config.get("method", "method_under_test"))
    dataset = str(config.get("dataset", "toy"))
    seed = int(config.get("seed", 1))

    record = {
        "run_id": run_id,
        "status": "placeholder",
        "command": command,
        "git_commit": commit,
        "method": method,
        "dataset": dataset,
        "seed": seed,
        "metrics": {
            "placeholder_metric": 1.0,
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    (output_dir / "command.sh").write_text(command + "\n", encoding="utf-8", newline="\n")
    (output_dir / "stdout.log").write_text("placeholder smoke run completed\n", encoding="utf-8", newline="\n")
    (output_dir / "stderr.log").write_text("", encoding="utf-8", newline="\n")
    (output_dir / "run_config.yaml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    (output_dir / "git_commit.txt").write_text(commit + "\n", encoding="utf-8", newline="\n")
    (output_dir / "environment.txt").write_text(environment_text(), encoding="utf-8", newline="\n")
    (output_dir / "metrics.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")

    print(f"wrote {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

