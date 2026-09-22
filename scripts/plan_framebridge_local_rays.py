#!/usr/bin/env python3
"""Plan exact sparse rows for the preregistered FB05 local mesh pairs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
GAUGE_ROOT = ROOT / "data" / "external" / "constraint-gauge"
sys.path.insert(0, str(GAUGE_ROOT))

from scroll_lab.local_mesh_pairs import build_local_adjacent_pairs  # noqa: E402
from scroll_lab.ray_support import e1_multiray_bricks, rows_for_bricks  # noqa: E402
from scroll_lab.respool import RespoolIndex, byte_ranges_for_rows  # noqa: E402
from scroll_lab.sparse_e1 import load_umbilicus_axis  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh-dir", type=Path, required=True)
    parser.add_argument("--umbilicus", type=Path, required=True)
    parser.add_argument("--meta", type=Path, required=True)
    parser.add_argument("--coords", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--channel-url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    axis, _ = load_umbilicus_axis(args.umbilicus)
    points, pairs, pair_info = build_local_adjacent_pairs(
        args.mesh_dir, axis, constraint_gauge_root=GAUGE_ROOT
    )
    index = RespoolIndex.load(args.meta, args.coords, args.table)
    bricks = set()
    valid_histogram: dict[int, int] = {}
    for ordinal, (a_index, b_index) in enumerate(zip(pairs["a"], pairs["b"])):
        pair_bricks, valid = e1_multiray_bricks(
            points[a_index],
            points[b_index],
            array_shape_zyx=index.array_shape,
            brick_shape_zyx=index.brick_shape,
            grid_shape_zyx=index.grid_shape,
        )
        bricks.update(pair_bricks)
        valid_histogram[valid] = valid_histogram.get(valid, 0) + 1
        if (ordinal + 1) % 5000 == 0:
            print(f"planned {ordinal + 1:,} local pairs; {len(bricks):,} bricks", flush=True)
    rows = rows_for_bricks(index.table, bricks)
    ranges = byte_ranges_for_rows(rows, index.brick_voxels)
    output = {
        "schema_version": 1,
        "kind": "framebridge_e1_local_ray_plan",
        "channel_url": args.channel_url,
        "pair_protocol": pair_info,
        "support": {
            "valid_ray_histogram": dict(sorted(valid_histogram.items())),
            "pairs": len(pairs["dw"]),
        },
        "acquisition": {
            "logical_bricks_requested": len(bricks),
            "occupied_rows_requested": len(rows),
            "absent_zero_bricks": len(bricks) - len(rows),
            "payload_bytes": len(rows) * index.brick_voxels,
            "full_channel_bytes": index.channel_file_bytes,
            "payload_fraction_of_full": len(rows) * index.brick_voxels / index.channel_file_bytes,
            "range_count": len(ranges),
            "ranges": [item.to_dict() for item in ranges],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "pairs": len(pairs["dw"]),
        "logical_bricks": len(bricks),
        "occupied_rows": len(rows),
        "payload_bytes": output["acquisition"]["payload_bytes"],
        "ranges": len(ranges),
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
