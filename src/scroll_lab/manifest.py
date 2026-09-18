"""Portable manifest validation for cross-tool benchmark inputs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .contracts import ValidationIssue, validate_bbox, validate_shape, validate_spacing


@dataclass(frozen=True)
class AssetRecord:
    """The common metadata subset needed by benchmark adapters."""

    asset_id: str
    kind: str
    path: str
    shape: tuple[int, ...] | None = None
    spacing: tuple[float, ...] | None = None
    bbox: tuple[tuple[float, ...], tuple[float, ...]] | None = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "AssetRecord":
        missing = [key for key in ("id", "kind", "path") if key not in raw]
        if missing:
            raise ValueError(f"asset missing required fields: {missing}")
        shape = tuple(int(value) for value in raw["shape"]) if "shape" in raw else None
        spacing = tuple(float(value) for value in raw["spacing"]) if "spacing" in raw else None
        bbox = None
        if "bbox" in raw:
            bbox = (
                tuple(float(value) for value in raw["bbox"][0]),
                tuple(float(value) for value in raw["bbox"][1]),
            )
        return cls(str(raw["id"]), str(raw["kind"]), str(raw["path"]), shape, spacing, bbox)


def load_manifest(path: str | Path) -> Mapping[str, Any]:
    """Load JSON only; format-specific readers belong in adapters."""

    with Path(path).open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("manifest root must be a JSON object")
    return value


def validate_manifest(raw: Mapping[str, Any]) -> list[ValidationIssue]:
    """Validate structure and embedded metadata without opening large assets."""

    assets = raw.get("assets")
    if not isinstance(assets, list):
        return [ValidationIssue("assets_missing", "manifest must contain an assets list")]

    issues: list[ValidationIssue] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(assets):
        if not isinstance(item, dict):
            issues.append(ValidationIssue("asset_type", f"asset {index} is not an object"))
            continue
        try:
            asset = AssetRecord.from_mapping(item)
        except (TypeError, ValueError, IndexError) as exc:
            issues.append(ValidationIssue("asset_fields", f"asset {index}: {exc}"))
            continue
        if asset.asset_id in seen_ids:
            issues.append(ValidationIssue("duplicate_asset_id", asset.asset_id))
        seen_ids.add(asset.asset_id)
        if asset.shape is not None:
            issues.extend(_prefix(asset.asset_id, validate_shape(asset.shape)))
        if asset.spacing is not None:
            issues.extend(_prefix(asset.asset_id, validate_spacing(asset.spacing)))
        if asset.bbox is not None:
            issues.extend(_prefix(asset.asset_id, validate_bbox([], asset.bbox)))
    return issues


def _prefix(asset_id: str, issues: list[ValidationIssue]) -> list[ValidationIssue]:
    return [ValidationIssue(issue.code, f"{asset_id}: {issue.message}", issue.severity) for issue in issues]

