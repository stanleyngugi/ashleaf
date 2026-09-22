"""Applicability-matched adjacent-wrap pairs from a verified TIFXYZ mesh."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np


def build_local_adjacent_pairs(
    mesh_dir: str | Path,
    umbilicus_axis,
    *,
    constraint_gauge_root: str | Path,
    stride_v: int = 10,
    stride_u: int = 10,
    trim_wraps: int = 1,
    max_pairs: int = 20_000,
    seed: int = 1,
) -> tuple[np.ndarray, dict[str, np.ndarray], dict[str, object]]:
    """Return outward-oriented, true-``dw=1`` local mesh correspondences."""

    if min(stride_v, stride_u, max_pairs) < 1 or trim_wraps < 0:
        raise ValueError("strides/max_pairs must be positive and trim nonnegative")
    gauge_root = str(Path(constraint_gauge_root).resolve())
    if gauge_root not in sys.path:
        sys.path.insert(0, gauge_root)
    from gauge.meshgt import _arc_axis, _load_tifxyz, _row_chain
    from scipy.spatial import cKDTree

    mesh_path = Path(mesh_dir)
    x, y, z, valid = _load_tifxyz(str(mesh_path))
    with (mesh_path / "meta.json").open("r", encoding="utf-8") as handle:
        meta = json.load(handle)
    step_voxels = 1.0 / float(meta["scale"][0])
    guard_voxels = 10.0 * step_voxels
    transposed = _arc_axis(x, y, z, valid) == 0
    if transposed:
        x, y, z, valid = x.T, y.T, z.T, valid.T
    rows, columns = z.shape

    coverage = valid.sum(axis=1)
    good = np.nonzero(coverage >= 0.5 * coverage.max())[0]
    picks = good[np.linspace(0, len(good) - 1, min(5, len(good))).astype(int)]
    consensus = []
    for row in picks:
        cols, chain, arcs = _row_chain(x, y, z, valid, row, guard_voxels)
        consensus.append((row, cols, chain, arcs))
    row_wrap_counts = [len(chain) - 1 for _, _, chain, _ in consensus]
    values, frequencies = np.unique(row_wrap_counts, return_counts=True)
    wrap_count = int(values[np.argmax(frequencies)])
    candidates = [
        record for record, count in zip(consensus, row_wrap_counts) if count == wrap_count
    ]
    reference_row, reference_cols, reference_chain, _ = max(
        candidates, key=lambda record: len(record[1])
    )
    if wrap_count < 2 * trim_wraps + 2:
        raise ValueError(f"only {wrap_count} wraps; no retained adjacent pair after trim")
    bounds_u = reference_cols[reference_chain]

    endpoint_records: list[tuple[int, int, int, int]] = []
    endpoint_a: list[np.ndarray] = []
    endpoint_b: list[np.ndarray] = []
    distances: list[float] = []
    for row in range(0, rows, stride_v):
        for wrap in range(trim_wraps, wrap_count - 1 - trim_wraps):
            a0, a1 = int(bounds_u[wrap]), int(bounds_u[wrap + 1])
            b0, b1 = int(bounds_u[wrap + 1]), int(bounds_u[wrap + 2])
            a_columns = np.arange(a0, a1, stride_u)
            b_columns = np.arange(b0, b1)
            a_columns = a_columns[valid[row, a_columns]]
            b_columns = b_columns[valid[row, b_columns]]
            if len(a_columns) < 1 or len(b_columns) < 3:
                continue
            a_xyz = np.column_stack([x[row, a_columns], y[row, a_columns], z[row, a_columns]])
            b_curve = np.column_stack([x[row, b_columns], y[row, b_columns], z[row, b_columns]])
            distance, nearest = cKDTree(b_curve).query(a_xyz, k=1, workers=-1)
            keep = (
                (distance > 0)
                & (distance < 0.5 * (a1 - a0) * step_voxels)
                & (nearest > 0)
                & (nearest < len(b_columns) - 1)
            )
            for source_col, nearest_index, gap, source_xyz in zip(
                a_columns[keep], nearest[keep], distance[keep], a_xyz[keep]
            ):
                target_col = int(b_columns[int(nearest_index)])
                endpoint_records.append((row, int(source_col), target_col, wrap))
                endpoint_a.append(source_xyz)
                endpoint_b.append(b_curve[int(nearest_index)])
                distances.append(float(gap))

    if not endpoint_records:
        raise RuntimeError("local correspondence protocol produced no pairs")
    # Exact endpoint-index deduplication precedes the deterministic cap.
    unique_indices = []
    seen = set()
    for index, record in enumerate(endpoint_records):
        if record[:3] not in seen:
            seen.add(record[:3])
            unique_indices.append(index)
    if len(unique_indices) > max_pairs:
        rng = np.random.default_rng(seed)
        unique_indices = sorted(rng.choice(unique_indices, size=max_pairs, replace=False).tolist())

    a_mesh = np.asarray([endpoint_a[index] for index in unique_indices], dtype=np.float64)
    b_mesh = np.asarray([endpoint_b[index] for index in unique_indices], dtype=np.float64)
    selected_distances = np.asarray([distances[index] for index in unique_indices])
    wraps = np.asarray([endpoint_records[index][3] for index in unique_indices], dtype=np.int64)
    a_working, b_working = a_mesh / 4.0, b_mesh / 4.0

    midpoint_z = 0.5 * (a_working[:, 2] + b_working[:, 2])
    centers = np.asarray([umbilicus_axis(float(value)) for value in midpoint_z])
    radius_a = np.linalg.norm(a_working[:, :2] - centers, axis=1)
    radius_b = np.linalg.norm(b_working[:, :2] - centers, axis=1)
    nonzero = radius_a != radius_b
    a_working, b_working = a_working[nonzero], b_working[nonzero]
    wraps = wraps[nonzero]
    selected_distances = selected_distances[nonzero]
    radius_a, radius_b = radius_a[nonzero], radius_b[nonzero]
    swap = radius_b < radius_a
    original_a = a_working.copy()
    a_working[swap] = b_working[swap]
    b_working[swap] = original_a[swap]

    pair_count = len(a_working)
    points = np.concatenate([a_working, b_working], axis=0)
    pairs = {
        "a": np.arange(pair_count, dtype=np.int64),
        "b": np.arange(pair_count, 2 * pair_count, dtype=np.int64),
        "dw": np.ones(pair_count, dtype=np.int64),
    }
    vector_a = a_working[:, :2] - centers[nonzero]
    vector_b = b_working[:, :2] - centers[nonzero]
    angular = np.abs(np.arctan2(
        vector_a[:, 0] * vector_b[:, 1] - vector_a[:, 1] * vector_b[:, 0],
        np.sum(vector_a * vector_b, axis=1),
    )) * 180.0 / np.pi
    working_distance = np.linalg.norm(b_working - a_working, axis=1)
    info: dict[str, object] = {
        "protocol": "adjacent-wrap same-row nearest correspondence",
        "transposed_arc_axis": transposed,
        "reference_row": int(reference_row),
        "row_wrap_counts": row_wrap_counts,
        "n_wraps": wrap_count,
        "trimmed": trim_wraps,
        "stride_v": stride_v,
        "stride_u": stride_u,
        "candidate_pairs_before_dedup_cap": len(endpoint_records),
        "unique_pairs_before_cap": len(seen),
        "pairs_after_cap_and_orientation": pair_count,
        "orientation_swaps": int(swap.sum()),
        "equal_radius_rejections": int((~nonzero).sum()),
        "wrap_histogram": {
            str(int(value)): int(count)
            for value, count in zip(*np.unique(wraps, return_counts=True))
        },
        "working_distance_percentiles": _percentiles(working_distance),
        "angular_separation_degrees_percentiles": _percentiles(angular),
        "raw_mesh_gap_voxels_percentiles": _percentiles(selected_distances),
    }
    return points, pairs, info


def _percentiles(values: np.ndarray) -> dict[str, float]:
    levels = (0, 25, 50, 75, 90, 99, 100)
    measured = np.percentile(values, levels)
    return {f"p{level}": float(value) for level, value in zip(levels, measured)}
