#!/usr/bin/env python3
"""Check whether a proposed spiral-fit window has real patch evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scroll_lab.fit_window import preflight_fit_window  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("patches", nargs="+", type=Path)
    parser.add_argument("--z0", type=float, required=True)
    parser.add_argument("--z1", type=float, required=True)
    parser.add_argument("--annotations", nargs="*", type=Path, default=[])
    parser.add_argument("--pixels", action="store_true")
    parser.add_argument("--max-pixels", type=int, default=20_000_000)
    args = parser.parse_args()
    result = preflight_fit_window(
        args.patches, z0=args.z0, z1=args.z1,
        annotation_paths=args.annotations,
        scan_pixels=args.pixels, max_pixels=args.max_pixels,
    )
    print(json.dumps({
        **{key: value for key, value in vars(result).items() if key != "patches"},
        "patches": [vars(status) for status in result.patches],
    }, indent=2, sort_keys=True))
    if result.false_negative_metadata_patches:
        return 2
    if args.pixels and result.actual_active_patches == 0 and result.unknown_patches == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
