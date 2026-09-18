#!/usr/bin/env python3
"""Audit official same/relative/absolute winding point-collection JSONs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scroll_lab.pointcollections import audit_pointcollections, load_pointcollections  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--volume-shape-zyx", nargs=3, type=int)
    args = parser.parse_args()
    results = []
    failures = 0
    for path in args.files:
        try:
            audit = audit_pointcollections(load_pointcollections(path), volume_shape_zyx=args.volume_shape_zyx)
            results.append({"file": str(path), **{key: value for key, value in vars(audit).items() if key != "issues"},
                            "ok": audit.ok, "issues": [vars(issue) for issue in audit.issues]})
            failures += not audit.ok
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            results.append({"file": str(path), "ok": False, "issues": [{"code": "read_error", "message": str(exc), "severity": "error"}]})
            failures += 1
    print(json.dumps({"audits": results}, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
