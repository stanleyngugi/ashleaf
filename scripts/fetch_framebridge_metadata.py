#!/usr/bin/env python3
"""Fetch pinned, metadata-only Paris 4 inputs for FrameBridge.

This downloads nine small TIFXYZ ``meta.json`` files, the public umbilicus,
and packed grad-magnitude metadata/verification JSON.  It does not download
mesh coordinate TIFFs, array bricks, CT chunks, or GPU inputs.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DATASET = "https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4"
S3 = "https://vesuvius-challenge-open-data.s3.amazonaws.com/PHercParis4"
VOLUME = "20260411134726-2.4um"

FILES = {
    "umbilicus.json": (
        f"{DATASET}/umbilicus.json",
        "c5f30b0d135c1d333f8170e592079a3d5a636e0071c0dcce560eecebb0ee2602",
    ),
    "lasagna_inputs/grad_mag_respool_g4_meta.json": (
        f"{DATASET}/lasagna_inputs/las_008_grad_mag.ome.zarr.respool_g4/meta.json",
        "c2558e4e60fc9abfcbd4299f52d263a384c3a64b2243428f0cd8474c590a932b",
    ),
    "lasagna_inputs/verification.json": (
        f"{DATASET}/lasagna_inputs/verification.json",
        "dddeb4d3dd4090ea2d1fd47c8687714b1b19671e5681b799057e9a48eb413cc8",
    ),
    "lasagna_inputs/batch_verification.json": (
        f"{DATASET}/lasagna_inputs/batch_verification.json",
        "8c39adddd545770d00905e802e018ec951adb60929193665aeaa4381a60fe024",
    ),
    "lasagna_inputs/grad_mag_respool_g4_brick_coords.npy": (
        f"{DATASET}/lasagna_inputs/las_008_grad_mag.ome.zarr.respool_g4/brick_coords.npy",
        "bfe74a188964bfa188e61ae7e55d32309d645f579b2c9d47066cbd3c9cd87a10",
    ),
    "lasagna_inputs/grad_mag_respool_g4_table.npy": (
        f"{DATASET}/lasagna_inputs/las_008_grad_mag.ome.zarr.respool_g4/table.npy",
        "90edae136224642c7aeee02939dc05911e4c4a97fdfcb7390de539feac180848",
    ),
}

MESH_META_HASHES = {
    "20230702185753": "105c2716274077c3c832765ae6c0885cf679b2cbdef9f89a49875b1ee12fb84f",
    "20230929220926": "5af018c7da1ce401d26012fa97327c24394e32197230ffada03d5eb8fa4cbdeb",
    "20231005123336": "bc9985c4bfee5edf065a5cdcd50e6664a24fd0eef3a491e90faae93c45036d11",
    "20231012184424": "d932e84fc880ee131075a6ce2e2b97fbf1d8cec8935baec22e4a84b3e0c3b266",
    "20231016151002": "6bd22e7e7a87b29075e9d2897c7171b72c30ba4b0864405f590d752dc0a6e58d",
    "20231022170901": "c2e01ee6bc0dfb1bed3f495b495ce40ebb862b9ea7794167606f8868d653036a",
    "20231031143852": "07146605aa833faa61bdcccce24f0350827eea0d6b1f1b0ab256be2e8eee6dfc",
    "20231106155351": "85b4e74cde37bb26ca6d7ab26cd83d5b511bc21a458eec0e2ef3f41e727e48fc",
    "20231221180251": "0d2cabdf18f337c85298b5155b944c036f22b49bb15c783fac0d3c6b66fc676c",
}


def _fetch(target: Path, url: str, expected: str) -> str:
    if target.is_file():
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual == expected:
            return "verified"
    with urlopen(url, timeout=30) as response:
        contents = response.read()
    actual = hashlib.sha256(contents).hexdigest()
    if actual != expected:
        raise ValueError(f"source changed for {url}: sha256={actual}, expected={expected}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(contents)
    return "downloaded"


def main() -> int:
    data = ROOT / "data" / "PHercParis4"
    for relative, (url, expected) in FILES.items():
        status = _fetch(data / relative, url, expected)
        print(f"{status} {relative}")
    for segment_id, expected in MESH_META_HASHES.items():
        dirname = f"{segment_id}-on-{VOLUME}.tifxyz"
        relative = Path("benchmark_meshes") / dirname / "meta.json"
        url = f"{S3}/segments/{segment_id}/mesh/{dirname}/meta.json"
        status = _fetch(data / relative, url, expected)
        print(f"{status} {relative.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
