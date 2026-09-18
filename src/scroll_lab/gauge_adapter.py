"""Export solved winding nodes to constraint-gauge's JSON adapter contract."""

from __future__ import annotations

import math
from typing import Any, Mapping

from .winding import WindingSolution


def export_gauge_adapter(
    solution: WindingSolution,
    nodes: Mapping[str, Mapping[str, Any]],
    *,
    name: str,
) -> dict[str, Any]:
    """Return points_xyz, winding and conf arrays in stable node-ID order.

    Coordinates must be full-resolution [x, y, z] voxels. Winding labels can
    be relative because constraint-gauge evaluates winding differences.
    """

    if set(nodes) != set(solution.labels):
        missing = sorted(set(solution.labels) - set(nodes))
        extra = sorted(set(nodes) - set(solution.labels))
        raise ValueError(f"node/solution IDs differ: missing={missing}, extra={extra}")
    points_xyz: list[list[float]] = []
    winding: list[int] = []
    confidence: list[float] = []
    for node_id in sorted(nodes):
        raw = nodes[node_id]
        point = raw.get("p")
        if not isinstance(point, (list, tuple)) or len(point) != 3:
            raise ValueError(f"{node_id}: p must be [x, y, z]")
        xyz = [float(value) for value in point]
        conf = float(raw.get("confidence", 1.0))
        if not all(math.isfinite(value) for value in xyz) or not math.isfinite(conf) or conf < 0:
            raise ValueError(f"{node_id}: nonfinite coordinate or invalid confidence")
        points_xyz.append(xyz)
        winding.append(int(solution.labels[node_id]))
        confidence.append(conf)
    return {"name": name, "points_xyz": points_xyz, "winding": winding, "conf": confidence}
