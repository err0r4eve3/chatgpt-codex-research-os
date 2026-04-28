#!/usr/bin/env python3
"""Placeholder smoke runner.

Replace this with the real experiment driver once C1 starts.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def read_simple_yaml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
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


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    config = read_simple_yaml(config_path)
    output_dir = Path(config.get("output_dir", "results/smoke_001"))
    output_dir.mkdir(parents=True, exist_ok=True)

    command = f"{Path(sys.executable).name} {' '.join(sys.argv)}"
    (output_dir / "command.sh").write_text(command + "\n", encoding="utf-8")
    (output_dir / "stdout.log").write_text("placeholder smoke run\n", encoding="utf-8")
    (output_dir / "stderr.log").write_text("", encoding="utf-8")
    (output_dir / "run_config.yaml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    (output_dir / "git_commit.txt").write_text(git_commit() + "\n", encoding="utf-8")
    (output_dir / "metrics.json").write_text(
        json.dumps(
            {
                "status": "placeholder",
                "method": config.get("method", "unknown"),
                "dataset": config.get("dataset", "unknown"),
                "seed": int(config.get("seed", "0")),
                "metrics": {},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

