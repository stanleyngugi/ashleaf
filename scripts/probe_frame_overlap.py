#!/usr/bin/env python3
"""Run a metadata/point-only coordinate-frame overlap probe."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scroll_lab.frame_probe import run_frame_probe, sha256_file  # noqa: E402
from scroll_lab.provenance import environment_fingerprint  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare declared/measured support only; this command never reads CT/Zarr chunks."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with args.manifest.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        parser.error("manifest root must be an object")
    try:
        result = run_frame_probe(raw, manifest_dir=args.manifest.resolve().parent)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    result["manifest"] = {
        "path": str(args.manifest.resolve()),
        "sha256": sha256_file(args.manifest),
    }
    result["environment"] = environment_fingerprint(ROOT)
    rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["all_expectations_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
