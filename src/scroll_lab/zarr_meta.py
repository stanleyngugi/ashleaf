"""Metadata-only audit for the OME-Zarr v2 volumes used by the challenge."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import ValidationIssue


@dataclass(frozen=True)
class ZarrLevel:
    path: str
    shape: tuple[int, ...]
    chunks: tuple[int, ...]
    dtype: str
    relative_scale: tuple[float, ...]
    estimated_uncompressed_bytes: int | None


@dataclass(frozen=True)
class ZarrAudit:
    root: str
    axes: tuple[str, ...]
    levels: tuple[ZarrLevel, ...]
    issues: tuple[ValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


def audit_omezarr_v2(path: str | Path) -> ZarrAudit:
    """Inspect .zgroup, .zattrs and level .zarray files; never read chunks."""

    root = Path(path)
    issues: list[ValidationIssue] = []
    axes: tuple[str, ...] = ()
    levels: list[ZarrLevel] = []
    if not root.is_dir():
        return ZarrAudit(str(root), (), (), (ValidationIssue("not_directory", str(root)),))
    try:
        group = _read_object(root / ".zgroup")
        attrs = _read_object(root / ".zattrs")
    except (OSError, ValueError) as exc:
        return ZarrAudit(str(root), (), (), (ValidationIssue("invalid_zarr_root", str(exc)),))
    if group.get("zarr_format") != 2:
        issues.append(ValidationIssue("unsupported_zarr_version", "expected Zarr v2 .zgroup"))
    multiscales = attrs.get("multiscales")
    if not isinstance(multiscales, list) or not multiscales or not isinstance(multiscales[0], dict):
        return ZarrAudit(str(root), (), (), tuple(issues + [ValidationIssue("missing_multiscales", "OME multiscales metadata is missing")]))
    spec = multiscales[0]
    raw_axes = spec.get("axes")
    if isinstance(raw_axes, list):
        axes = tuple(item.get("name", "") if isinstance(item, dict) else str(item) for item in raw_axes)
        if not axes or any(not name for name in axes) or len(set(axes)) != len(axes):
            issues.append(ValidationIssue("invalid_axes", "axes must be named and unique"))
    else:
        issues.append(ValidationIssue("missing_axes", "multiscales axes are missing"))
    datasets = spec.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        return ZarrAudit(str(root), axes, (), tuple(issues + [ValidationIssue("missing_datasets", "multiscales datasets are missing")]))
    seen: set[str] = set()
    for index, dataset in enumerate(datasets):
        if not isinstance(dataset, dict):
            issues.append(ValidationIssue("invalid_dataset", f"dataset {index} is not an object"))
            continue
        level_path = dataset.get("path")
        if not isinstance(level_path, str) or not level_path or level_path.startswith("/") or ".." in Path(level_path).parts:
            issues.append(ValidationIssue("invalid_level_path", f"dataset {index}: {level_path!r}"))
            continue
        if level_path in seen:
            issues.append(ValidationIssue("duplicate_level", level_path))
        seen.add(level_path)
        try:
            array = _read_object(root / level_path / ".zarray")
            shape = _positive_int_tuple(array.get("shape"), "shape")
            chunks = _positive_int_tuple(array.get("chunks"), "chunks")
            dtype = array.get("dtype")
            if not isinstance(dtype, str) or not dtype:
                raise ValueError("dtype must be a nonempty string")
            if array.get("zarr_format") != 2:
                raise ValueError("level .zarray is not Zarr v2")
            scale = _dataset_scale(dataset)
            if len(shape) != len(chunks) or len(shape) != len(scale) or (axes and len(shape) != len(axes)):
                raise ValueError("shape/chunks/scale/axes dimensionality mismatch")
            bytes_per_value = _dtype_bytes(dtype)
            estimated_bytes = math.prod(shape) * bytes_per_value if bytes_per_value else None
            levels.append(ZarrLevel(level_path, shape, chunks, dtype, scale, estimated_bytes))
        except (OSError, ValueError, TypeError) as exc:
            issues.append(ValidationIssue("invalid_level", f"{level_path}: {exc}"))
    if levels:
        first = levels[0]
        for level in levels[1:]:
            for axis, (base_len, base_scale, length, scale) in enumerate(zip(first.shape, first.relative_scale, level.shape, level.relative_scale)):
                expected = math.ceil(base_len * base_scale / scale)
                if abs(length - expected) > 1:
                    issues.append(ValidationIssue("pyramid_shape_mismatch", f"{level.path} axis {axis}: {length} vs expected about {expected}", "warning"))
    return ZarrAudit(str(root), axes, tuple(levels), tuple(issues))


def _read_object(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be a JSON object")
    return value


def _positive_int_tuple(value: Any, field: str) -> tuple[int, ...]:
    if not isinstance(value, list) or not value or any(type(item) is not int or item <= 0 for item in value):
        raise ValueError(f"{field} must be a nonempty list of positive integers")
    return tuple(value)


def _dataset_scale(dataset: dict[str, Any]) -> tuple[float, ...]:
    transforms = dataset.get("coordinateTransformations")
    if not isinstance(transforms, list):
        raise ValueError("coordinateTransformations are missing")
    for transform in transforms:
        if isinstance(transform, dict) and transform.get("type") == "scale":
            value = transform.get("scale")
            if not isinstance(value, list) or not value:
                break
            scale = tuple(float(item) for item in value)
            if not all(math.isfinite(item) and item > 0 for item in scale):
                break
            return scale
    raise ValueError("positive scale coordinate transformation is missing")


def _dtype_bytes(dtype: str) -> int | None:
    # Common Zarr v2 NumPy dtype strings: |u1, <u2, <f4, >i4.
    if len(dtype) < 3 or dtype[0] not in "|<>=":
        return None
    try:
        size = int(dtype[2:])
    except ValueError:
        return None
    return size if size > 0 else None
