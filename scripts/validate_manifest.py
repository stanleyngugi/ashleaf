#!/usr/bin/env python3
"""Validate a benchmark manifest without downloading volume data."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from scroll_lab.manifest import load_manifest, validate_manifest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        issues = validate_manifest(load_manifest(args.manifest))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR manifest: {exc}")
        return 2
    if not issues:
        print(f"OK {args.manifest}")
        return 0
    for issue in issues:
        print(f"{issue.severity.upper()} {issue.code}: {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

