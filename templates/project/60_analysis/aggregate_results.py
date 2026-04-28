#!/usr/bin/env python3
"""Project-level aggregation entrypoint.

Replace this with analysis code that reads only recorded metrics and run logs.
"""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNS = PROJECT_ROOT / "50_runs"


def main() -> int:
    metrics = sorted(RUNS.rglob("metrics.json")) if RUNS.exists() else []
    output = PROJECT_ROOT / "60_analysis" / "result_summary.json"
    output.write_text(
        json.dumps({"metrics_files": [str(path.relative_to(PROJECT_ROOT)) for path in metrics]}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

