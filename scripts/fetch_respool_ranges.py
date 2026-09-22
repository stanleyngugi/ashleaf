#!/usr/bin/env python3
"""Download and verify the exact HTTP ranges in a FrameBridge ray plan."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen


def _sha256_bytes(contents: bytes) -> str:
    return hashlib.sha256(contents).hexdigest()


def _sha256_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _download_one(url: str, record: dict[str, object], output_dir: Path, retries: int):
    index = int(record["index"])
    start = int(record["byte_start"])
    end = int(record["byte_end"])
    expected_length = end - start + 1
    target = output_dir / f"{index:05d}_rows_{record['row_start']}_{record['row_end']}.u8"
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"Range": f"bytes={start}-{end}"})
            with urlopen(request, timeout=90) as response:
                status = getattr(response, "status", None)
                content_range = response.headers.get("Content-Range")
                if status != 206:
                    raise RuntimeError(
                        f"server returned HTTP {status}, refusing possible full-file response"
                    )
                expected_header = f"bytes {start}-{end}/"
                if not content_range or not content_range.startswith(expected_header):
                    raise RuntimeError(f"unexpected Content-Range {content_range!r}")
                contents = response.read(expected_length + 1)
            if len(contents) != expected_length:
                raise RuntimeError(
                    f"range length {len(contents)} does not equal expected {expected_length}"
                )
            target.write_bytes(contents)
            return {
                "index": index,
                "path": target.name,
                "row_start": int(record["row_start"]),
                "row_end": int(record["row_end"]),
                "byte_start": start,
                "byte_end": end,
                "bytes": expected_length,
                "sha256": _sha256_bytes(contents),
            }
        except Exception:
            if attempt == retries:
                raise
            time.sleep(min(2**attempt, 8))
    raise AssertionError("unreachable")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()
    if args.workers < 1 or args.retries < 1:
        raise ValueError("workers and retries must be positive")

    plan_bytes = args.plan.read_bytes()
    plan = json.loads(plan_bytes)
    if plan.get("kind") not in {
        "framebridge_e1_pilot_ray_plan",
        "framebridge_e1_local_ray_plan",
        "framebridge_e1_all_mesh_local_ray_plan",
    }:
        raise ValueError(f"unsupported plan kind {plan.get('kind')!r}")
    url = plan.get("channel_url")
    if not isinstance(url, str) or not url.startswith("https://"):
        raise ValueError("channel_url must be HTTPS")
    raw_ranges = plan.get("acquisition", {}).get("ranges")
    if not isinstance(raw_ranges, list) or not raw_ranges:
        raise ValueError("plan contains no acquisition ranges")
    records = []
    previous_end = -1
    for index, item in enumerate(raw_ranges):
        record = dict(item)
        record["index"] = index
        start, end = int(record["byte_start"]), int(record["byte_end"])
        if start <= previous_end or end < start:
            raise ValueError("ranges must be sorted, non-overlapping, and non-empty")
        if int(record["length"]) != end - start + 1:
            raise ValueError("range length does not match inclusive endpoints")
        previous_end = end
        records.append(record)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    completed = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(_download_one, url, record, args.output_dir, args.retries): record
            for record in records
        }
        for ordinal, future in enumerate(as_completed(futures), start=1):
            completed.append(future.result())
            if ordinal % 25 == 0 or ordinal == len(records):
                downloaded = sum(int(item["bytes"]) for item in completed)
                print(
                    f"verified {ordinal:,}/{len(records):,} ranges; "
                    f"{downloaded / 1024**2:.1f} MiB",
                    flush=True,
                )

    completed.sort(key=lambda item: int(item["index"]))
    expected_bytes = int(plan["acquisition"]["payload_bytes"])
    actual_bytes = sum(int(item["bytes"]) for item in completed)
    if actual_bytes != expected_bytes:
        raise RuntimeError(f"downloaded {actual_bytes} bytes, plan requires {expected_bytes}")
    manifest = {
        "schema_version": 1,
        "kind": "framebridge_respool_range_download",
        "plan_path": str(args.plan),
        "plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
        "channel_url": url,
        "payload_bytes": actual_bytes,
        "range_count": len(completed),
        "files": completed,
    }
    manifest_path = args.output_dir / "download_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    # Re-read every file after writing so success proves durable bytes, not
    # merely the in-memory response buffers.
    for item in completed:
        actual = _sha256_file(args.output_dir / str(item["path"]))
        if actual != item["sha256"]:
            raise RuntimeError(f"post-write digest mismatch for {item['path']}")
    print(json.dumps({
        "payload_bytes": actual_bytes,
        "range_count": len(completed),
        "manifest": str(manifest_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
