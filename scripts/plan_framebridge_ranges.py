#!/usr/bin/env python3
"""Plan exact grad_mag HTTP ranges for the Paris 4 benchmark meshes.

This is deliberately a planning command: it validates the public resident-
pool indexes and writes a machine-readable acquisition plan, but downloads no
channel payload.  Mesh metadata uses xyz coordinates on the 2.4 um scan.  E1
works on the 9.6 um grid and samples grad_mag group 4, so one field voxel is
16 mesh voxels.  The frozen seven-ray envelope adds +/-6 E1 voxels in x/y,
equivalent to +/-1.5 group-4 voxels, plus a trilinear interpolation halo.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scroll_lab.respool import RespoolIndex, sampling_roi_from_closed_bounds, union_rois


MESH_TO_FIELD = 1.0 / 16.0
E1_MAX_OFFSET_FIELD_VOXELS = 6.0 / 4.0


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mesh_roi(path: Path, array_shape: tuple[int, int, int]):
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    bbox = data.get("bbox")
    if not isinstance(bbox, list) or len(bbox) != 2 or any(
        not isinstance(row, list) or len(row) != 3 for row in bbox
    ):
        raise ValueError(f"{path}: bbox must be [[x,y,z],[x,y,z]]")
    lower_xyz = [float(v) * MESH_TO_FIELD for v in bbox[0]]
    upper_xyz = [float(v) * MESH_TO_FIELD for v in bbox[1]]
    lower_zyx = tuple(reversed(lower_xyz))
    upper_zyx = tuple(reversed(upper_xyz))
    padding_zyx = (0.0, E1_MAX_OFFSET_FIELD_VOXELS, E1_MAX_OFFSET_FIELD_VOXELS)
    return sampling_roi_from_closed_bounds(
        lower_zyx,
        upper_zyx,
        array_shape=array_shape,
        padding_zyx=padding_zyx,
        interpolation_halo=1,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--meta", type=Path, required=True)
    parser.add_argument("--coords", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--mesh-meta", type=Path, action="append", required=True)
    parser.add_argument("--channel-url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    index = RespoolIndex.load(args.meta, args.coords, args.table)
    mesh_records = []
    rois = []
    for mesh_path in args.mesh_meta:
        roi = _mesh_roi(mesh_path, index.array_shape)
        rois.append(roi)
        plan = index.plan(*roi)
        mesh_records.append(
            {
                "id": mesh_path.parent.name,
                "metadata_path": str(mesh_path),
                "metadata_sha256": _sha256(mesh_path),
                "plan": plan.to_dict(),
            }
        )

    union_roi = union_rois(rois)
    union_plan = index.plan(*union_roi)
    output = {
        "schema_version": 1,
        "kind": "framebridge_respool_range_plan",
        "channel_url": args.channel_url,
        "source": {
            "meta": {"path": str(args.meta), "sha256": _sha256(args.meta)},
            "coords": {"path": str(args.coords), "sha256": _sha256(args.coords)},
            "table": {"path": str(args.table), "sha256": _sha256(args.table)},
        },
        "format_validation": {
            "format": index.meta["format"],
            "version": index.meta["version"],
            "array_shape_zyx": list(index.array_shape),
            "brick_shape_zyx": list(index.brick_shape),
            "grid_shape_zyx": list(index.grid_shape),
            "rows_including_zero": index.rows,
            "brick_bytes": index.brick_voxels,
            "channel_file_bytes": index.channel_file_bytes,
            "table_coords_exact_inverse": True,
        },
        "coordinate_contract": {
            "mesh_frame": "xyz at 2.4 um/voxel",
            "e1_frame": "xyz at 9.6 um/voxel",
            "grad_mag_frame": "zyx group 4 at 38.4 um/voxel",
            "mesh_to_grad_mag_scale": MESH_TO_FIELD,
            "frozen_e1_max_offset_voxels": 6.0,
            "max_offset_grad_mag_voxels_xy": E1_MAX_OFFSET_FIELD_VOXELS,
            "interpolation_halo_voxels": 1,
        },
        "semantics": {
            "ranges_are_inclusive": True,
            "omitted_logical_bricks": "defined by respool v2 as all-zero; do not download",
            "occupied_does_not_mean_all_voxels_nonzero": True,
            "bbox_plan_is_conservative": True,
        },
        "meshes": mesh_records,
        "union": union_plan.to_dict(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "meshes": len(mesh_records),
        "occupied_bricks": union_plan.occupied_bricks,
        "logical_bricks": union_plan.logical_bricks,
        "payload_bytes": union_plan.payload_bytes,
        "range_count": len(union_plan.ranges),
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
