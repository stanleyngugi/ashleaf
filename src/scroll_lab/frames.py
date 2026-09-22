"""Explicit coordinate-frame contracts for cross-volume geometry.

The Vesuvius ecosystem commonly mixes coordinates stored as ``xyz`` points
with arrays indexed as ``zyx`` and pyramid levels whose voxel sizes differ by
integer factors.  This module keeps those facts in data rather than in hidden
constants.  It intentionally depends only on the Python standard library so a
frame can be validated before NumPy, Zarr, or a GPU stack is installed.

Conventions
-----------

* A point tuple is ordered exactly as ``FrameSpec.axis_order`` declares.
* Physical coordinates are always canonical ``(x, y, z)`` micrometres.
* ``origin_um_xyz`` is the physical location of coordinate ``(0, 0, 0)``.
* Bounds are closed coordinate bounds.  Their ``extent`` is a coordinate
  span, not a voxel count.
* Frames with different sample semantics (voxel centers versus corners) are
  not transformed implicitly.  The caller must supply a frame/affine that
  resolves that convention instead of accepting a silent half-voxel shift.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

Point3 = tuple[float, float, float]
Matrix4 = tuple[
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
]

_XYZ = ("x", "y", "z")
_SEMANTICS = {"voxel_center", "voxel_corner"}


def _finite_point3(value: Sequence[float], field: str) -> Point3:
    if len(value) != 3:
        raise ValueError(f"{field} must contain exactly three values")
    point = tuple(float(item) for item in value)
    if not all(math.isfinite(item) for item in point):
        raise ValueError(f"{field} must contain only finite values")
    return point  # type: ignore[return-value]


def _matrix4(value: Sequence[Sequence[float]], field: str) -> Matrix4:
    if len(value) != 4 or any(len(row) != 4 for row in value):
        raise ValueError(f"{field} must be a 4x4 matrix")
    matrix = tuple(tuple(float(item) for item in row) for row in value)
    if not all(math.isfinite(item) for row in matrix for item in row):
        raise ValueError(f"{field} must contain only finite values")
    expected = (0.0, 0.0, 0.0, 1.0)
    if any(abs(a - b) > 1e-12 for a, b in zip(matrix[3], expected)):
        raise ValueError(f"{field} must be affine with final row [0, 0, 0, 1]")
    return matrix  # type: ignore[return-value]


def _identity4() -> Matrix4:
    return (
        (1.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )


def _matmul(a: Matrix4, b: Matrix4) -> Matrix4:
    return tuple(
        tuple(sum(a[row][k] * b[k][col] for k in range(4)) for col in range(4))
        for row in range(4)
    )  # type: ignore[return-value]


def _apply(matrix: Matrix4, point: Sequence[float]) -> Point3:
    x = _finite_point3(point, "point")
    h = (*x, 1.0)
    result = tuple(sum(matrix[row][col] * h[col] for col in range(4)) for row in range(3))
    if not all(math.isfinite(item) for item in result):
        raise ValueError("transform produced a non-finite point")
    return result  # type: ignore[return-value]


def _inverse_affine(matrix: Matrix4) -> Matrix4:
    """Invert a finite affine 4x4 matrix using Gauss-Jordan elimination."""

    work = [list(matrix[row]) + list(_identity4()[row]) for row in range(4)]
    for col in range(4):
        pivot = max(range(col, 4), key=lambda row: abs(work[row][col]))
        if abs(work[pivot][col]) <= 1e-15:
            raise ValueError("voxel-to-physical affine is singular")
        work[col], work[pivot] = work[pivot], work[col]
        divisor = work[col][col]
        work[col] = [item / divisor for item in work[col]]
        for row in range(4):
            if row == col:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [a - factor * b for a, b in zip(work[row], work[col])]
    inverse = tuple(tuple(row[4:]) for row in work)
    return _matrix4(inverse, "inverse affine")


def _axis_aligned_affine(
    axis_order: Sequence[str],
    voxel_size_um: Sequence[float],
    origin_um_xyz: Sequence[float],
) -> Matrix4:
    order = tuple(str(axis).lower() for axis in axis_order)
    if len(order) != 3 or set(order) != set(_XYZ):
        raise ValueError("axis_order must be a permutation of ['x', 'y', 'z']")
    sizes = _finite_point3(voxel_size_um, "voxel_size_um")
    if any(value <= 0 for value in sizes):
        raise ValueError("voxel_size_um values must be positive")
    origin = _finite_point3(origin_um_xyz, "origin_um_xyz")
    rows: list[list[float]] = []
    for canonical_axis, offset in zip(_XYZ, origin):
        row = [0.0, 0.0, 0.0, offset]
        input_index = order.index(canonical_axis)
        row[input_index] = sizes[input_index]
        rows.append(row)
    rows.append([0.0, 0.0, 0.0, 1.0])
    return _matrix4(rows, "derived affine")


@dataclass(frozen=True)
class FrameSpec:
    """A named mapping from stored voxel coordinates to physical xyz microns."""

    name: str
    axis_order: tuple[str, str, str]
    voxel_size_um: Point3
    origin_um_xyz: Point3 = (0.0, 0.0, 0.0)
    sample_semantics: str = "voxel_center"
    source: str = ""
    affine_voxel_to_um_xyz: Matrix4 | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("frame name cannot be empty")
        order = tuple(axis.lower() for axis in self.axis_order)
        if len(order) != 3 or set(order) != set(_XYZ):
            raise ValueError("axis_order must be a permutation of ('x', 'y', 'z')")
        sizes = _finite_point3(self.voxel_size_um, "voxel_size_um")
        if any(value <= 0 for value in sizes):
            raise ValueError("voxel_size_um values must be positive")
        origin = _finite_point3(self.origin_um_xyz, "origin_um_xyz")
        if self.sample_semantics not in _SEMANTICS:
            raise ValueError(f"sample_semantics must be one of {sorted(_SEMANTICS)}")
        affine = None
        if self.affine_voxel_to_um_xyz is not None:
            affine = _matrix4(self.affine_voxel_to_um_xyz, "affine_voxel_to_um_xyz")
            _inverse_affine(affine)
        object.__setattr__(self, "axis_order", order)
        object.__setattr__(self, "voxel_size_um", sizes)
        object.__setattr__(self, "origin_um_xyz", origin)
        object.__setattr__(self, "affine_voxel_to_um_xyz", affine)

    @property
    def voxel_to_physical(self) -> Matrix4:
        return self.affine_voxel_to_um_xyz or _axis_aligned_affine(
            self.axis_order, self.voxel_size_um, self.origin_um_xyz
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "axis_order": list(self.axis_order),
            "voxel_size_um": list(self.voxel_size_um),
            "origin_um_xyz": list(self.origin_um_xyz),
            "sample_semantics": self.sample_semantics,
            "source": self.source,
        }
        if self.affine_voxel_to_um_xyz is not None:
            result["affine_voxel_to_um_xyz"] = [list(row) for row in self.affine_voxel_to_um_xyz]
        return result

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "FrameSpec":
        allowed = {
            "name", "axis_order", "voxel_size_um", "origin_um_xyz",
            "sample_semantics", "source", "affine_voxel_to_um_xyz",
        }
        unknown = sorted(set(raw) - allowed)
        if unknown:
            raise ValueError(f"unknown frame fields: {unknown}")
        missing = sorted({"name", "axis_order", "voxel_size_um"} - set(raw))
        if missing:
            raise ValueError(f"missing frame fields: {missing}")
        return cls(
            name=str(raw["name"]),
            axis_order=tuple(raw["axis_order"]),
            voxel_size_um=tuple(raw["voxel_size_um"]),
            origin_um_xyz=tuple(raw.get("origin_um_xyz", (0.0, 0.0, 0.0))),
            sample_semantics=str(raw.get("sample_semantics", "voxel_center")),
            source=str(raw.get("source", "")),
            affine_voxel_to_um_xyz=(
                tuple(tuple(row) for row in raw["affine_voxel_to_um_xyz"])
                if raw.get("affine_voxel_to_um_xyz") is not None else None
            ),
        )


@dataclass(frozen=True)
class Bounds3D:
    lower: Point3
    upper: Point3

    def __post_init__(self) -> None:
        lower = _finite_point3(self.lower, "bounds.lower")
        upper = _finite_point3(self.upper, "bounds.upper")
        if any(lo > hi for lo, hi in zip(lower, upper)):
            raise ValueError("bounds lower values cannot exceed upper values")
        object.__setattr__(self, "lower", lower)
        object.__setattr__(self, "upper", upper)

    @property
    def extent(self) -> Point3:
        return tuple(hi - lo for lo, hi in zip(self.lower, self.upper))  # type: ignore[return-value]

    @property
    def corners(self) -> tuple[Point3, ...]:
        return tuple(itertools.product(*zip(self.lower, self.upper)))  # type: ignore[return-value]

    def intersection(self, other: "Bounds3D") -> "Bounds3D | None":
        lower = tuple(max(a, b) for a, b in zip(self.lower, other.lower))
        upper = tuple(min(a, b) for a, b in zip(self.upper, other.upper))
        if any(lo > hi for lo, hi in zip(lower, upper)):
            return None
        return Bounds3D(lower, upper)  # type: ignore[arg-type]

    def to_dict(self) -> dict[str, list[float]]:
        return {"lower": list(self.lower), "upper": list(self.upper)}


@dataclass(frozen=True)
class FrameTransform:
    source: FrameSpec
    target: FrameSpec
    matrix: Matrix4

    @classmethod
    def between(cls, source: FrameSpec, target: FrameSpec) -> "FrameTransform":
        if source.sample_semantics != target.sample_semantics:
            raise ValueError(
                "sample semantics differ; resolve voxel-center/corner convention "
                "with an explicit affine instead of applying an implicit half-voxel shift"
            )
        matrix = _matmul(_inverse_affine(target.voxel_to_physical), source.voxel_to_physical)
        return cls(source, target, matrix)

    def apply_point(self, point: Sequence[float]) -> Point3:
        return _apply(self.matrix, point)

    def apply_points(self, points: Iterable[Sequence[float]]) -> tuple[Point3, ...]:
        return tuple(self.apply_point(point) for point in points)

    def apply_bounds(self, bounds: Bounds3D) -> Bounds3D:
        transformed = self.apply_points(bounds.corners)
        return Bounds3D(
            tuple(min(point[axis] for point in transformed) for axis in range(3)),
            tuple(max(point[axis] for point in transformed) for axis in range(3)),
        )  # type: ignore[arg-type]

    def inverse(self) -> "FrameTransform":
        return FrameTransform(self.target, self.source, _inverse_affine(self.matrix))

    def max_roundtrip_error(self, points: Iterable[Sequence[float]]) -> float:
        inverse = self.inverse()
        maximum = 0.0
        for point in points:
            original = _finite_point3(point, "point")
            restored = inverse.apply_point(self.apply_point(original))
            maximum = max(maximum, *(abs(a - b) for a, b in zip(original, restored)))
        return maximum

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.name,
            "target": self.target.name,
            "matrix": [list(row) for row in self.matrix],
        }


def bounds_from_points(points: Iterable[Sequence[float]]) -> Bounds3D:
    iterator = iter(points)
    try:
        first = _finite_point3(next(iterator), "point")
    except StopIteration as exc:
        raise ValueError("cannot calculate bounds of an empty point sequence") from exc
    lower = list(first)
    upper = list(first)
    for raw in iterator:
        point = _finite_point3(raw, "point")
        for axis, value in enumerate(point):
            lower[axis] = min(lower[axis], value)
            upper[axis] = max(upper[axis], value)
    return Bounds3D(tuple(lower), tuple(upper))  # type: ignore[arg-type]


def physical_overlap(
    a_frame: FrameSpec,
    a_bounds: Bounds3D,
    b_frame: FrameSpec,
    b_bounds: Bounds3D,
) -> dict[str, Any]:
    """Compare two coordinate bounds in canonical physical xyz micrometres."""

    physical = FrameSpec(
        name="physical-xyz-um",
        axis_order=("x", "y", "z"),
        voxel_size_um=(1.0, 1.0, 1.0),
        sample_semantics=a_frame.sample_semantics,
        source="canonical comparison frame",
    )
    if a_frame.sample_semantics != b_frame.sample_semantics:
        raise ValueError("cannot compare bounds with different sample semantics")
    a_um = FrameTransform.between(a_frame, physical).apply_bounds(a_bounds)
    b_um = FrameTransform.between(b_frame, physical).apply_bounds(b_bounds)
    overlap = a_um.intersection(b_um)
    return {
        "a_frame": a_frame.name,
        "b_frame": b_frame.name,
        "a_bounds_um_xyz": a_um.to_dict(),
        "b_bounds_um_xyz": b_um.to_dict(),
        "overlap": overlap is not None,
        "overlap_bounds_um_xyz": overlap.to_dict() if overlap else None,
        "overlap_extent_um_xyz": list(overlap.extent) if overlap else [0.0, 0.0, 0.0],
    }


def physical_axis_interval(
    frame: FrameSpec,
    canonical_axis: str,
    interval: Sequence[float],
) -> tuple[float, float]:
    """Convert one separable coordinate interval to physical micrometres.

    This supports evidence that reports only a z band.  It refuses a general
    affine when the requested physical axis also depends on unreported input
    axes; such an interval cannot be transformed exactly without full bounds.
    """

    axis = canonical_axis.lower()
    if axis not in _XYZ:
        raise ValueError("canonical_axis must be one of 'x', 'y', or 'z'")
    if len(interval) != 2:
        raise ValueError("interval must contain lower and upper values")
    lo, hi = (float(value) for value in interval)
    if not all(math.isfinite(value) for value in (lo, hi)) or lo > hi:
        raise ValueError("interval must be finite and ordered")
    physical_row = _XYZ.index(axis)
    input_axis = frame.axis_order.index(axis)
    row = frame.voxel_to_physical[physical_row]
    coupled = [index for index in range(3) if index != input_axis and abs(row[index]) > 1e-12]
    if coupled:
        raise ValueError(
            f"physical {axis} depends on unreported input axes {coupled}; full bounds are required"
        )
    values = (row[input_axis] * lo + row[3], row[input_axis] * hi + row[3])
    return (min(values), max(values))


def physical_axis_overlap(
    a_frame: FrameSpec,
    a_interval: Sequence[float],
    b_frame: FrameSpec,
    b_interval: Sequence[float],
    *,
    canonical_axis: str,
) -> dict[str, Any]:
    """Compare two one-axis support intervals without inventing other bounds."""

    if a_frame.sample_semantics != b_frame.sample_semantics:
        raise ValueError("cannot compare intervals with different sample semantics")
    a_um = physical_axis_interval(a_frame, canonical_axis, a_interval)
    b_um = physical_axis_interval(b_frame, canonical_axis, b_interval)
    lo, hi = max(a_um[0], b_um[0]), min(a_um[1], b_um[1])
    overlaps = lo <= hi
    return {
        "axis": canonical_axis.lower(),
        "a_frame": a_frame.name,
        "b_frame": b_frame.name,
        "a_interval_um": list(a_um),
        "b_interval_um": list(b_um),
        "overlap": overlaps,
        "overlap_interval_um": [lo, hi] if overlaps else None,
        "overlap_extent_um": hi - lo if overlaps else 0.0,
    }
