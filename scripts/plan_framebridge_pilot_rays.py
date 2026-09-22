#!/usr/bin/env python3
"""Build the frozen FB03 pilot pairs and plan their seven-ray field bricks."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GAUGE_ROOT = ROOT / "data" / "external" / "constraint-gauge"
sys.path.insert(0, str(GAUGE_ROOT))

from gauge.gt import build_pairs  # noqa: E402
from gauge.meshgt import load_mesh_gt  # noqa: E402

from scroll_lab.ray_support import e1_multiray_bricks, rows_for_bricks  # noqa: E402
from scroll_lab.respool import RespoolIndex, byte_ranges_for_rows  # noqa: E402


def _sha256(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh-dir", type=Path, required=True)
    parser.add_argument("--meta", type=Path, required=True)
    parser.add_argument("--coords", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--channel-url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mesh-stride", type=int, default=10)
    parser.add_argument("--max-pairs", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    if args.mesh_stride < 1 or args.max_pairs < 1:
        raise ValueError("mesh stride and max pairs must be positive")

    required_mesh_files = [args.mesh_dir / name for name in ("meta.json", "x.tif", "y.tif", "z.tif")]
    missing = [str(path) for path in required_mesh_files if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing pilot mesh inputs: {missing}")

    index = RespoolIndex.load(args.meta, args.coords, args.table)
    mesh_xyz, winding, collection, mesh_info = load_mesh_gt(
        str(args.mesh_dir), stride=args.mesh_stride
    )
    pairs = build_pairs(
        mesh_xyz,
        winding,
        collection,
        max_pairs=args.max_pairs,
        seed=args.seed,
    )
    working_xyz = mesh_xyz / 4.0

    requested_bricks: set[tuple[int, int, int]] = set()
    corrected_histogram: Counter[int] = Counter()
    wrong_frame_histogram: Counter[int] = Counter()
    pair_count = len(pairs["dw"])
    for ordinal, (a_index, b_index) in enumerate(zip(pairs["a"], pairs["b"])):
        pair_bricks, valid_rays = e1_multiray_bricks(
            working_xyz[a_index],
            working_xyz[b_index],
            array_shape_zyx=index.array_shape,
            brick_shape_zyx=index.brick_shape,
            grid_shape_zyx=index.grid_shape,
        )
        requested_bricks.update(pair_bricks)
        corrected_histogram[valid_rays] += 1

        # Historical control: feed 2.4 um mesh indexes directly to E1 as if
        # they were 9.6 um working indexes. Only count support; no data read.
        _, wrong_valid = e1_multiray_bricks(
            mesh_xyz[a_index],
            mesh_xyz[b_index],
            array_shape_zyx=index.array_shape,
            brick_shape_zyx=index.brick_shape,
            grid_shape_zyx=index.grid_shape,
        )
        wrong_frame_histogram[wrong_valid] += 1
        if (ordinal + 1) % 2000 == 0:
            print(
                f"planned {ordinal + 1:,}/{pair_count:,} pairs; "
                f"{len(requested_bricks):,} logical bricks",
                flush=True,
            )

    occupied_rows = rows_for_bricks(index.table, requested_bricks)
    ranges = byte_ranges_for_rows(occupied_rows, index.brick_voxels)
    absent = len(requested_bricks) - len(occupied_rows)
    result = {
        "schema_version": 1,
        "kind": "framebridge_e1_pilot_ray_plan",
        "channel_url": args.channel_url,
        "mesh": {
            "path": str(args.mesh_dir),
            "files": [
                {"path": str(path), "bytes": path.stat().st_size, "sha256": _sha256(path)}
                for path in required_mesh_files
            ],
            "load_info": mesh_info,
            "points": int(len(mesh_xyz)),
            "measured_bounds_xyz_2p4": [mesh_xyz.min(axis=0).tolist(), mesh_xyz.max(axis=0).tolist()],
        },
        "pair_protocol": {
            "implementation": "pinned constraint-gauge gauge.meshgt.load_mesh_gt + gauge.gt.build_pairs",
            "mesh_stride": args.mesh_stride,
            "max_pairs": args.max_pairs,
            "seed": args.seed,
            "pairs": pair_count,
            "dw_histogram": {
                str(int(value)): int(count)
                for value, count in zip(*np.unique(pairs["dw"], return_counts=True))
            },
        },
        "frame_contract": {
            "mesh_xyz_to_e1_working_xyz": "divide each coordinate by 4",
            "e1_working_xyz_to_grad_mag_group4_zyx": "divide by 4 then reverse axis order",
            "combined_mesh_xyz_to_grad_mag_group4_zyx": "divide by 16 then reverse axis order",
            "frozen_multiray": {"rays": 7, "max_offset_working_voxels": 6.0},
            "trilinear_halo_field_voxels": 1.0,
        },
        "support_controls": {
            "wrong_frame_valid_ray_histogram": dict(sorted(wrong_frame_histogram.items())),
            "corrected_frame_valid_ray_histogram": dict(sorted(corrected_histogram.items())),
            "wrong_frame_pairs_with_any_valid_ray": int(
                sum(count for rays, count in wrong_frame_histogram.items() if rays > 0)
            ),
            "corrected_pairs_with_any_valid_ray": int(
                sum(count for rays, count in corrected_histogram.items() if rays > 0)
            ),
            "corrected_pairs_with_all_seven_rays": int(corrected_histogram.get(7, 0)),
        },
        "acquisition": {
            "logical_bricks_requested": len(requested_bricks),
            "occupied_rows_requested": len(occupied_rows),
            "absent_zero_bricks": absent,
            "payload_bytes": len(occupied_rows) * index.brick_voxels,
            "full_channel_bytes": index.channel_file_bytes,
            "payload_fraction_of_full": (
                len(occupied_rows) * index.brick_voxels / index.channel_file_bytes
            ),
            "range_count": len(ranges),
            "ranges": [item.to_dict() for item in ranges],
        },
        "semantics": [
            "Ray bricks conservatively cover each continuous valid ray plus a one-field-voxel interpolation halo.",
            "Absent logical bricks are reconstructed as zeros under the official respool v2 contract.",
            "This is an allocation/acquisition proof, not an E1 accuracy result.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "points": len(mesh_xyz),
        "pairs": pair_count,
        "wrong_frame_any_valid": result["support_controls"]["wrong_frame_pairs_with_any_valid_ray"],
        "corrected_any_valid": result["support_controls"]["corrected_pairs_with_any_valid_ray"],
        "corrected_all_seven": result["support_controls"]["corrected_pairs_with_all_seven_rays"],
        "logical_bricks": len(requested_bricks),
        "occupied_rows": len(occupied_rows),
        "payload_bytes": result["acquisition"]["payload_bytes"],
        "ranges": len(ranges),
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
