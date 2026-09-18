#!/usr/bin/env python3
"""Audit local OME-Zarr v2 metadata without reading any array chunks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scroll_lab.zarr_meta import audit_omezarr_v2  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="+", type=Path)
    args = parser.parse_args()
    audits = [audit_omezarr_v2(root) for root in args.roots]
    print(json.dumps({"audits": [
        {
            "root": audit.root,
            "ok": audit.ok,
            "axes": audit.axes,
            "levels": [vars(level) for level in audit.levels],
            "issues": [vars(issue) for issue in audit.issues],
        }
        for audit in audits
    ]}, indent=2, sort_keys=True))
    return 0 if all(audit.ok for audit in audits) else 1


if __name__ == "__main__":
    raise SystemExit(main())
