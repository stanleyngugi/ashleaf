"""Small weighted least-squares winding synchronization diagnostic.

Not the official spiral fitter. All edges remain in the objective; one zero
gauge is imposed per connected component before integer rounding.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
import math
from typing import Iterable, Mapping

import numpy as np

from .winding import RelativeConstraint


@dataclass(frozen=True)
class WeightedWindingSolution:
    labels: Mapping[str, int]
    continuous: Mapping[str, float]
    component_count: int
    weighted_squared_residual: float


def solve_weighted_winding(
    constraints: Iterable[RelativeConstraint],
    *,
    multipliers: Mapping[str, float] | None = None,
) -> WeightedWindingSolution:
    """Solve `min sum weight*(x_b-x_a-delta)^2`, then round to integers."""

    edges = list(constraints)
    factors = multipliers or {}
    adjacency: dict[str, set[str]] = defaultdict(set)
    weights = []
    for edge in edges:
        if type(edge.delta) is not int:
            raise TypeError("integer winding differences required")
        if not math.isfinite(edge.confidence) or not 0 <= edge.confidence <= 1:
            raise ValueError("E1 confidence must be finite in [0,1]")
        factor = float(factors.get(edge.evidence_id, 1.0))
        if not math.isfinite(factor) or factor <= 0:
            raise ValueError("all weight multipliers must be positive and finite")
        weights.append(max(edge.confidence, 0.05) * factor)
        adjacency[edge.source].add(edge.target)
        adjacency[edge.target].add(edge.source)

    component_for: dict[str, int] = {}
    components: list[list[str]] = []
    for start in sorted(adjacency):
        if start in component_for:
            continue
        number = len(components)
        queue = deque([start])
        component_for[start] = number
        nodes = []
        while queue:
            node = queue.popleft()
            nodes.append(node)
            for neighbour in sorted(adjacency[node]):
                if neighbour not in component_for:
                    component_for[neighbour] = number
                    queue.append(neighbour)
        components.append(sorted(nodes))

    grouped: list[list[tuple[RelativeConstraint, float]]] = [[] for _ in components]
    for edge, weight in zip(edges, weights):
        grouped[component_for[edge.source]].append((edge, weight))
    continuous: dict[str, float] = {}
    labels: dict[str, int] = {}
    residual_sum = 0.0
    for nodes, component_edges in zip(components, grouped):
        anchor = nodes[0]
        columns = {node: i for i, node in enumerate(nodes[1:])}
        matrix = np.zeros((len(component_edges), len(columns)), dtype=np.float64)
        target = np.zeros(len(component_edges), dtype=np.float64)
        for i, (edge, weight) in enumerate(component_edges):
            factor = math.sqrt(weight)
            if edge.source != anchor:
                matrix[i, columns[edge.source]] -= factor
            if edge.target != anchor:
                matrix[i, columns[edge.target]] += factor
            target[i] = factor * edge.delta
        solved = np.linalg.lstsq(matrix, target, rcond=None)[0] if columns else np.empty(0)
        continuous[anchor] = 0.0
        labels[anchor] = 0
        for node, column in columns.items():
            value = float(solved[column])
            continuous[node] = value
            labels[node] = int(np.rint(value))
        residual_sum += float(np.sum((matrix @ solved - target) ** 2))
    return WeightedWindingSolution(labels, continuous, len(components), residual_sum)
