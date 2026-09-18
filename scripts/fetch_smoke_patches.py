#!/usr/bin/env python3
"""Fetch two tiny public Paris 4 TIFXYZ patches for a real-data smoke test."""

from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/verified_patches"
FILES = {
    "0003_fill_sel_20260512_105100_10": {
        "meta.json": "2d85ab7e7a83cae45e3a1b4db530ad6239f3e816c09569d18aa09701dd753776",
        "x.tif": "593dbe75a657cacd27b57c2c8a44bc87a3a7b6642d8cd95c9db2ab495f0ef89e",
        "y.tif": "5be8a1bf8840c835164081b0dfadec04c667338ad295d06e22bf5bd5cbb61b3b",
        "z.tif": "2c2844ad51cb9502abd805e7a47cfb07f17090c471d7702f479247dae8c29e8e",
    },
    "same_wrap000882_growpatch": {
        "meta.json": "c829486d8969dfad175a7356a54f2de7196614611865bddd2a8cf86ebeca0555",
        "x.tif": "090c35a170f5a6f7d2528cb12592dc59b72ab42e92d4a1263fbbd0a676dbed0b",
        "y.tif": "0ae2bc2994841aeda5327c46f31d355d0c4fe9f18389b24a2f2497b639e25172",
        "z.tif": "0b92e3692f2be66812efb4a9b56ff8e10614958bcf15254179b91206034d996e",
    },
}


def main() -> int:
    for patch_name, files in FILES.items():
        folder = ROOT / "data" / "PHercParis4" / "verified_patches" / patch_name
        folder.mkdir(parents=True, exist_ok=True)
        for filename, expected_hash in files.items():
            target = folder / filename
            if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == expected_hash:
                print(f"verified {patch_name}/{filename}")
                continue
            url = f"{BASE}/{patch_name}/{filename}"
            with urlopen(url, timeout=30) as response:
                contents = response.read()
            actual_hash = hashlib.sha256(contents).hexdigest()
            if actual_hash != expected_hash:
                raise ValueError(f"source changed for {patch_name}/{filename}: sha256={actual_hash}")
            target.write_bytes(contents)
            print(f"downloaded {patch_name}/{filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
