#!/usr/bin/env python3
"""Create a research project from templates/project."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "project"
PROJECTS = ROOT / "projects"
PROJECT_ID_RE = re.compile(r"^\d{4}-\d{2}-[a-z0-9][a-z0-9-]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a Research OS project.")
    parser.add_argument("project_id", help="Format: YYYY-MM-short-topic")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing project directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_id = args.project_id.strip()

    if not PROJECT_ID_RE.match(project_id):
        print(
            "error: project_id must match YYYY-MM-short-topic, "
            "for example 2026-04-graph-cache-optimization",
            file=sys.stderr,
        )
        return 2

    if not TEMPLATE.exists():
        print(f"error: missing template directory: {TEMPLATE}", file=sys.stderr)
        return 2

    PROJECTS.mkdir(parents=True, exist_ok=True)
    destination = PROJECTS / project_id
    if destination.exists():
        if not args.force:
            print(f"error: project already exists: {destination}", file=sys.stderr)
            return 1
        shutil.rmtree(destination)

    shutil.copytree(TEMPLATE, destination)

    replacements = {
        "__PROJECT_ID__": project_id,
        "__PROJECT_TITLE__": project_id.replace("-", " ").title(),
    }
    for path in destination.rglob("*"):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if b"\0" in raw:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8", newline="\n")

    print(f"created {destination.relative_to(ROOT)}")
    print(f"next: python scripts/validate_artifacts.py --project {destination.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
