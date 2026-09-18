"""Read and audit TIFXYZ directories without loading their large image planes.

The metadata audit uses only the Python standard library.  A later pixel scan
can use tifffile to compare actual valid vertices with the cached bbox.
"""

from __future__ import annotations

import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import ValidationIssue, validate_bbox, validate_spacing


@dataclass(frozen=True)
class TiffHeader:
    width: int
    height: int
    samples_per_pixel: int


@dataclass(frozen=True)
class TifxyzAudit:
    path: str
    width: int | None
    height: int | None
    metadata: dict[str, Any]
    issues: tuple[ValidationIssue, ...]
    stats: dict[str, Any] | None = None

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


def read_tiff_header(path: str | Path) -> TiffHeader:
    """Read the first TIFF IFD's dimensions, including BigTIFF headers."""

    with Path(path).open("rb") as handle:
        byte_order = handle.read(2)
        if byte_order not in (b"II", b"MM"):
            raise ValueError("not a TIFF file: invalid byte order marker")
        endian = "<" if byte_order == b"II" else ">"
        magic = struct.unpack(endian + "H", _read_exact(handle, 2))[0]
        if magic == 42:
            offset = struct.unpack(endian + "I", _read_exact(handle, 4))[0]
            count_bytes, entry_bytes, value_bytes = 2, 12, 4
        elif magic == 43:
            offset_size, reserved = struct.unpack(endian + "HH", _read_exact(handle, 4))
            if offset_size != 8 or reserved != 0:
                raise ValueError("unsupported BigTIFF header")
            offset = struct.unpack(endian + "Q", _read_exact(handle, 8))[0]
            count_bytes, entry_bytes, value_bytes = 8, 20, 8
        else:
            raise ValueError(f"not a TIFF file: magic={magic}")

        handle.seek(offset)
        count = struct.unpack(endian + ("H" if count_bytes == 2 else "Q"), _read_exact(handle, count_bytes))[0]
        if count > 100_000:
            raise ValueError("unreasonable TIFF tag count")
        values: dict[int, int] = {}
        for _ in range(count):
            entry = _read_exact(handle, entry_bytes)
            tag, dtype = struct.unpack(endian + "HH", entry[:4])
            item_count = struct.unpack(endian + ("I" if value_bytes == 4 else "Q"), entry[4 : 4 + value_bytes])[0]
            if tag not in (256, 257, 277) or item_count != 1:
                continue
            value_field = entry[-value_bytes:]
            type_format = {3: "H", 4: "I", 16: "Q"}.get(dtype)
            if type_format is None:
                raise ValueError(f"unsupported TIFF type {dtype} for tag {tag}")
            if struct.calcsize(type_format) > value_bytes:
                raise ValueError(f"TIFF tag {tag} value does not fit inline")
            values[tag] = struct.unpack(endian + type_format, value_field[: struct.calcsize(type_format)])[0]
        if 256 not in values or 257 not in values:
            raise ValueError("TIFF is missing width or height")
        if values[256] <= 0 or values[257] <= 0:
            raise ValueError("TIFF width and height must be positive")
        return TiffHeader(values[256], values[257], values.get(277, 1))


def _read_exact(handle: Any, size: int) -> bytes:
    data = handle.read(size)
    if len(data) != size:
        raise ValueError("truncated TIFF header or IFD")
    return data


def audit_tifxyz(
    path: str | Path,
    *,
    scan_pixels: bool = False,
    max_pixels: int = 20_000_000,
) -> TifxyzAudit:
    """Check a TIFXYZ directory's structure and cheap metadata invariants."""

    directory = Path(path)
    issues: list[ValidationIssue] = []
    metadata: dict[str, Any] = {}
    width: int | None = None
    height: int | None = None
    stats: dict[str, Any] = {}
    metadata_loaded = False

    if not directory.is_dir():
        return TifxyzAudit(str(directory), None, None, {}, (ValidationIssue("not_directory", str(directory)),))
    metadata_path = directory / "meta.json"
    if not metadata_path.is_file():
        issues.append(ValidationIssue("missing_metadata", "meta.json is missing"))
    else:
        try:
            raw = json.loads(metadata_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("metadata root must be an object")
            metadata = raw
            metadata_loaded = True
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            issues.append(ValidationIssue("invalid_metadata", str(exc)))

    if metadata_loaded:
        if metadata.get("format") != "tifxyz":
            issues.append(ValidationIssue("invalid_format", "meta.json format must be tifxyz"))
        if "scale" not in metadata:
            issues.append(ValidationIssue("missing_scale", "meta.json scale is missing"))
        else:
            scale = metadata["scale"]
            if not isinstance(scale, (list, tuple)) or len(scale) != 2:
                issues.append(ValidationIssue("invalid_scale", "scale must contain exactly two numbers"))
            else:
                issues.extend(validate_spacing(scale))
        if "bbox" in metadata:
            issues.extend(validate_bbox([], metadata["bbox"]))

    headers: dict[str, TiffHeader] = {}
    for axis in ("x", "y", "z"):
        image = directory / f"{axis}.tif"
        if not image.is_file():
            issues.append(ValidationIssue("missing_coordinate", f"{axis}.tif is missing"))
            continue
        try:
            header = read_tiff_header(image)
            headers[axis] = header
            if header.samples_per_pixel != 1:
                issues.append(ValidationIssue("multi_sample_coordinate", f"{axis}.tif has {header.samples_per_pixel} samples"))
        except (OSError, ValueError) as exc:
            issues.append(ValidationIssue("invalid_tiff", f"{axis}.tif: {exc}"))
    if headers:
        first = next(iter(headers.values()))
        width, height = first.width, first.height
        if any((header.width, header.height) != (width, height) for header in headers.values()):
            issues.append(ValidationIssue("coordinate_shape_mismatch", "x/y/z TIFF dimensions differ"))

    mask = directory / "mask.tif"
    if mask.is_file() and width is not None and height is not None:
        try:
            mask_header = read_tiff_header(mask)
            if (
                mask_header.width % width != 0
                or mask_header.height % height != 0
                or mask_header.width < width
                or mask_header.height < height
            ):
                issues.append(ValidationIssue("mask_shape_incompatible", "mask resolution is not an integer multiple of coordinate resolution"))
        except (OSError, ValueError) as exc:
            issues.append(ValidationIssue("invalid_mask_tiff", str(exc)))
    if scan_pixels and width is not None and height is not None and len(headers) == 3:
        if width * height > max_pixels:
            issues.append(ValidationIssue("pixel_scan_limit", f"{width * height} vertices exceed max_pixels={max_pixels}", "warning"))
        elif not any(issue.code == "coordinate_shape_mismatch" for issue in issues):
            pixel_issues, stats = _scan_vertices(directory, metadata, width, height)
            issues.extend(pixel_issues)
    return TifxyzAudit(str(directory), width, height, metadata, tuple(issues), stats)


def _scan_vertices(
    directory: Path,
    metadata: dict[str, Any],
    width: int,
    height: int,
) -> tuple[list[ValidationIssue], dict[str, Any]]:
    try:
        import numpy as np
        import tifffile
    except ImportError:
        return [ValidationIssue("missing_pixel_dependencies", "install the pixel extra: numpy and tifffile")], {}

    try:
        grids = [tifffile.imread(directory / f"{axis}.tif") for axis in "xyz"]
        if any(grid.shape != (height, width) for grid in grids):
            return [ValidationIssue("coordinate_shape_mismatch", "pixel arrays differ from TIFF header dimensions")], {}
        valid = np.isfinite(grids[2]) & (grids[2] > 0)
        mask_path = directory / "mask.tif"
        if mask_path.is_file():
            mask = tifffile.imread(mask_path)
            if mask.ndim == 3:
                mask = mask[..., 0]
            if mask.ndim != 2 or mask.shape[0] % height or mask.shape[1] % width:
                return [ValidationIssue("mask_shape_incompatible", "mask pixel shape cannot map to grid")], {}
            factor_y, factor_x = mask.shape[0] // height, mask.shape[1] // width
            valid &= (mask.reshape(height, factor_y, width, factor_x) >= 255).all(axis=(1, 3))
        count = int(np.count_nonzero(valid))
        if count == 0:
            return [ValidationIssue("empty_surface", "no valid vertices after mask and Z>0")], {"valid_vertices": 0}
        if not all(np.isfinite(grid[valid]).all() for grid in grids):
            return [ValidationIssue("nonfinite_vertex", "valid vertices contain nonfinite coordinates")], {"valid_vertices": count}
        actual_min = [float(np.min(grid[valid])) for grid in grids]
        actual_max = [float(np.max(grid[valid])) for grid in grids]
        stats = {"valid_vertices": count, "actual_bbox": [actual_min, actual_max]}
        issues = []
        if "bbox" in metadata:
            bbox_issues = validate_bbox((actual_min, actual_max), metadata["bbox"], tolerance=1e-3)
            if bbox_issues:
                issues.append(ValidationIssue("stale_bbox", "recorded bbox does not contain all valid vertices"))
        scale = metadata.get("scale")
        if isinstance(scale, (list, tuple)) and len(scale) == 2:
            for axis, step in ((0, _sample_neighbor_step(grids, valid, horizontal=True)),
                               (1, _sample_neighbor_step(grids, valid, horizontal=False))):
                if step is None:
                    continue
                stats[f"observed_step_{'u' if axis == 0 else 'v'}"] = step
                try:
                    expected_step = 1.0 / float(scale[axis])
                except (TypeError, ValueError, ZeroDivisionError):
                    continue
                ratio = step / expected_step
                if ratio > 8 or ratio < 1 / 8:
                    issues.append(ValidationIssue(
                        "scale_spacing_mismatch",
                        f"axis {axis}: observed adjacent-point step {step:.3g} vs 1/scale {expected_step:.3g}",
                        "warning",
                    ))
        return issues, stats
    except (OSError, ValueError, TypeError) as exc:
        return [ValidationIssue("pixel_scan_failed", str(exc))], {}


def _sample_neighbor_step(grids: list[Any], valid: Any, *, horizontal: bool) -> float | None:
    import numpy as np

    height, width = valid.shape
    row_stride = max(1, height // 256)
    col_stride = max(1, width // 256)
    if horizontal:
        left = (slice(None, None, row_stride), slice(0, width - 1, col_stride))
        right = (slice(None, None, row_stride), slice(1, width, col_stride))
    else:
        left = (slice(0, height - 1, row_stride), slice(None, None, col_stride))
        right = (slice(1, height, row_stride), slice(None, None, col_stride))
    paired = valid[left] & valid[right]
    if not np.any(paired):
        return None
    delta2 = sum((grid[left][paired].astype("float64") - grid[right][paired].astype("float64")) ** 2 for grid in grids)
    return float(np.median(np.sqrt(delta2)))
