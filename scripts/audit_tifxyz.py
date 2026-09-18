#!/usr/bin/env python3
"""Audit one or more TIFXYZ directories without loading image pixels."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scroll_lab.tifxyz import audit_tifxyz  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", nargs="+", type=Path)
    parser.add_argument("--pixels", action="store_true", help="scan valid vertices and check the bbox (requires numpy and tifffile)")
    parser.add_argument("--max-pixels", type=int, default=20_000_000)
    args = parser.parse_args()
    audits = [audit_tifxyz(path, scan_pixels=args.pixels, max_pixels=args.max_pixels) for path in args.directories]
    report = {
        "audits": [
            {
                "path": item.path,
                "width": item.width,
                "height": item.height,
                "ok": item.ok,
                "stats": item.stats,
                "issues": [
                    {"code": issue.code, "message": issue.message, "severity": issue.severity}
                    for issue in item.issues
                ],
            }
            for item in audits
        ]
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if all(item.ok for item in audits) else 1


if __name__ == "__main__":
    raise SystemExit(main())
