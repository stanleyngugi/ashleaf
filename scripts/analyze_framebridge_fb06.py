#!/usr/bin/env python3
"""Exploratory FB06 error analysis; never substitutes for the frozen score."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from scroll_lab.respool import RespoolIndex
from scroll_lab.sparse_e1 import predict_pairs
from scroll_lab.sparse_sampling import SparseRespoolSampler

THRESHOLDS = (12.0, 16.0, 20.0, 24.0, 32.0, 40.0, 48.0, 64.0)


def metrics(predicted: np.ndarray, keep: np.ndarray) -> dict[str, float | int]:
    selected = predicted[keep]
    return {
        "pairs": int(keep.sum()),
        "coverage_within_mesh": float(keep.mean()),
        "exact_signed_dw1": float(np.mean(selected == 1)) if len(selected) else float("nan"),
        "mae_to_dw1": float(np.mean(np.abs(selected - 1))) if len(selected) else float("nan"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--umbilicus", type=Path, required=True)
    parser.add_argument("--meta", type=Path, required=True)
    parser.add_argument("--coords", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--download-manifest", type=Path, required=True)
    parser.add_argument("--ray-plan", type=Path, required=True)
    parser.add_argument("--pilot-id", default="20231022170901")
    parser.add_argument("--details-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    plan = json.loads(args.ray_plan.read_text(encoding="utf-8"))
    index = RespoolIndex.load(args.meta, args.coords, args.table)
    sampler = SparseRespoolSampler.from_download(index, args.download_manifest)
    args.details_dir.mkdir(parents=True, exist_ok=True)
    summaries: dict[str, object] = {}
    pooled_distance, pooled_prediction = [], []
    for mesh_name, planned in sorted(plan["meshes"].items()):
        if planned.get("status") != "eligible":
            continue
        mesh_id = mesh_name.split("-on-", 1)[0]
        role = "development_pilot" if mesh_id == args.pilot_id else "frozen_replication"
        cache_path = Path(planned["pair_cache_path"])
        digest = hashlib.sha256(cache_path.read_bytes()).hexdigest()
        if digest != planned["pair_cache_sha256"]:
            raise RuntimeError(f"pair cache digest mismatch for {mesh_id}")
        with np.load(cache_path, allow_pickle=False) as payload:
            points = payload["points"]
            pairs = {name: payload[name] for name in ("a", "b", "dw")}
        predicted, answered, confidence, estimator = predict_pairs(
            sampler, points, pairs, args.umbilicus
        )
        if not answered.all():
            raise RuntimeError(f"{mesh_id}: exploratory analysis expected full support")
        a, b = points[pairs["a"]], points[pairs["b"]]
        distance = np.linalg.norm(b - a, axis=1)
        midpoint_z = 0.5 * (a[:, 2] + b[:, 2])
        detail_path = args.details_dir / f"{mesh_id}.npz"
        np.savez_compressed(
            detail_path,
            predicted=predicted,
            confidence=confidence,
            distance=distance,
            midpoint_z=midpoint_z,
        )
        quantile_edges = np.unique(np.quantile(distance, np.linspace(0, 1, 11)))
        bins = []
        for lower, upper in zip(quantile_edges[:-1], quantile_edges[1:]):
            keep = (distance >= lower) & (distance <= upper if upper == quantile_edges[-1] else distance < upper)
            item = metrics(predicted, keep)
            item.update({"distance_lower": float(lower), "distance_upper": float(upper)})
            bins.append(item)
        summaries[mesh_id] = {
            "role": role,
            "pairs": len(predicted),
            "detail_path": str(detail_path),
            "detail_sha256": hashlib.sha256(detail_path.read_bytes()).hexdigest(),
            "thresholds": {
                str(value): metrics(predicted, distance <= value) for value in THRESHOLDS
            },
            "distance_deciles": bins,
            "estimator": estimator,
        }
        if role == "frozen_replication":
            pooled_distance.append(distance)
            pooled_prediction.append(predicted)
        print(json.dumps({
            "mesh": mesh_id,
            "role": role,
            "distance_le_32": summaries[mesh_id]["thresholds"]["32.0"],
        }), flush=True)

    distance = np.concatenate(pooled_distance)
    predicted = np.concatenate(pooled_prediction)
    output = {
        "schema_version": 1,
        "experiment": "FB06E",
        "status": "exploratory_post_Frozen_FB06",
        "not_a_replacement_for": "FB06 primary frozen replication",
        "hypothesis": "long Euclidean chords cause E1 to count multiple field peaks",
        "fixed_descriptive_thresholds_working_voxels": list(THRESHOLDS),
        "pooled_heldout_thresholds": {
            str(value): metrics(predicted, distance <= value) for value in THRESHOLDS
        },
        "meshes": summaries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "pooled_heldout_thresholds": output["pooled_heldout_thresholds"],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
