#!/usr/bin/env python3
"""Fetch and hash the nine pinned Paris 4 benchmark TIFXYZ coordinate sets."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
VOLUME = "20260411134726-2.4um"
SEGMENTS = (
    "20230702185753",
    "20230929220926",
    "20231005123336",
    "20231012184424",
    "20231016151002",
    "20231022170901",
    "20231031143852",
    "20231106155351",
    "20231221180251",
)


def _sha256(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _fetch(segment: str, axis: str, retries: int) -> dict[str, object]:
    dirname = f"{segment}-on-{VOLUME}.tifxyz"
    relative = Path("data") / "PHercParis4" / "benchmark_meshes" / dirname / f"{axis}.tif"
    target = ROOT / relative
    url = (
        "https://vesuvius-challenge-open-data.s3.amazonaws.com/PHercParis4/"
        f"segments/{segment}/mesh/{dirname}/{axis}.tif"
    )
    if target.is_file() and target.stat().st_size > 8:
        with target.open("rb") as handle:
            magic = handle.read(4)
        if magic[:2] in {b"II", b"MM"}:
            return {
                "segment": segment,
                "axis": axis,
                "path": relative.as_posix(),
                "url": url,
                "bytes": target.stat().st_size,
                "sha256": _sha256(target),
                "status": "verified-existing",
            }
    for attempt in range(1, retries + 1):
        try:
            with urlopen(url, timeout=120) as response:
                contents = response.read()
            if len(contents) <= 8 or contents[:2] not in {b"II", b"MM"}:
                raise ValueError(f"{url}: response is not a TIFF")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(contents)
            return {
                "segment": segment,
                "axis": axis,
                "path": relative.as_posix(),
                "url": url,
                "bytes": len(contents),
                "sha256": hashlib.sha256(contents).hexdigest(),
                "status": "downloaded",
            }
        except Exception:
            if attempt == retries:
                raise
            time.sleep(min(2**attempt, 8))
    raise AssertionError("unreachable")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "artifacts" / "framebridge" / "all_mesh_tiff_manifest.json",
    )
    args = parser.parse_args()
    jobs = [(segment, axis) for segment in SEGMENTS for axis in ("x", "y", "z")]
    records = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(_fetch, segment, axis, args.retries): (segment, axis)
            for segment, axis in jobs
        }
        for ordinal, future in enumerate(as_completed(futures), start=1):
            record = future.result()
            records.append(record)
            print(
                f"{ordinal:02d}/{len(jobs)} {record['status']} "
                f"{record['segment']} {record['axis']} {record['bytes']} bytes",
                flush=True,
            )
    records.sort(key=lambda item: (str(item["segment"]), str(item["axis"])))
    output = {
        "schema_version": 1,
        "kind": "framebridge_mesh_tiff_manifest",
        "volume": VOLUME,
        "segments": list(SEGMENTS),
        "total_bytes": sum(int(record["bytes"]) for record in records),
        "files": records,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(records), "total_bytes": output["total_bytes"], "manifest": str(args.manifest)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
