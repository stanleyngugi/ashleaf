#!/usr/bin/env python3
"""Plan one exact sparse-respool acquisition for frozen local pairs on all meshes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GAUGE_ROOT = ROOT / "data" / "external" / "constraint-gauge"
sys.path.insert(0, str(GAUGE_ROOT))

from scroll_lab.local_mesh_pairs import build_local_adjacent_pairs  # noqa: E402
from scroll_lab.ray_support import e1_multiray_bricks, rows_for_bricks  # noqa: E402
from scroll_lab.respool import (  # noqa: E402
    RespoolIndex,
    byte_ranges_for_rows,
    coalesce_byte_ranges,
)
from scroll_lab.sparse_e1 import load_umbilicus_axis  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--meshes-root", type=Path, required=True)
    parser.add_argument("--umbilicus", type=Path, required=True)
    parser.add_argument("--meta", type=Path, required=True)
    parser.add_argument("--coords", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--channel-url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pairs-cache-dir", type=Path, required=True)
    parser.add_argument("--stride-v", type=int, default=10)
    parser.add_argument("--stride-u", type=int, default=10)
    parser.add_argument("--max-pairs", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--merge-gap-rows", type=int, default=16)
    args = parser.parse_args()

    mesh_dirs = sorted(path for path in args.meshes_root.iterdir() if path.is_dir())
    if not mesh_dirs:
        raise ValueError(f"no mesh directories found under {args.meshes_root}")
    axis, _ = load_umbilicus_axis(args.umbilicus)
    index = RespoolIndex.load(args.meta, args.coords, args.table)
    args.pairs_cache_dir.mkdir(parents=True, exist_ok=True)
    union_bricks: set[tuple[int, int, int]] = set()
    mesh_summaries: dict[str, object] = {}
    for mesh_dir in mesh_dirs:
        try:
            points, pairs, pair_info = build_local_adjacent_pairs(
                mesh_dir,
                axis,
                constraint_gauge_root=GAUGE_ROOT,
                stride_v=args.stride_v,
                stride_u=args.stride_u,
                max_pairs=args.max_pairs,
                seed=args.seed,
            )
        except ValueError as error:
            if not str(error).startswith("only "):
                raise
            mesh_summaries[mesh_dir.name] = {
                "status": "ineligible_frozen_protocol",
                "reason": str(error),
            }
            print(f"{mesh_dir.name}: ineligible ({error})", flush=True)
            continue
        mesh_bricks: set[tuple[int, int, int]] = set()
        valid_histogram: dict[int, int] = {}
        for ordinal, (a_index, b_index) in enumerate(zip(pairs["a"], pairs["b"])):
            pair_bricks, valid = e1_multiray_bricks(
                points[a_index],
                points[b_index],
                array_shape_zyx=index.array_shape,
                brick_shape_zyx=index.brick_shape,
                grid_shape_zyx=index.grid_shape,
            )
            mesh_bricks.update(pair_bricks)
            valid_histogram[valid] = valid_histogram.get(valid, 0) + 1
            if (ordinal + 1) % 5000 == 0:
                print(
                    f"{mesh_dir.name}: planned {ordinal + 1:,} pairs; "
                    f"{len(mesh_bricks):,} bricks",
                    flush=True,
                )
        mesh_rows = rows_for_bricks(index.table, mesh_bricks)
        union_bricks.update(mesh_bricks)
        cache_path = args.pairs_cache_dir / f"{mesh_dir.name}.npz"
        np.savez_compressed(
            cache_path,
            points=points,
            a=pairs["a"],
            b=pairs["b"],
            dw=pairs["dw"],
        )
        cache_sha256 = hashlib.sha256(cache_path.read_bytes()).hexdigest()
        mesh_summaries[mesh_dir.name] = {
            "status": "eligible",
            "pair_cache_path": str(cache_path),
            "pair_cache_bytes": cache_path.stat().st_size,
            "pair_cache_sha256": cache_sha256,
            "pair_protocol": pair_info,
            "valid_ray_histogram": dict(sorted(valid_histogram.items())),
            "pairs": len(pairs["dw"]),
            "logical_bricks_requested": len(mesh_bricks),
            "occupied_rows_requested": len(mesh_rows),
            "absent_zero_bricks": len(mesh_bricks) - len(mesh_rows),
        }
        print(
            f"{mesh_dir.name}: {len(mesh_bricks):,} logical bricks; "
            f"union now {len(union_bricks):,}",
            flush=True,
        )

    rows = rows_for_bricks(index.table, union_bricks)
    exact_ranges = byte_ranges_for_rows(rows, index.brick_voxels)
    ranges = coalesce_byte_ranges(
        exact_ranges, index.brick_voxels, max_gap_rows=args.merge_gap_rows
    )
    acquired_rows = sum(item.row_end - item.row_start + 1 for item in ranges)
    output = {
        "schema_version": 1,
        "kind": "framebridge_e1_all_mesh_local_ray_plan",
        "channel_url": args.channel_url,
        "frozen_protocol": {
            "name": "adjacent-wrap same-row nearest correspondence",
            "stride_v": args.stride_v,
            "stride_u": args.stride_u,
            "trim_wraps": 1,
            "max_pairs_per_mesh": args.max_pairs,
            "seed": args.seed,
        },
        "meshes": mesh_summaries,
        "acquisition": {
            "logical_bricks_requested": len(union_bricks),
            "occupied_rows_requested": len(rows),
            "absent_zero_bricks": len(union_bricks) - len(rows),
            "exact_occupied_rows_requested": len(rows),
            "acquired_rows_including_request_coalescing": acquired_rows,
            "extra_rows_from_request_coalescing": acquired_rows - len(rows),
            "merge_gap_rows": args.merge_gap_rows,
            "exact_range_count_before_coalescing": len(exact_ranges),
            "payload_bytes": acquired_rows * index.brick_voxels,
            "full_channel_bytes": index.channel_file_bytes,
            "payload_fraction_of_full": acquired_rows * index.brick_voxels / index.channel_file_bytes,
            "range_count": len(ranges),
            "ranges": [item.to_dict() for item in ranges],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "meshes": len(mesh_summaries),
        "eligible_meshes": sum(item.get("status") == "eligible" for item in mesh_summaries.values()),
        "pairs": sum(int(item.get("pairs", 0)) for item in mesh_summaries.values()),
        "logical_bricks": len(union_bricks),
        "occupied_rows": len(rows),
        "payload_bytes": output["acquisition"]["payload_bytes"],
        "range_count": len(ranges),
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
