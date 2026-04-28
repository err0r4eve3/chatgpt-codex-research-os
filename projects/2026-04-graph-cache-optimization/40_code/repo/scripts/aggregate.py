#!/usr/bin/env python3
"""Aggregate recorded smoke or experiment metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate metrics.json files.")
    parser.add_argument("--runs", required=True, help="Run directory to scan.")
    parser.add_argument("--out", required=True, help="Output report directory.")
    return parser.parse_args()


def load_metric(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"metrics file is not a JSON object: {path}")
    return data


def main() -> int:
    args = parse_args()
    runs = Path(args.runs)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    metrics_files = sorted(runs.rglob("metrics.json")) if runs.exists() else []
    records = [load_metric(path) for path in metrics_files]
    summary = {
        "metrics_files": [str(path) for path in metrics_files],
        "count": len(records),
        "runs": [
            {
                "run_id": record.get("run_id"),
                "status": record.get("status"),
                "method": record.get("method"),
                "dataset": record.get("dataset"),
                "seed": record.get("seed"),
            }
            for record in records
        ],
    }

    output = out / "summary.json"
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

