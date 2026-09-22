"""Conservative brick support for E1's frozen seven-ray estimator."""

from __future__ import annotations

import itertools
import math
from typing import Iterable, Sequence

import numpy as np


def conservative_line_bricks(
    start_zyx: Sequence[float],
    end_zyx: Sequence[float],
    *,
    brick_shape_zyx: Sequence[int],
    grid_shape_zyx: Sequence[int],
    interpolation_halo_voxels: float = 1.0,
    max_step_voxels: float | None = None,
) -> set[tuple[int, int, int]]:
    """Return every brick in a conservative halo around a line segment.

    The line is divided so no coordinate can move by a full brick between
    consecutive samples.  For each subsegment, all bricks in the integer box
    enclosing that subsegment plus the requested halo are included.  This can
    over-select corner bricks but cannot skip a brick intersected by the
    continuous segment or its axis-aligned halo.
    """

    start = np.asarray(start_zyx, dtype=np.float64)
    end = np.asarray(end_zyx, dtype=np.float64)
    brick = np.asarray(brick_shape_zyx, dtype=np.int64)
    grid = np.asarray(grid_shape_zyx, dtype=np.int64)
    if start.shape != (3,) or end.shape != (3,):
        raise ValueError("line endpoints must be three-dimensional")
    if brick.shape != (3,) or grid.shape != (3,) or np.any(brick <= 0) or np.any(grid <= 0):
        raise ValueError("brick and grid shapes must be positive triples")
    if not np.isfinite(start).all() or not np.isfinite(end).all():
        raise ValueError("line endpoints must be finite")
    if interpolation_halo_voxels < 0:
        raise ValueError("interpolation halo cannot be negative")
    safe_step = float(np.min(brick) / 2.0 if max_step_voxels is None else max_step_voxels)
    if not math.isfinite(safe_step) or safe_step <= 0 or safe_step >= float(np.min(brick)):
        raise ValueError("max_step_voxels must be positive and smaller than every brick dimension")

    segments = max(1, int(math.ceil(float(np.max(np.abs(end - start))) / safe_step)))
    samples = np.linspace(start, end, segments + 1)
    result: set[tuple[int, int, int]] = set()
    halo = float(interpolation_halo_voxels)
    for first, second in zip(samples[:-1], samples[1:]):
        voxel_lower = np.floor(np.minimum(first, second) - halo).astype(np.int64)
        voxel_upper = np.floor(np.maximum(first, second) + halo).astype(np.int64)
        brick_lower = np.floor_divide(voxel_lower, brick)
        brick_upper = np.floor_divide(voxel_upper, brick)
        for coordinate in itertools.product(
            *(range(int(lo), int(hi) + 1) for lo, hi in zip(brick_lower, brick_upper))
        ):
            if all(0 <= coordinate[axis] < grid[axis] for axis in range(3)):
                result.add(tuple(int(v) for v in coordinate))
    return result


def e1_multiray_bricks(
    a_xyz_working: Sequence[float],
    b_xyz_working: Sequence[float],
    *,
    array_shape_zyx: Sequence[int],
    brick_shape_zyx: Sequence[int],
    grid_shape_zyx: Sequence[int],
    lasagna_scale: float = 4.0,
    m_rays: int = 7,
    max_offset_working_voxels: float = 6.0,
) -> tuple[set[tuple[int, int, int]], int]:
    """Plan valid E1 rays for one pair, returning bricks and valid-ray count."""

    a = np.asarray(a_xyz_working, dtype=np.float64)
    b = np.asarray(b_xyz_working, dtype=np.float64)
    shape = np.asarray(array_shape_zyx, dtype=np.float64)
    if a.shape != (3,) or b.shape != (3,) or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("working-frame endpoints must be finite xyz triples")
    if lasagna_scale <= 0 or m_rays < 1 or max_offset_working_voxels < 0:
        raise ValueError("invalid E1 sampling parameters")
    direction = b - a
    perp = np.array([-direction[1], direction[0], 0.0])
    norm = float(np.linalg.norm(perp))
    if norm < 1e-9:
        perp = np.array([1.0, 0.0, 0.0])
    else:
        perp /= norm

    bricks: set[tuple[int, int, int]] = set()
    valid_rays = 0
    for offset in np.linspace(-max_offset_working_voxels, max_offset_working_voxels, m_rays):
        start_xyz = (a + perp * offset) / lasagna_scale
        end_xyz = (b + perp * offset) / lasagna_scale
        start_zyx = start_xyz[::-1]
        end_zyx = end_xyz[::-1]
        # A straight segment is inside an axis-aligned convex box iff both
        # endpoints are inside. This reproduces E1's per-sample array test.
        if np.any(start_zyx < 0) or np.any(end_zyx < 0):
            continue
        if np.any(start_zyx > shape - 1) or np.any(end_zyx > shape - 1):
            continue
        valid_rays += 1
        bricks.update(
            conservative_line_bricks(
                start_zyx,
                end_zyx,
                brick_shape_zyx=brick_shape_zyx,
                grid_shape_zyx=grid_shape_zyx,
                interpolation_halo_voxels=1.0,
            )
        )
    return bricks, valid_rays


def rows_for_bricks(table: np.ndarray, bricks: Iterable[Sequence[int]]) -> tuple[int, ...]:
    """Map requested logical bricks to sorted occupied rows, omitting zeros."""

    coordinates = sorted(set(tuple(int(v) for v in item) for item in bricks))
    if not coordinates:
        return ()
    array = np.asarray(coordinates, dtype=np.int64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("brick coordinates must be zyx triples")
    if np.any(array < 0) or np.any(array >= np.asarray(table.shape)):
        raise ValueError("brick coordinate outside table")
    rows = table[array[:, 0], array[:, 1], array[:, 2]]
    return tuple(int(v) for v in np.unique(rows[rows != 0]))
