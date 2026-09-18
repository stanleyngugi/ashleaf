#!/usr/bin/env python3
"""Solve a JSON relative-winding fixture with the CPU baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from scroll_lab.winding import RelativeConstraint, score_solution, solve_bfs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--confidence-order", action="store_true")
    args = parser.parse_args()
    with args.fixture.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    constraints = [RelativeConstraint(**item) for item in raw["constraints"]]
    solution = solve_bfs(constraints, confidence_order=args.confidence_order)
    output = {
        "labels": dict(sorted(solution.labels.items())),
        "component_count": solution.component_count,
        "contradictions": [
            {
                "source": item.constraint.source,
                "target": item.constraint.target,
                "expected_delta": item.constraint.delta,
                "predicted_delta": item.predicted_delta,
                "residual": item.residual,
                "evidence_id": item.constraint.evidence_id,
            }
            for item in solution.contradictions
        ],
        "score": score_solution(solution, constraints),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 1 if solution.contradictions else 0


if __name__ == "__main__":
    raise SystemExit(main())

