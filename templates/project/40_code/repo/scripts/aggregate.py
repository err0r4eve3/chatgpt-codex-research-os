#!/usr/bin/env python3
"""Placeholder result aggregator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runs = Path(args.runs)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    metrics = sorted(runs.rglob("metrics.json")) if runs.exists() else []
    summary = {"metrics_files": [str(path) for path in metrics], "count": len(metrics)}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

