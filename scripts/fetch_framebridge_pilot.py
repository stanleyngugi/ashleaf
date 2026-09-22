#!/usr/bin/env python3
"""Fetch and verify the three coordinate TIFFs for the FB03 pilot mesh."""

from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SEGMENT = "20231022170901"
VOLUME = "20260411134726-2.4um"
DIRNAME = f"{SEGMENT}-on-{VOLUME}.tifxyz"
BASE = (
    "https://vesuvius-challenge-open-data.s3.amazonaws.com/PHercParis4/"
    f"segments/{SEGMENT}/mesh/{DIRNAME}"
)
HASHES = {
    "x.tif": "83f9285228392894ec7fbb3cae85965c45ff2ca1d434398147cfca2594088f8c",
    "y.tif": "f89d7f8b391e15414affff25d82520096c99ba0907fb6b8dcfd64496ef604168",
    "z.tif": "9a5f4bffd45f356d8341c32aae63069bf2d1cc3fe9f2a6bfaac519f84938723c",
}


def _digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> int:
    target_dir = ROOT / "data" / "PHercParis4" / "benchmark_meshes" / DIRNAME
    target_dir.mkdir(parents=True, exist_ok=True)
    for name, expected in HASHES.items():
        target = target_dir / name
        status = "verified"
        if not target.is_file() or _digest(target) != expected:
            with urlopen(f"{BASE}/{name}", timeout=60) as response:
                contents = response.read()
            actual = hashlib.sha256(contents).hexdigest()
            if actual != expected:
                raise ValueError(
                    f"source changed for {BASE}/{name}: sha256={actual}, expected={expected}"
                )
            target.write_bytes(contents)
            status = "downloaded"
        print(f"{status} {target.relative_to(ROOT).as_posix()} sha256={expected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
