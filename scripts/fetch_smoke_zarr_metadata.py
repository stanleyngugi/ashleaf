#!/usr/bin/env python3
"""Fetch only the metadata for one official Grand Prize-eligible CT volume."""

from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
RELATIVE = "PHerc0125/volumes/20250821151825-9.362um-1.2m-113keV-masked.zarr"
BASE = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/" + RELATIVE
HASHES = {
    ".zgroup": "2383746e67b4bcc2762b3f100f06c3fa2d5f149ab5a8e5da5d33521464a01959",
    ".zattrs": "97e968dbbf11cc856dc57648aaaa9e6cade5e6575472dcfdeac7cfa50f546dd9",
    "0/.zarray": "ae9b954b9e3c9155a39c716afab5b133eb87d546a4b6dc6ded77abae4c71c613",
    "1/.zarray": "b6292da58c1319bd890a8ccaef427b615250f16a4064f2b654c3335eb5ffe8d0",
    "2/.zarray": "f2163c95656766269d57f865b0c3e835d78e8d812d2edad548785a42f9146da2",
    "3/.zarray": "e409f47fb3b02107259e6278a9f916a862a6fccf373ab3e4e6a7ae3e54d74ff2",
    "4/.zarray": "04011de63806440610a80297577ce30fdef557480718f12c292fc3675f24c73f",
    "5/.zarray": "03be6c4135eb2ab0d3f37161abff61377728cb0b679de328a7b0934756a8a630",
}


def main() -> int:
    destination = ROOT / "data" / RELATIVE
    for name, expected in HASHES.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == expected:
            print(f"verified {name}")
            continue
        with urlopen(f"{BASE}/{name}", timeout=30) as response:
            contents = response.read()
        digest = hashlib.sha256(contents).hexdigest()
        if digest != expected:
            raise ValueError(f"source metadata changed for {name}: sha256={digest}")
        target.write_bytes(contents)
        print(f"downloaded {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
