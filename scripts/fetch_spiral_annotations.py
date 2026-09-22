#!/usr/bin/env python3
"""Fetch the small public Paris 4 winding annotations and umbilicus."""

from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4"
HASHES = {
    "same_windings.json": "d9be52c5ebb42853f75f235241cbfd159738f6f34468bcd182523bc91dc91048",
    "relative_windings.json": "a3243511d4eb91387a9b32f4dbff11514b08c3ae36e9b2a2b8222607b4883ac1",
    "abs_winding.json": "4e566731f7cbaf8f5ec843de687b3f72f4a784c40b587ebbaf544550902172c1",
    "umbilicus.json": "c5f30b0d135c1d333f8170e592079a3d5a636e0071c0dcce560eecebb0ee2602",
}


def main() -> int:
    folder = ROOT / "data" / "PHercParis4"
    folder.mkdir(parents=True, exist_ok=True)
    for name, expected in HASHES.items():
        target = folder / name
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == expected:
            print(f"verified {name}")
            continue
        with urlopen(f"{BASE}/{name}", timeout=30) as response:
            contents = response.read()
        actual = hashlib.sha256(contents).hexdigest()
        if actual != expected:
            raise ValueError(f"source changed for {name}: sha256={actual}")
        target.write_bytes(contents)
        print(f"downloaded {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
