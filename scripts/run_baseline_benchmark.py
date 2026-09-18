#!/usr/bin/env python3
"""Run the complete dependency-free manifest plus winding baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from scroll_lab.benchmark import run_winding_benchmark  # noqa: E402
from scroll_lab.manifest import load_manifest  # noqa: E402
from scroll_lab.winding import RelativeConstraint  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("constraints", type=Path)
    parser.add_argument("--confidence-order", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    with args.constraints.open(encoding="utf-8") as handle:
        raw_constraints = json.load(handle)["constraints"]
    constraints = [RelativeConstraint(**item) for item in raw_constraints]
    report = run_winding_benchmark(
        load_manifest(args.manifest),
        constraints,
        confidence_order=args.confidence_order,
        repo_root=REPO_ROOT,
    )
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 1 if report["solution"]["contradiction_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

