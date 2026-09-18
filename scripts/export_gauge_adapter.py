#!/usr/bin/env python3
"""Solve a node graph and export a constraint-gauge JSON adapter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scroll_lab.gauge_adapter import export_gauge_adapter  # noqa: E402
from scroll_lab.winding import RelativeConstraint, solve_bfs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("graph", type=Path, help="JSON with nodes and constraints")
    parser.add_argument("--name", default="scroll-lab/bfs-baseline")
    parser.add_argument("--confidence-order", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.graph.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    solution = solve_bfs(
        [RelativeConstraint(**item) for item in raw["constraints"]],
        confidence_order=args.confidence_order,
    )
    adapter = export_gauge_adapter(solution, raw["nodes"], name=args.name)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(adapter, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(adapter['winding'])} nodes to {args.output}")
    print(f"contradictions in input graph: {len(solution.contradictions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
