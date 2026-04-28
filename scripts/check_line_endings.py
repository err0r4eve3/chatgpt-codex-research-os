#!/usr/bin/env python3
"""Check structured repository files for LF line endings."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

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

IGNORED_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate LF line endings in structured files.")
    parser.add_argument(
        "paths",
        nargs="*",
        default=[str(ROOT)],
        help="Files or directories to check. Defaults to the repository root.",
    )
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def is_structured_file(path: Path) -> bool:
    return path.suffix in STRUCTURED_SUFFIXES or path.name in STRUCTURED_NAMES


def iter_structured_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.is_absolute():
            path = ROOT / path
        if path.is_file():
            if is_structured_file(path):
                files.append(path)
            continue
        if not path.exists():
            raise FileNotFoundError(path)
        for candidate in path.rglob("*"):
            if not candidate.is_file() or any(part in IGNORED_PARTS for part in candidate.parts):
                continue
            if is_structured_file(candidate):
                files.append(candidate)
    return sorted(set(files))


def check_file(path: Path) -> list[str]:
    raw = path.read_bytes()
    if not raw or b"\0" in raw:
        return []

    errors: list[str] = []
    if b"\r" in raw:
        errors.append(f"{display_path(path)}: contains CR bytes; expected LF-only line endings")

    newline_count = raw.count(b"\n")
    if len(raw) > 200 and newline_count <= 1:
        errors.append(f"{display_path(path)}: suspicious single-line structured file")

    return errors


def main() -> int:
    args = parse_args()
    errors: list[str] = []

    try:
        files = iter_structured_files(args.paths)
    except FileNotFoundError as exc:
        print(f"error: missing path: {display_path(Path(str(exc)))}", file=sys.stderr)
        return 2

    for path in files:
        errors.extend(check_file(path))

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"ok: checked {len(files)} structured files for LF line endings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
