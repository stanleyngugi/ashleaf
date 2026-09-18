"""Dependency-light checks for geometry metadata.

These checks intentionally operate on ordinary Python sequences.  They can run
in a clean CPU environment before NumPy, Zarr, or the official villa stack is
installed.  Adapters for those formats should convert their data into these
small primitives instead of duplicating validation logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Sequence

Point3 = tuple[float, float, float]


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"


def _point3(value: Sequence[float]) -> Point3:
    if len(value) != 3:
        raise ValueError(f"expected 3 coordinates, got {len(value)}")
    point = tuple(float(x) for x in value)
    if not all(isfinite(x) for x in point):
        raise ValueError(f"non-finite point: {value!r}")
    return point  # type: ignore[return-value]


def validate_bbox(
    points: Iterable[Sequence[float]],
    bbox: Sequence[Sequence[float]],
    *,
    tolerance: float = 1e-6,
) -> list[ValidationIssue]:
    """Check that every valid point lies inside an axis-aligned 3D bbox.

    `bbox` is represented as ``[[min_x, min_y, min_z], [max_x, max_y, max_z]]``.
    This is intentionally independent of any TIFF/TIFXYZ reader.  A caller can
    filter sentinel vertices before passing the points here.
    """

    issues: list[ValidationIssue] = []
    if len(bbox) != 2:
        return [ValidationIssue("bbox_shape", "bbox must contain min and max points")]
    try:
        lower, upper = _point3(bbox[0]), _point3(bbox[1])
    except (TypeError, ValueError) as exc:
        return [ValidationIssue("bbox_values", str(exc))]

    for axis, (lo, hi) in enumerate(zip(lower, upper)):
        if lo > hi:
            issues.append(ValidationIssue("bbox_order", f"axis {axis}: min exceeds max"))

    try:
        checked_points = [_point3(point) for point in points]
    except (TypeError, ValueError) as exc:
        return issues + [ValidationIssue("point_values", str(exc))]

    for index, point in enumerate(checked_points):
        outside = [
            axis
            for axis, (value, lo, hi) in enumerate(zip(point, lower, upper))
            if value < lo - tolerance or value > hi + tolerance
        ]
        if outside:
            issues.append(
                ValidationIssue(
                    "point_outside_bbox",
                    f"point {index} is outside bbox on axes {outside}",
                )
            )
    return issues


def validate_spacing(
    spacing: Sequence[float],
    *,
    allow_anisotropy: bool = True,
    min_spacing: float = 1e-9,
    max_spacing: float = 1e6,
) -> list[ValidationIssue]:
    """Validate positive finite voxel/grid spacing without assuming its units."""

    issues: list[ValidationIssue] = []
    try:
        values = [float(x) for x in spacing]
    except (TypeError, ValueError) as exc:
        return [ValidationIssue("spacing_values", str(exc))]
    if not values:
        return [ValidationIssue("spacing_empty", "spacing cannot be empty")]
    for axis, value in enumerate(values):
        if not isfinite(value) or value <= 0:
            issues.append(ValidationIssue("spacing_nonpositive", f"axis {axis}: {value!r}"))
        elif value < min_spacing or value > max_spacing:
            issues.append(ValidationIssue("spacing_extreme", f"axis {axis}: {value!r}"))
    if not allow_anisotropy and len(set(values)) > 1:
        issues.append(ValidationIssue("unexpected_anisotropy", f"spacing={values!r}"))
    return issues


def validate_shape(shape: Sequence[int]) -> list[ValidationIssue]:
    """Validate a positive finite array shape."""

    issues: list[ValidationIssue] = []
    try:
        values = [int(x) for x in shape]
    except (TypeError, ValueError) as exc:
        return [ValidationIssue("shape_values", str(exc))]
    if not values:
        return [ValidationIssue("shape_empty", "shape cannot be empty")]
    for axis, value in enumerate(values):
        if value <= 0:
            issues.append(ValidationIssue("shape_nonpositive", f"axis {axis}: {value!r}"))
    return issues

