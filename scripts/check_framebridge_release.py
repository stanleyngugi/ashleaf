#!/usr/bin/env python3
"""Fail-loudly evidence check and concise release summary for FrameBridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual: float, expected: float, label: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-10):
        raise ValueError(f"{label}: recomputed {actual} != stored {expected}")


def verify_fb06(fb06: dict) -> dict:
    eligible = [
        mesh for mesh in fb06["meshes"].values()
        if mesh.get("role") == "frozen_replication" and mesh.get("status") == "eligible"
    ]
    ineligible = [
        mesh for mesh in fb06["meshes"].values()
        if mesh.get("role") == "frozen_replication" and mesh.get("status") != "eligible"
    ]
    primary = fb06["primary_replication"]
    if len(eligible) != primary["replication_meshes"] or len(ineligible) != primary["ineligible_replication_meshes"]:
        raise ValueError("FB06 eligibility counts changed")
    pooled: dict[int, int] = {}
    scores = []
    for mesh in eligible:
        count = mesh["n_pairs_gt"]
        if mesh["n_dw1"] != count or mesh["n_scorable"] != count or mesh["M4_coverage"] != 1.0:
            raise ValueError("FB06 eligible mesh is not completely scored with dw=+1 labels")
        hist = {int(value): int(n) for value, n in mesh["prediction_histogram"].items()}
        if sum(hist.values()) != count:
            raise ValueError("FB06 prediction histogram does not cover its mesh")
        for prediction, n in hist.items():
            pooled[prediction] = pooled.get(prediction, 0) + n
        exact = hist.get(1, 0) / count
        mae = sum(abs(prediction - 1) * n for prediction, n in hist.items()) / count
        close(exact, mesh["M1_exact_dw1"], "FB06 mesh exact")
        close(mae, mesh["M2_mae"], "FB06 mesh MAE")
        scores.append(exact)
    count = sum(pooled.values())
    if count != primary["replication_pairs"] or {str(k): v for k, v in pooled.items()} != primary["pooled_prediction_histogram"]:
        raise ValueError("FB06 pooled pair count or prediction histogram changed")
    exact = pooled.get(1, 0) / count
    mae = sum(abs(prediction - 1) * n for prediction, n in pooled.items()) / count
    close(exact, primary["pooled_exact_signed_dw1"], "FB06 pooled exact")
    close(mae, primary["pooled_mae"], "FB06 pooled MAE")
    close(mean(scores), primary["macro_exact_signed_dw1"]["mean"], "FB06 macro exact")
    close(median(scores), primary["macro_exact_signed_dw1"]["median"], "FB06 median exact")
    return {"pairs": count, "exact_hits": pooled.get(1, 0), "pooled_e1_agreement": exact,
            "pooled_mae": mae, "constant_plus_one_baseline_accuracy": 1.0}


def verify_fb07(fb07: dict) -> dict:
    if fb07.get("evidence_class") != "internal_loso_post_FB06":
        raise ValueError("FB07 evidence class changed")
    folds = fb07["folds"]
    if len(folds) != 4:
        raise ValueError("FB07 fold count changed")
    recomputed = {}
    for method in ("distance_only", "native_confidence", "geometry_logistic"):
        for coverage, stored in fb07["aggregate"][method].items():
            rows = [fold["methods"][method][coverage] for fold in folds.values()]
            scores = [row["accuracy"] for row in rows]
            selected = sum(row["selected"] for row in rows)
            pooled = sum(row["accuracy"] * row["selected"] for row in rows) / selected
            for key, value in (
                ("macro_mean_accuracy", mean(scores)),
                ("macro_median_accuracy", median(scores)),
                ("worst_segment_accuracy", min(scores)),
                ("best_segment_accuracy", max(scores)),
                ("pooled_accuracy", pooled),
            ):
                close(value, stored[key], f"FB07 {method}/{coverage} {key}")
            if selected != stored["pooled_selected_pairs"]:
                raise ValueError(f"FB07 {method}/{coverage} selected-pair count changed")
            if coverage == "0.30":
                recomputed[method] = {"macro_e1_agreement": mean(scores),
                                      "pooled_e1_agreement": pooled, "selected_pairs": selected}
    return recomputed


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
    verified_fb06 = verify_fb06(fb06)
    verified_fb07 = verify_fb07(fb07)
    primary = fb06["primary_replication"]
    summary = {
        "release_check": "PASS",
        "claim_boundary": "positive-only dw=+1 E1 agreement; FB06 frozen held-out replication; FB07 internal LOSO only; no raw CT rerun",
        "fb06_sha256": digest(args.fb06),
        "fb07_sha256": digest(args.fb07),
        "fb06": {
            "eligible_heldout_meshes": primary["replication_meshes"],
            "ineligible_heldout_meshes": primary["ineligible_replication_meshes"],
            "heldout_pairs": primary["replication_pairs"],
            "pooled_exact_full_coverage": primary["pooled_exact_signed_dw1"],
            "macro_exact_mean": primary["macro_exact_signed_dw1"]["mean"],
            "macro_exact_median": primary["macro_exact_signed_dw1"]["median"],
            "recomputed_from_tracked_histograms": verified_fb06,
        },
        "fb07_internal_loso_at_30pct": verified_fb07,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
