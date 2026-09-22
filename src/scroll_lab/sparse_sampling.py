"""CPU sampling of a selectively downloaded Villa resident pool."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Sequence

import numpy as np

from .respool import RespoolIndex


def _sha256(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


class SparseRespoolSampler:
    """Trilinear CPU sampler backed only by acquired occupied rows.

    Original pool row 0 and all logically absent bricks return zero. If a
    requested coordinate reaches an occupied row that was not acquired, the
    sampler raises instead of silently changing the estimator.
    """

    def __init__(
        self,
        index: RespoolIndex,
        compact_pool: np.ndarray,
        row_remap: np.ndarray,
    ) -> None:
        if compact_pool.dtype != np.uint8 or compact_pool.ndim != 2:
            raise ValueError("compact pool must be a two-dimensional uint8 array")
        if compact_pool.shape[1] != index.brick_voxels:
            raise ValueError("compact pool row width does not match brick geometry")
        if row_remap.dtype != np.int32 or row_remap.shape != (index.rows,):
            raise ValueError("row remap must be int32 with one entry per original row")
        if not np.all(compact_pool[0] == 0) or row_remap[0] != 0:
            raise ValueError("compact row zero must remain the all-zero row")
        self.index = index
        self.pool = compact_pool
        self.row_remap = row_remap

    @classmethod
    def from_download(
        cls,
        index: RespoolIndex,
        download_manifest_path: str | Path,
        *,
        verify_hashes: bool = True,
    ) -> "SparseRespoolSampler":
        manifest_path = Path(download_manifest_path)
        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        if manifest.get("kind") != "framebridge_respool_range_download":
            raise ValueError(f"unsupported download manifest {manifest.get('kind')!r}")
        files = manifest.get("files")
        if not isinstance(files, list) or not files:
            raise ValueError("download manifest has no files")

        acquired_rows: list[int] = []
        for item in files:
            start, end = int(item["row_start"]), int(item["row_end"])
            if start < 1 or end < start or end >= index.rows:
                raise ValueError(f"invalid acquired row interval {start}-{end}")
            acquired_rows.extend(range(start, end + 1))
        if len(acquired_rows) != len(set(acquired_rows)):
            raise ValueError("download manifest contains overlapping row intervals")
        acquired_rows.sort()

        compact = np.zeros((len(acquired_rows) + 1, index.brick_voxels), dtype=np.uint8)
        remap = np.zeros(index.rows, dtype=np.int32)
        compact_cursor = 1
        for item in sorted(files, key=lambda value: int(value["row_start"])):
            path = manifest_path.parent / str(item["path"])
            expected_bytes = int(item["bytes"])
            if path.stat().st_size != expected_bytes:
                raise ValueError(f"{path}: byte size changed")
            if verify_hashes and _sha256(path) != item["sha256"]:
                raise ValueError(f"{path}: SHA-256 mismatch")
            rows = int(item["row_end"]) - int(item["row_start"]) + 1
            if expected_bytes != rows * index.brick_voxels:
                raise ValueError(f"{path}: payload does not contain whole brick rows")
            block = np.fromfile(path, dtype=np.uint8).reshape(rows, index.brick_voxels)
            compact[compact_cursor : compact_cursor + rows] = block
            original = np.arange(int(item["row_start"]), int(item["row_end"]) + 1)
            remap[original] = np.arange(compact_cursor, compact_cursor + rows, dtype=np.int32)
            compact_cursor += rows
        return cls(index, compact, remap)

    def sample(
        self, coordinates_zyx: np.ndarray, *, quantize_uint8: bool = False
    ) -> np.ndarray:
        """Trilinearly sample finite, in-bounds zyx coordinates.

        SciPy's ``map_coordinates`` defaults its output dtype to the input
        dtype. The frozen E1 therefore rounds interpolated values back to
        uint8 before decoding. ``quantize_uint8=True`` reproduces that
        behavior; the default retains the mathematically interpolated float.
        """

        coordinates = np.asarray(coordinates_zyx, dtype=np.float64)
        if coordinates.ndim != 2 or coordinates.shape[1] != 3:
            raise ValueError("coordinates must have shape (N,3) in zyx order")
        if not np.isfinite(coordinates).all():
            raise ValueError("coordinates must be finite")
        shape = np.asarray(self.index.array_shape, dtype=np.float64)
        if np.any(coordinates < 0) or np.any(coordinates > shape - 1):
            raise IndexError("sample coordinate outside resident-pool array")
        if not len(coordinates):
            return np.empty(0, dtype=np.float64)

        lower = np.floor(coordinates).astype(np.int64)
        upper = np.minimum(lower + 1, np.asarray(self.index.array_shape) - 1)
        fraction = coordinates - lower
        result = np.zeros(len(coordinates), dtype=np.float64)
        for z_high in (0, 1):
            for y_high in (0, 1):
                for x_high in (0, 1):
                    choose = np.array([z_high, y_high, x_high], dtype=bool)
                    integer = np.where(choose, upper, lower)
                    weight_axis = np.where(choose, fraction, 1.0 - fraction)
                    weight = np.prod(weight_axis, axis=1)
                    result += weight * self._gather_integer(integer)
        if quantize_uint8:
            return np.rint(result).clip(0, 255).astype(np.uint8)
        return result

    def _gather_integer(self, integer_zyx: np.ndarray) -> np.ndarray:
        brick = np.asarray(self.index.brick_shape, dtype=np.int64)
        brick_index = np.floor_divide(integer_zyx, brick)
        original_rows = self.index.table[
            brick_index[:, 0], brick_index[:, 1], brick_index[:, 2]
        ]
        compact_rows = self.row_remap[original_rows]
        missing = (original_rows != 0) & (compact_rows == 0)
        if np.any(missing):
            rows = np.unique(original_rows[missing])
            preview = ",".join(str(int(v)) for v in rows[:8])
            raise RuntimeError(
                f"sampling reached {len(rows)} occupied row(s) absent from the acquisition: {preview}"
            )
        local = integer_zyx - brick_index * brick
        linear = (local[:, 0] * brick[1] + local[:, 1]) * brick[2] + local[:, 2]
        return self.pool[compact_rows, linear].astype(np.float64)
