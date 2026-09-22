#!/usr/bin/env python3
"""Coalesce small gaps in an existing FrameBridge HTTP range plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scroll_lab.respool import ByteRange, coalesce_byte_ranges


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--merge-gap-rows", type=int, default=16)
    parser.add_argument("--brick-bytes", type=int, default=32_768)
    args = parser.parse_args()
    plan = json.loads(args.input.read_text(encoding="utf-8"))
    raw = plan["acquisition"]["ranges"]
    exact = tuple(ByteRange(
        row_start=int(item["row_start"]),
        row_end=int(item["row_end"]),
        byte_start=int(item["byte_start"]),
        byte_end=int(item["byte_end"]),
    ) for item in raw)
    merged = coalesce_byte_ranges(
        exact, args.brick_bytes, max_gap_rows=args.merge_gap_rows
    )
    exact_rows = int(plan["acquisition"]["occupied_rows_requested"])
    acquired_rows = sum(item.row_end - item.row_start + 1 for item in merged)
    plan["acquisition"].update({
        "exact_occupied_rows_requested": exact_rows,
        "acquired_rows_including_request_coalescing": acquired_rows,
        "extra_rows_from_request_coalescing": acquired_rows - exact_rows,
        "merge_gap_rows": args.merge_gap_rows,
        "exact_range_count_before_coalescing": len(exact),
        "payload_bytes": acquired_rows * args.brick_bytes,
        "payload_fraction_of_full": acquired_rows * args.brick_bytes
        / int(plan["acquisition"]["full_channel_bytes"]),
        "range_count": len(merged),
        "ranges": [item.to_dict() for item in merged],
    })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "exact_ranges": len(exact),
        "coalesced_ranges": len(merged),
        "exact_rows": exact_rows,
        "acquired_rows": acquired_rows,
        "payload_bytes": acquired_rows * args.brick_bytes,
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
