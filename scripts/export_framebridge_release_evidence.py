#!/usr/bin/env python3
"""Validate and export compact FrameBridge result JSON for a public clone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def export(source: Path, destination: Path, *, experiment: str) -> dict[str, object]:
    raw = source.read_bytes()
    parsed = json.loads(raw)
    if parsed.get("experiment") != experiment:
        raise ValueError(f"{source}: expected experiment {experiment}")
    if experiment == "FB07" and not parsed.get("not_new_heldout_evidence"):
        raise ValueError("FB07 evidence-class guard failed")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    return {
        "experiment": experiment,
        "path": str(destination),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fb06", type=Path, required=True)
    parser.add_argument("--fb07", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    records = [
        export(args.fb06, args.output_dir / "framebridge_fb06_summary.json", experiment="FB06"),
        export(args.fb07, args.output_dir / "framebridge_fb07_loso.json", experiment="FB07"),
    ]
    print(json.dumps({"exports": records}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
