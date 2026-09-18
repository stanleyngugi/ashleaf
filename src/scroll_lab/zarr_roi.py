"""Plan bounded reads against Zarr metadata before touching CT chunks."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from .zarr_meta import ZarrLevel


@dataclass(frozen=True)
class RoiPlan:
    level: str
    start: tuple[int, ...]
    stop: tuple[int, ...]
    chunk_start: tuple[int, ...]
    chunk_stop_exclusive: tuple[int, ...]
    requested_voxels: int
    touched_chunks: int
    estimated_chunk_bytes_upper_bound: int | None
    overfetch_ratio_upper_bound: float | None


def plan_roi(level: ZarrLevel, start: Sequence[int], stop: Sequence[int]) -> RoiPlan:
    """Estimate the worst-case uncompressed bytes for a half-open ROI."""

    begin = tuple(start)
    end = tuple(stop)
    if len(begin) != len(level.shape) or len(end) != len(level.shape):
        raise ValueError("ROI dimensionality must match the array")
    if any(type(lo) is not int or type(hi) is not int for lo, hi in zip(begin, end)):
        raise ValueError("ROI bounds must be integers")
    for axis, (lo, hi, length) in enumerate(zip(begin, end, level.shape)):
        if not (0 <= lo < hi <= length):
            raise ValueError(f"axis {axis}: require 0 <= start < stop <= {length}")
    chunk_begin = tuple(lo // chunk for lo, chunk in zip(begin, level.chunks))
    chunk_end = tuple((hi - 1) // chunk + 1 for hi, chunk in zip(end, level.chunks))
    touched = math.prod(hi - lo for lo, hi in zip(chunk_begin, chunk_end))
    requested = math.prod(hi - lo for lo, hi in zip(begin, end))
    if level.estimated_uncompressed_bytes is None:
        estimated = None
        overfetch = None
    else:
        item_size = level.estimated_uncompressed_bytes // math.prod(level.shape)
        estimated = touched * math.prod(level.chunks) * item_size
        overfetch = estimated / (requested * item_size)
    return RoiPlan(level.path, begin, end, chunk_begin, chunk_end, requested, touched, estimated, overfetch)
