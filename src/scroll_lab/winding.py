"""Small deterministic baselines for relative winding constraints.

The official problem uses constraints of the form
``winding[v] - winding[u] = delta``.  This module is intentionally a baseline,
not a replacement for stronger synchronization projects.  Its value is as a
common reference and as a test oracle for adapters and future GPU solvers.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class RelativeConstraint:
    source: str
    target: str
    delta: int
    confidence: float = 1.0
    evidence_id: str = ""


@dataclass(frozen=True)
class Contradiction:
    constraint: RelativeConstraint
    predicted_delta: int
    residual: int


@dataclass(frozen=True)
class WindingSolution:
    labels: Mapping[str, int]
    contradictions: tuple[Contradiction, ...]
    component_count: int


def solve_bfs(
    constraints: Iterable[RelativeConstraint],
    *,
    confidence_order: bool = False,
) -> WindingSolution:
    """Solve a relative-constraint graph by deterministic propagation.

    Each connected component is assigned an arbitrary zero origin.  If an
    edge disagrees with an already assigned path, it is retained as a
    contradiction instead of being silently discarded.
    """

    edges = list(constraints)
    adjacency: dict[str, list[tuple[str, int, RelativeConstraint]]] = defaultdict(list)
    nodes: set[str] = set()
    for edge in edges:
        if not isinstance(edge.delta, int):
            raise TypeError("constraint delta must be an integer")
        if edge.source == edge.target and edge.delta != 0:
            # Keep this as a graph contradiction, handled uniformly below.
            nodes.add(edge.source)
        else:
            nodes.update((edge.source, edge.target))
        adjacency[edge.source].append((edge.target, edge.delta, edge))
        adjacency[edge.target].append((edge.source, -edge.delta, edge))

    for node in adjacency:
        adjacency[node].sort(key=lambda item: (
            -item[2].confidence if confidence_order else 0,
            item[0],
            item[2].evidence_id,
        ))

    labels: dict[str, int] = {}
    contradictions: list[Contradiction] = []
    components = 0
    for root in sorted(nodes):
        if root in labels:
            continue
        components += 1
        labels[root] = 0
        queue = deque([root])
        while queue:
            current = queue.popleft()
            for neighbour, expected_delta, edge in adjacency[current]:
                candidate = labels[current] + expected_delta
                if neighbour not in labels:
                    labels[neighbour] = candidate
                    queue.append(neighbour)
                    continue
                predicted_delta = labels[neighbour] - labels[current]
                if predicted_delta != expected_delta:
                    contradictions.append(
                        Contradiction(edge, predicted_delta, predicted_delta - expected_delta)
                    )

    contradictions.sort(key=lambda item: (item.constraint.source, item.constraint.target, item.constraint.evidence_id))
    return WindingSolution(labels, tuple(contradictions), components)


def score_solution(
    solution: WindingSolution,
    constraints: Iterable[RelativeConstraint],
) -> dict[str, float]:
    """Score constraint satisfaction for a reproducible baseline report."""

    edges = list(constraints)
    if not edges:
        return {"edge_count": 0.0, "satisfied_fraction": 1.0, "weighted_satisfied_fraction": 1.0}
    satisfied = 0
    total_weight = 0.0
    satisfied_weight = 0.0
    for edge in edges:
        if edge.source not in solution.labels or edge.target not in solution.labels:
            continue
        total_weight += max(0.0, float(edge.confidence))
        if solution.labels[edge.target] - solution.labels[edge.source] == edge.delta:
            satisfied += 1
            satisfied_weight += max(0.0, float(edge.confidence))
    return {
        "edge_count": float(len(edges)),
        "satisfied_fraction": satisfied / len(edges),
        "weighted_satisfied_fraction": satisfied_weight / total_weight if total_weight else 1.0,
        "contradiction_count": float(len(solution.contradictions)),
    }

