#!/usr/bin/env python3
"""Fail-loudly evidence check and concise release summary for FrameBridge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fb06", type=Path, required=True)
    parser.add_argument("--fb07", type=Path, required=True)
    args = parser.parse_args()
    fb06 = json.loads(args.fb06.read_text(encoding="utf-8"))
    fb07 = json.loads(args.fb07.read_text(encoding="utf-8"))
    if fb06.get("experiment") != "FB06":
        raise ValueError("unexpected FB06 artifact")
    if fb07.get("experiment") != "FB07" or not fb07.get("not_new_heldout_evidence"):
        raise ValueError("FB07 evidence-class guard failed")
    primary = fb06["primary_replication"]
    if primary["replication_meshes"] != 3 or primary["ineligible_replication_meshes"] != 5:
        raise ValueError("FB06 eligibility counts changed")
    for mesh_id, mesh in fb06["meshes"].items():
        if mesh.get("status") == "eligible" and mesh["M4_coverage"] != 1.0:
            raise ValueError(f"{mesh_id}: incomplete technical coverage")
    summary = {
        "release_check": "PASS",
        "claim_boundary": "FB06 frozen held-out replication; FB07 internal LOSO only",
        "fb06_sha256": digest(args.fb06),
        "fb07_sha256": digest(args.fb07),
        "fb06": {
            "eligible_heldout_meshes": primary["replication_meshes"],
            "ineligible_heldout_meshes": primary["ineligible_replication_meshes"],
            "heldout_pairs": primary["replication_pairs"],
            "pooled_exact_full_coverage": primary["pooled_exact_signed_dw1"],
            "macro_exact_mean": primary["macro_exact_signed_dw1"]["mean"],
            "macro_exact_median": primary["macro_exact_signed_dw1"]["median"],
        },
        "fb07_internal_loso_at_30pct": {
            method: fb07["aggregate"][method]["0.30"]
            for method in ("distance_only", "native_confidence", "geometry_logistic")
        },
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
