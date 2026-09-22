"""Manifest-driven, metadata-only coordinate support probes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .frames import Bounds3D, FrameSpec, bounds_from_points, physical_axis_overlap, physical_overlap


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_object(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _pointcollection_points(path: Path) -> list[tuple[float, float, float]]:
    raw = _read_object(path)
    collections = raw.get("collections")
    if not isinstance(collections, dict):
        raise ValueError(f"{path}: collections must be an object")
    points: list[tuple[float, float, float]] = []
    for collection_id, collection in collections.items():
        if not isinstance(collection, dict) or not isinstance(collection.get("points"), dict):
            raise ValueError(f"{path}: collection {collection_id!r} has invalid points")
        for point_id, point in collection["points"].items():
            position = point.get("p") if isinstance(point, dict) else None
            if not isinstance(position, (list, tuple)) or len(position) != 3:
                raise ValueError(f"{path}: point {collection_id}/{point_id} lacks [x,y,z] p")
            xyz = tuple(float(value) for value in position)
            points.append(xyz)  # type: ignore[arg-type]
    return points


def _umbilicus_points(path: Path) -> list[tuple[float, float, float]]:
    raw = _read_object(path)
    controls = raw.get("control_points")
    if not isinstance(controls, list) or not controls:
        raise ValueError(f"{path}: control_points must be a nonempty list")
    points = []
    for index, point in enumerate(controls):
        if not isinstance(point, dict) or any(axis not in point for axis in ("x", "y", "z")):
            raise ValueError(f"{path}: control point {index} lacks x/y/z")
        points.append(tuple(float(point[axis]) for axis in ("x", "y", "z")))
    return points  # type: ignore[return-value]


def _intervals_from_bounds(frame: FrameSpec, bounds: Bounds3D) -> dict[str, list[float]]:
    return {
        axis: [bounds.lower[index], bounds.upper[index]]
        for index, axis in enumerate(frame.axis_order)
    }


def _bounds_from_intervals(frame: FrameSpec, intervals: Mapping[str, list[float]]) -> Bounds3D | None:
    if any(axis not in intervals for axis in ("x", "y", "z")):
        return None
    return Bounds3D(
        tuple(intervals[axis][0] for axis in frame.axis_order),
        tuple(intervals[axis][1] for axis in frame.axis_order),
    )  # type: ignore[arg-type]


def _merge_intervals(
    existing: dict[str, list[float]],
    measured: Mapping[str, list[float]],
) -> None:
    for axis, interval in measured.items():
        if axis in existing:
            existing[axis] = [
                min(existing[axis][0], interval[0]),
                max(existing[axis][1], interval[1]),
            ]
        else:
            existing[axis] = list(interval)


def run_frame_probe(raw: Mapping[str, Any], *, manifest_dir: str | Path) -> dict[str, Any]:
    if raw.get("schema_version") != 1:
        raise ValueError("frame probe schema_version must be 1")
    frames_raw = raw.get("frames")
    artifacts_raw = raw.get("artifacts")
    comparisons_raw = raw.get("comparisons")
    if not isinstance(frames_raw, dict) or not frames_raw:
        raise ValueError("frames must be a nonempty object")
    if not isinstance(artifacts_raw, list) or not artifacts_raw:
        raise ValueError("artifacts must be a nonempty list")
    if not isinstance(comparisons_raw, list) or not comparisons_raw:
        raise ValueError("comparisons must be a nonempty list")

    frames = {frame_id: FrameSpec.from_dict(spec) for frame_id, spec in frames_raw.items()}
    root = Path(manifest_dir) / str(raw.get("base_dir", "."))
    root = root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}

    for item in artifacts_raw:
        if not isinstance(item, dict):
            raise ValueError("each artifact must be an object")
        artifact_id = str(item.get("id", ""))
        if not artifact_id or artifact_id in artifacts:
            raise ValueError(f"artifact id is empty or duplicated: {artifact_id!r}")
        frame_id = str(item.get("frame", ""))
        if frame_id not in frames:
            raise ValueError(f"artifact {artifact_id}: unknown frame {frame_id!r}")
        frame = frames[frame_id]
        intervals: dict[str, list[float]] = {}
        sources: list[dict[str, Any]] = []
        point_count = 0

        declared = item.get("axis_intervals")
        if declared is not None:
            if not isinstance(declared, dict):
                raise ValueError(f"artifact {artifact_id}: axis_intervals must be an object")
            for axis, interval in declared.items():
                if axis not in ("x", "y", "z") or not isinstance(interval, list) or len(interval) != 2:
                    raise ValueError(f"artifact {artifact_id}: invalid {axis!r} interval")
                lo, hi = float(interval[0]), float(interval[1])
                if lo > hi:
                    raise ValueError(f"artifact {artifact_id}: interval {axis} is reversed")
                intervals[axis] = [lo, hi]

        files = item.get("pointcollections", [])
        if not isinstance(files, list):
            raise ValueError(f"artifact {artifact_id}: pointcollections must be a list")
        if files:
            if frame.axis_order != ("x", "y", "z"):
                raise ValueError(
                    f"artifact {artifact_id}: VC3D pointcollections are xyz but frame is {frame.axis_order}"
                )
            all_points: list[tuple[float, float, float]] = []
            for relative in files:
                path = (root / str(relative)).resolve()
                if not path.is_relative_to(root):
                    raise ValueError(f"artifact {artifact_id}: path escapes base_dir: {relative}")
                points = _pointcollection_points(path)
                all_points.extend(points)
                sources.append({
                    "path": str(path),
                    "sha256": sha256_file(path),
                    "point_count": len(points),
                })
            bounds = bounds_from_points(all_points)
            measured = _intervals_from_bounds(frame, bounds)
            for axis, interval in measured.items():
                if axis in intervals and intervals[axis] != interval:
                    raise ValueError(
                        f"artifact {artifact_id}: declared {axis} interval disagrees with measured points"
                    )
                intervals[axis] = interval
            point_count = len(all_points)

        umbilicus_files = item.get("umbilicus_json", [])
        if isinstance(umbilicus_files, str):
            umbilicus_files = [umbilicus_files]
        if not isinstance(umbilicus_files, list):
            raise ValueError(f"artifact {artifact_id}: umbilicus_json must be a path or list")
        if umbilicus_files:
            if frame.axis_order != ("x", "y", "z"):
                raise ValueError(f"artifact {artifact_id}: umbilicus controls are xyz")
            all_points = []
            for relative in umbilicus_files:
                path = (root / str(relative)).resolve()
                if not path.is_relative_to(root):
                    raise ValueError(f"artifact {artifact_id}: path escapes base_dir: {relative}")
                points = _umbilicus_points(path)
                all_points.extend(points)
                sources.append({
                    "path": str(path), "sha256": sha256_file(path),
                    "control_point_count": len(points),
                })
            _merge_intervals(intervals, _intervals_from_bounds(frame, bounds_from_points(all_points)))
            point_count += len(all_points)

        meta_files = item.get("tifxyz_metadata", [])
        if isinstance(meta_files, str):
            meta_files = [meta_files]
        if not isinstance(meta_files, list):
            raise ValueError(f"artifact {artifact_id}: tifxyz_metadata must be a path or list")
        if meta_files:
            if frame.axis_order != ("x", "y", "z"):
                raise ValueError(f"artifact {artifact_id}: TIFXYZ bboxes are xyz")
            for relative in meta_files:
                path = (root / str(relative)).resolve()
                if not path.is_relative_to(root):
                    raise ValueError(f"artifact {artifact_id}: path escapes base_dir: {relative}")
                meta = _read_object(path)
                bbox = meta.get("bbox")
                if not isinstance(bbox, list) or len(bbox) != 2:
                    raise ValueError(f"{path}: bbox must contain lower and upper xyz")
                bounds = Bounds3D(tuple(bbox[0]), tuple(bbox[1]))
                _merge_intervals(intervals, _intervals_from_bounds(frame, bounds))
                sources.append({"path": str(path), "sha256": sha256_file(path)})

        array_meta = item.get("array_metadata")
        if array_meta is not None:
            path = (root / str(array_meta)).resolve()
            if not path.is_relative_to(root):
                raise ValueError(f"artifact {artifact_id}: path escapes base_dir: {array_meta}")
            meta = _read_object(path)
            shape = meta.get("array_shape")
            if not isinstance(shape, list) or len(shape) != 3 or any(type(v) is not int or v <= 0 for v in shape):
                raise ValueError(f"{path}: array_shape must contain three positive integers")
            bounds = Bounds3D((0.0, 0.0, 0.0), tuple(float(v - 1) for v in shape))
            _merge_intervals(intervals, _intervals_from_bounds(frame, bounds))
            sources.append({
                "path": str(path), "sha256": sha256_file(path),
                "array_shape": shape, "format": meta.get("format"),
            })

        if not intervals:
            raise ValueError(f"artifact {artifact_id}: no measured or declared support")
        artifacts[artifact_id] = {
            "id": artifact_id,
            "frame": frame_id,
            "axis_intervals_native": intervals,
            "point_count": point_count,
            "sources": sources,
            "evidence": str(item.get("evidence", "")),
        }

    comparisons: list[dict[str, Any]] = []
    for item in comparisons_raw:
        if not isinstance(item, dict):
            raise ValueError("each comparison must be an object")
        comparison_id = str(item.get("id", ""))
        a_id, b_id = str(item.get("a", "")), str(item.get("b", ""))
        axis = str(item.get("axis", ""))
        mode = str(item.get("mode", "axis"))
        if not comparison_id:
            raise ValueError("comparison id cannot be empty")
        if a_id not in artifacts or b_id not in artifacts:
            raise ValueError(f"comparison {comparison_id}: unknown artifact")
        a, b = artifacts[a_id], artifacts[b_id]
        if mode == "axis":
            if axis not in a["axis_intervals_native"] or axis not in b["axis_intervals_native"]:
                raise ValueError(f"comparison {comparison_id}: axis {axis!r} is unavailable")
            result = physical_axis_overlap(
                frames[a["frame"]], a["axis_intervals_native"][axis],
                frames[b["frame"]], b["axis_intervals_native"][axis],
                canonical_axis=axis,
            )
        elif mode == "bounds3d":
            a_bounds = _bounds_from_intervals(frames[a["frame"]], a["axis_intervals_native"])
            b_bounds = _bounds_from_intervals(frames[b["frame"]], b["axis_intervals_native"])
            if a_bounds is None or b_bounds is None:
                raise ValueError(f"comparison {comparison_id}: full xyz bounds are unavailable")
            result = physical_overlap(frames[a["frame"]], a_bounds, frames[b["frame"]], b_bounds)
        else:
            raise ValueError(f"comparison {comparison_id}: unknown mode {mode!r}")
        comparisons.append({
            "id": comparison_id,
            "mode": mode,
            "a": a_id,
            "b": b_id,
            "expected_overlap": item.get("expected_overlap"),
            "expectation_met": (
                result["overlap"] == item["expected_overlap"]
                if isinstance(item.get("expected_overlap"), bool) else None
            ),
            **result,
        })

    return {
        "schema_version": 1,
        "description": str(raw.get("description", "")),
        "frames": {frame_id: frame.to_dict() for frame_id, frame in frames.items()},
        "artifacts": list(artifacts.values()),
        "comparisons": comparisons,
        "all_expectations_met": all(
            item["expectation_met"] is not False for item in comparisons
        ),
        "limitations": list(raw.get("limitations", [])),
    }
