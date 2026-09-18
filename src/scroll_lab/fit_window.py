"""Preflight a spiral-fit Z window against patch geometry and annotations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .pointcollections import audit_pointcollections, load_pointcollections
from .tifxyz import audit_tifxyz


@dataclass(frozen=True)
class PatchWindowStatus:
    path: str
    cached_bbox_intersects: bool | None
    actual_vertices_inside: int | None
    stale_bbox: bool
    audit_ok: bool


@dataclass(frozen=True)
class WindowPreflight:
    z0: float
    z1: float
    patches: tuple[PatchWindowStatus, ...]
    annotation_points_inside: dict[str, int]
    metadata_candidate_patches: int
    actual_active_patches: int
    false_negative_metadata_patches: int
    unknown_patches: int


def preflight_fit_window(
    patch_paths: Iterable[str | Path],
    *,
    z0: float,
    z1: float,
    annotation_paths: Iterable[str | Path] = (),
    scan_pixels: bool = False,
    max_pixels: int = 20_000_000,
) -> WindowPreflight:
    """Count candidate patches and points in a half-open full-res Z window."""

    if not z0 < z1:
        raise ValueError("require z0 < z1")
    statuses: list[PatchWindowStatus] = []
    for path in patch_paths:
        audit = audit_tifxyz(path, scan_pixels=scan_pixels, max_pixels=max_pixels)
        cached_bbox = audit.metadata.get("bbox")
        cached_intersects = None
        if (
            isinstance(cached_bbox, list)
            and len(cached_bbox) == 2
            and all(isinstance(item, list) and len(item) == 3 for item in cached_bbox)
        ):
            try:
                cached_intersects = float(cached_bbox[0][2]) < z1 and float(cached_bbox[1][2]) >= z0
            except (TypeError, ValueError):
                pass
        actual_count = None
        if scan_pixels and audit.stats and "valid_vertices" in audit.stats:
            actual_count = (
                _count_valid_vertices_in_z_window(Path(path), z0, z1)
                if audit.stats["valid_vertices"] > 0 else 0
            )
        statuses.append(PatchWindowStatus(
            str(path), cached_intersects, actual_count,
            any(issue.code == "stale_bbox" for issue in audit.issues), audit.ok,
        ))

    annotation_counts: dict[str, int] = {}
    for path in annotation_paths:
        raw = load_pointcollections(path)
        audit = audit_pointcollections(raw)
        if not audit.ok:
            raise ValueError(f"annotation audit failed: {path}")
        count = sum(
            z0 <= float(point["p"][2]) < z1
            for collection in raw["collections"].values()
            for point in collection.get("points", {}).values()
        )
        annotation_counts[str(path)] = count
    return WindowPreflight(
        z0, z1, tuple(statuses), annotation_counts,
        sum(status.cached_bbox_intersects is True for status in statuses),
        sum(status.actual_vertices_inside is not None and status.actual_vertices_inside > 0 for status in statuses),
        sum(status.cached_bbox_intersects is False and status.actual_vertices_inside is not None and status.actual_vertices_inside > 0 for status in statuses),
        sum(status.actual_vertices_inside is None for status in statuses) if scan_pixels else len(statuses),
    )


def _count_valid_vertices_in_z_window(path: Path, z0: float, z1: float) -> int:
    import numpy as np
    import tifffile

    z = tifffile.imread(path / "z.tif")
    valid = np.isfinite(z) & (z > 0) & (z >= z0) & (z < z1)
    mask_path = path / "mask.tif"
    if mask_path.is_file():
        mask = tifffile.imread(mask_path)
        if mask.ndim == 3:
            mask = mask[..., 0]
        if mask.ndim != 2 or mask.shape[0] % z.shape[0] or mask.shape[1] % z.shape[1]:
            raise ValueError(f"mask shape incompatible: {mask_path}")
        factor_y, factor_x = mask.shape[0] // z.shape[0], mask.shape[1] // z.shape[1]
        valid &= (mask.reshape(z.shape[0], factor_y, z.shape[1], factor_x) >= 255).all(axis=(1, 3))
    return int(np.count_nonzero(valid))
