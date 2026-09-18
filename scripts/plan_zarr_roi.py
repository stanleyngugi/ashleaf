#!/usr/bin/env python3
"""Estimate chunk reads and memory for a proposed OME-Zarr region."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scroll_lab.zarr_meta import audit_omezarr_v2  # noqa: E402
from scroll_lab.zarr_roi import plan_roi  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("zarr_root", type=Path)
    parser.add_argument("--level", required=True)
    parser.add_argument("--start", nargs="+", required=True, type=int)
    parser.add_argument("--stop", nargs="+", required=True, type=int)
    parser.add_argument("--max-chunk-bytes", type=int)
    args = parser.parse_args()
    audit = audit_omezarr_v2(args.zarr_root)
    if not audit.ok:
        parser.error("Zarr metadata audit failed; run audit_zarr_metadata.py first")
    level = next((item for item in audit.levels if item.path == args.level), None)
    if level is None:
        parser.error(f"unknown level {args.level!r}")
    try:
        plan = plan_roi(level, args.start, args.stop)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps({"axes": audit.axes, **vars(plan)}, indent=2, sort_keys=True))
    if args.max_chunk_bytes is not None and plan.estimated_chunk_bytes_upper_bound is not None:
        return 1 if plan.estimated_chunk_bytes_upper_bound > args.max_chunk_bytes else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
