"""Audit VC3D point-collection files used by the spiral fitter."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import ValidationIssue


@dataclass(frozen=True)
class PointCollectionAudit:
    collection_count: int
    point_count: int
    empty_collections: int
    annotated_collections: int
    unannotated_collections: int
    issues: tuple[ValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


def load_pointcollections(path: str | Path) -> Mapping[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("point-collection JSON root must be an object")
    return value


def audit_pointcollections(
    raw: Mapping[str, Any],
    *,
    volume_shape_zyx: Sequence[int] | None = None,
) -> PointCollectionAudit:
    issues: list[ValidationIssue] = []
    if str(raw.get("vc_pointcollections_json_version")) != "1":
        issues.append(ValidationIssue("unsupported_pointcollections_version", "expected version 1"))
    collections = raw.get("collections")
    if not isinstance(collections, dict):
        return PointCollectionAudit(0, 0, 0, 0, 0, tuple(issues + [ValidationIssue("missing_collections", "collections must be an object")]))
    shape = None
    if volume_shape_zyx is not None:
        shape = tuple(volume_shape_zyx)
        if len(shape) != 3 or any(type(value) is not int or value <= 0 for value in shape):
            raise ValueError("volume_shape_zyx must contain three positive integers")

    point_count = 0
    empty = 0
    annotated = 0
    unannotated = 0
    for collection_id, collection in collections.items():
        if not isinstance(collection, dict):
            issues.append(ValidationIssue("invalid_collection", f"{collection_id}: not an object"))
            continue
        points = collection.get("points")
        if not isinstance(points, dict):
            issues.append(ValidationIssue("missing_points", f"{collection_id}: points must be an object"))
            continue
        if not points:
            empty += 1
            continue
        point_count += len(points)
        wind_flags = [isinstance(point, dict) and point.get("wind_a") is not None for point in points.values()]
        if any(wind_flags) and not all(wind_flags):
            issues.append(ValidationIssue("mixed_winding_annotation", f"{collection_id}: some points lack wind_a"))
        if all(wind_flags):
            annotated += 1
        else:
            unannotated += 1
        for point_id, point in points.items():
            label = f"{collection_id}/{point_id}"
            if not isinstance(point, dict):
                issues.append(ValidationIssue("invalid_point", f"{label}: not an object"))
                continue
            position = point.get("p")
            if not isinstance(position, (list, tuple)) or len(position) != 3:
                issues.append(ValidationIssue("invalid_position", f"{label}: p must be [x,y,z]"))
                continue
            try:
                xyz = tuple(float(value) for value in position)
            except (TypeError, ValueError):
                issues.append(ValidationIssue("invalid_position", f"{label}: p is not numeric"))
                continue
            if not all(math.isfinite(value) for value in xyz):
                issues.append(ValidationIssue("invalid_position", f"{label}: p is not finite"))
            elif shape is not None and any(not (0 <= value < size) for value, size in zip(xyz, reversed(shape))):
                issues.append(ValidationIssue("position_out_of_bounds", f"{label}: outside volume shape {shape}"))
            if point.get("wind_a") is not None:
                try:
                    winding = float(point["wind_a"])
                    if not math.isfinite(winding):
                        raise ValueError("not finite")
                except (TypeError, ValueError):
                    issues.append(ValidationIssue("invalid_winding", f"{label}: wind_a must be finite numeric"))
    return PointCollectionAudit(len(collections), point_count, empty, annotated, unannotated, tuple(issues))
