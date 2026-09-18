"""Dependency-light benchmark orchestration for the first research tracks."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .manifest import validate_manifest
from .provenance import environment_fingerprint
from .winding import RelativeConstraint, score_solution, solve_bfs


def run_winding_benchmark(
    manifest: Mapping[str, Any],
    constraints: Sequence[RelativeConstraint],
    *,
    confidence_order: bool = False,
    repo_root: str | None = None,
) -> dict[str, Any]:
    """Run the CPU baseline and return a stable report object."""

    manifest_issues = validate_manifest(manifest)
    solution = solve_bfs(constraints, confidence_order=confidence_order)
    return {
        "benchmark": "relative-winding-cpu-baseline",
        "manifest": {
            "asset_count": len(manifest.get("assets", [])) if isinstance(manifest.get("assets"), list) else 0,
            "issue_count": len(manifest_issues),
            "issues": [
                {"code": issue.code, "message": issue.message, "severity": issue.severity}
                for issue in manifest_issues
            ],
        },
        "solver": {"name": "bfs", "confidence_order": confidence_order},
        "solution": {
            "labels": dict(sorted(solution.labels.items())),
            "component_count": solution.component_count,
            "contradiction_count": len(solution.contradictions),
        },
        "score": score_solution(solution, constraints),
        "provenance": environment_fingerprint(repo_root),
    }

