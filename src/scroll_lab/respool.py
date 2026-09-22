"""Validate and plan byte-range access to Villa ``respool`` sidecars.

The resident-pool format stores one fixed-size, C-order uint8 brick per row.
Logical bricks absent from the index are semantically all zero.  This module
does not read channel data; it proves the two small index arrays agree and
turns a half-open voxel region into the exact occupied channel-file ranges
needed to reconstruct that region.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np


def _triple_int(value: object, name: str, *, positive: bool = False) -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{name} must be a three-element JSON list")
    if any(isinstance(v, bool) or not isinstance(v, int) for v in value):
        raise ValueError(f"{name} must contain integers")
    result = tuple(int(v) for v in value)
    if positive and any(v <= 0 for v in result):
        raise ValueError(f"{name} must be strictly positive")
    return result


@dataclass(frozen=True)
class ByteRange:
    """One inclusive HTTP byte range covering consecutive pool rows."""

    row_start: int
    row_end: int
    byte_start: int
    byte_end: int

    @property
    def length(self) -> int:
        return self.byte_end - self.byte_start + 1

    def to_dict(self) -> dict[str, int | str]:
        return {
            "row_start": self.row_start,
            "row_end": self.row_end,
            "byte_start": self.byte_start,
            "byte_end": self.byte_end,
            "length": self.length,
            "http_range": f"bytes={self.byte_start}-{self.byte_end}",
        }


@dataclass(frozen=True)
class RangePlan:
    """Occupied rows and exact ranges for a half-open voxel ROI."""

    voxel_lower_zyx: tuple[int, int, int]
    voxel_upper_zyx: tuple[int, int, int]
    brick_lower_zyx: tuple[int, int, int]
    brick_upper_zyx: tuple[int, int, int]
    logical_bricks: int
    occupied_rows: tuple[int, ...]
    ranges: tuple[ByteRange, ...]
    brick_voxels: int

    @property
    def occupied_bricks(self) -> int:
        return len(self.occupied_rows)

    @property
    def absent_zero_bricks(self) -> int:
        return self.logical_bricks - self.occupied_bricks

    @property
    def payload_bytes(self) -> int:
        return self.occupied_bricks * self.brick_voxels

    @property
    def occupancy_fraction(self) -> float:
        return self.occupied_bricks / self.logical_bricks if self.logical_bricks else 0.0

    def to_dict(self, *, include_rows: bool = False) -> dict[str, object]:
        result: dict[str, object] = {
            "voxel_roi_half_open_zyx": [list(self.voxel_lower_zyx), list(self.voxel_upper_zyx)],
            "brick_roi_half_open_zyx": [list(self.brick_lower_zyx), list(self.brick_upper_zyx)],
            "logical_bricks": self.logical_bricks,
            "occupied_bricks": self.occupied_bricks,
            "absent_zero_bricks": self.absent_zero_bricks,
            "occupancy_fraction": self.occupancy_fraction,
            "payload_bytes": self.payload_bytes,
            "range_count": len(self.ranges),
            "ranges": [item.to_dict() for item in self.ranges],
        }
        if include_rows:
            result["occupied_rows"] = list(self.occupied_rows)
        return result


@dataclass(frozen=True)
class RespoolIndex:
    """A fully validated version-2 resident-pool index."""

    meta: dict[str, object]
    table: np.ndarray
    coords: np.ndarray
    array_shape: tuple[int, int, int]
    brick_shape: tuple[int, int, int]
    grid_shape: tuple[int, int, int]
    rows: int
    brick_voxels: int

    @classmethod
    def load(
        cls,
        meta_path: str | Path,
        coords_path: str | Path,
        table_path: str | Path,
    ) -> "RespoolIndex":
        with Path(meta_path).open("r", encoding="utf-8") as handle:
            meta = json.load(handle)
        if not isinstance(meta, dict):
            raise ValueError("respool metadata must be a JSON object")
        if meta.get("format") != "respool" or meta.get("version") != 2:
            raise ValueError(
                f"unsupported respool format/version: {meta.get('format')!r} v{meta.get('version')!r}"
            )
        if meta.get("dtype") != "u1":
            raise ValueError(f"expected uint8 pool metadata, got {meta.get('dtype')!r}")

        array_shape = _triple_int(meta.get("array_shape"), "array_shape", positive=True)
        brick_shape = _triple_int(meta.get("brick_shape"), "brick_shape", positive=True)
        grid_shape = _triple_int(meta.get("grid_shape"), "grid_shape", positive=True)
        expected_grid = tuple(
            (size + brick - 1) // brick for size, brick in zip(array_shape, brick_shape)
        )
        if grid_shape != expected_grid:
            raise ValueError(f"grid_shape {grid_shape} does not equal ceil(array/brick) {expected_grid}")
        rows_value = meta.get("rows")
        if isinstance(rows_value, bool) or not isinstance(rows_value, int) or rows_value < 1:
            raise ValueError("rows must be a positive integer")
        rows = int(rows_value)

        coords = np.load(Path(coords_path), allow_pickle=False)
        table = np.load(Path(table_path), allow_pickle=False)
        if coords.dtype != np.int32 or coords.shape != (rows, 3):
            raise ValueError(f"brick_coords must be int32 shape {(rows, 3)}, got {coords.dtype} {coords.shape}")
        if table.dtype != np.int32 or table.shape != grid_shape:
            raise ValueError(f"table must be int32 shape {grid_shape}, got {table.dtype} {table.shape}")
        if not np.array_equal(coords[0], np.array([-1, -1, -1], dtype=np.int32)):
            raise ValueError("brick_coords row 0 must be the reserved (-1,-1,-1) zero brick")
        if np.any(coords[1:] < 0) or np.any(coords[1:] >= np.asarray(grid_shape)):
            raise ValueError("brick_coords contains a logical coordinate outside grid_shape")
        if rows > 1 and len(np.unique(coords[1:], axis=0)) != rows - 1:
            raise ValueError("brick_coords contains duplicate occupied coordinates")
        if table.min(initial=0) < 0 or table.max(initial=0) >= rows:
            raise ValueError("table contains an invalid pool row")
        expected_rows = np.arange(1, rows, dtype=np.int32)
        mapped = table[coords[1:, 0], coords[1:, 1], coords[1:, 2]]
        if not np.array_equal(mapped, expected_rows):
            raise ValueError("table and brick_coords are not exact inverses at occupied coordinates")
        if np.count_nonzero(table) != rows - 1:
            raise ValueError("table contains missing or extra occupied entries")

        brick_voxels = math.prod(brick_shape)
        return cls(
            meta=meta,
            table=table,
            coords=coords,
            array_shape=array_shape,
            brick_shape=brick_shape,
            grid_shape=grid_shape,
            rows=rows,
            brick_voxels=brick_voxels,
        )

    @property
    def channel_file_bytes(self) -> int:
        return self.rows * self.brick_voxels

    def plan(self, lower_zyx: Sequence[int], upper_zyx: Sequence[int]) -> RangePlan:
        """Plan occupied rows intersecting half-open array voxel bounds.

        Absent logical bricks are intentionally omitted: the format defines
        them as all-zero and a sparse consumer must synthesize those values.
        """

        if len(lower_zyx) != 3 or len(upper_zyx) != 3:
            raise ValueError("ROI bounds must each have three zyx coordinates")
        lower = tuple(int(v) for v in lower_zyx)
        upper = tuple(int(v) for v in upper_zyx)
        if any(v < 0 for v in lower) or any(v > size for v, size in zip(upper, self.array_shape)):
            raise ValueError(f"ROI [{lower}, {upper}) is outside array shape {self.array_shape}")
        if any(lo >= hi for lo, hi in zip(lower, upper)):
            raise ValueError(f"ROI must be non-empty and half-open, got [{lower}, {upper})")

        brick_lower = tuple(lo // brick for lo, brick in zip(lower, self.brick_shape))
        brick_upper = tuple(
            (hi + brick - 1) // brick for hi, brick in zip(upper, self.brick_shape)
        )
        logical = math.prod(hi - lo for lo, hi in zip(brick_lower, brick_upper))
        slab = self.table[
            brick_lower[0] : brick_upper[0],
            brick_lower[1] : brick_upper[1],
            brick_lower[2] : brick_upper[2],
        ]
        occupied = tuple(int(v) for v in np.sort(slab[slab != 0], axis=None))
        ranges = tuple(_merge_rows(occupied, self.brick_voxels))
        return RangePlan(
            voxel_lower_zyx=lower,
            voxel_upper_zyx=upper,
            brick_lower_zyx=brick_lower,
            brick_upper_zyx=brick_upper,
            logical_bricks=logical,
            occupied_rows=occupied,
            ranges=ranges,
            brick_voxels=self.brick_voxels,
        )


def sampling_roi_from_closed_bounds(
    lower_zyx: Sequence[float],
    upper_zyx: Sequence[float],
    *,
    array_shape: Sequence[int],
    padding_zyx: Sequence[float] = (0.0, 0.0, 0.0),
    interpolation_halo: int = 1,
) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    """Conservatively enclose samples and their interpolation neighbours.

    Bounds and padding are expressed in the target array's voxel coordinates.
    The returned bounds are integer, half-open, clipped to ``array_shape``.
    One halo voxel is sufficient for trilinear interpolation; callers may
    request a larger halo but may not silently request a negative one.
    """

    if not all(len(v) == 3 for v in (lower_zyx, upper_zyx, array_shape, padding_zyx)):
        raise ValueError("bounds, shape, and padding must be three-dimensional")
    if interpolation_halo < 0:
        raise ValueError("interpolation_halo cannot be negative")
    if any(not math.isfinite(float(v)) for v in (*lower_zyx, *upper_zyx, *padding_zyx)):
        raise ValueError("bounds and padding must be finite")
    if any(float(p) < 0 for p in padding_zyx):
        raise ValueError("padding cannot be negative")
    if any(float(lo) > float(hi) for lo, hi in zip(lower_zyx, upper_zyx)):
        raise ValueError("closed lower bounds cannot exceed upper bounds")

    lower = tuple(
        max(0, math.floor(float(lo) - float(pad)) - interpolation_halo)
        for lo, pad in zip(lower_zyx, padding_zyx)
    )
    upper = tuple(
        min(int(size), math.floor(float(hi) + float(pad)) + interpolation_halo + 1)
        for hi, pad, size in zip(upper_zyx, padding_zyx, array_shape)
    )
    if any(lo >= hi for lo, hi in zip(lower, upper)):
        raise ValueError("sampling bounds do not intersect the target array")
    return lower, upper


def union_rois(
    rois: Iterable[tuple[Sequence[int], Sequence[int]]]
) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    materialized = list(rois)
    if not materialized:
        raise ValueError("cannot union an empty ROI collection")
    lower = tuple(min(int(roi[0][axis]) for roi in materialized) for axis in range(3))
    upper = tuple(max(int(roi[1][axis]) for roi in materialized) for axis in range(3))
    return lower, upper


def _merge_rows(rows: Sequence[int], brick_bytes: int) -> list[ByteRange]:
    if not rows:
        return []
    merged: list[ByteRange] = []
    start = previous = int(rows[0])
    for row_value in rows[1:]:
        row = int(row_value)
        if row == previous + 1:
            previous = row
            continue
        merged.append(_row_range(start, previous, brick_bytes))
        start = previous = row
    merged.append(_row_range(start, previous, brick_bytes))
    return merged


def byte_ranges_for_rows(rows: Sequence[int], brick_bytes: int) -> tuple[ByteRange, ...]:
    """Public checked wrapper for merging sorted or unsorted pool rows."""

    if brick_bytes <= 0:
        raise ValueError("brick_bytes must be positive")
    normalized = sorted(set(int(row) for row in rows))
    if any(row < 1 for row in normalized):
        raise ValueError("channel acquisition rows must exclude reserved row 0")
    return tuple(_merge_rows(normalized, brick_bytes))


def coalesce_byte_ranges(
    ranges: Sequence[ByteRange], brick_bytes: int, *, max_gap_rows: int
) -> tuple[ByteRange, ...]:
    """Merge ordered ranges across small gaps to reduce HTTP request count.

    The additional rows are acquisition-only padding. They do not change the
    set of logically requested bricks and are safe for the fail-loud sampler.
    """

    if brick_bytes <= 0 or max_gap_rows < 0:
        raise ValueError("brick_bytes must be positive and max_gap_rows nonnegative")
    if not ranges:
        return ()
    merged: list[ByteRange] = []
    current = ranges[0]
    for item in ranges[1:]:
        gap = item.row_start - current.row_end - 1
        if gap < 0:
            raise ValueError("ranges must be sorted and non-overlapping")
        if gap <= max_gap_rows:
            current = _row_range(current.row_start, item.row_end, brick_bytes)
        else:
            merged.append(current)
            current = item
    merged.append(current)
    return tuple(merged)


def _row_range(start: int, end: int, brick_bytes: int) -> ByteRange:
    return ByteRange(
        row_start=start,
        row_end=end,
        byte_start=start * brick_bytes,
        byte_end=(end + 1) * brick_bytes - 1,
    )
