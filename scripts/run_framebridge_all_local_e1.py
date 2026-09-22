#!/usr/bin/env python3
"""Run the frozen local-pair E1 diagnostic across all verified Paris4 meshes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GAUGE_ROOT = ROOT / "data" / "external" / "constraint-gauge"
sys.path.insert(0, str(GAUGE_ROOT))

from gauge.pairwise import PairwiseResult, score_pairs, summarize_pairs  # noqa: E402

from scroll_lab.respool import RespoolIndex  # noqa: E402
from scroll_lab.sparse_e1 import predict_pairs  # noqa: E402
from scroll_lab.sparse_sampling import SparseRespoolSampler  # noqa: E402


def finite_summary(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "minimum": float(np.min(array)),
        "maximum": float(np.max(array)),
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
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stride-v", type=int, default=10)
    parser.add_argument("--stride-u", type=int, default=10)
    parser.add_argument("--max-pairs", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    umbilicus_digest = hashlib.sha256(args.umbilicus.read_bytes()).hexdigest()
    index = RespoolIndex.load(args.meta, args.coords, args.table)
    sampler = SparseRespoolSampler.from_download(index, args.download_manifest)
    ray_plan = json.loads(args.ray_plan.read_text(encoding="utf-8"))
    if ray_plan.get("kind") != "framebridge_e1_all_mesh_local_ray_plan":
        raise ValueError("ray plan has unexpected kind")
    results: dict[str, object] = {}
    pooled_truth: list[np.ndarray] = []
    pooled_predictions: list[np.ndarray] = []
    estimator = None
    for mesh_name, planned in sorted(ray_plan["meshes"].items()):
        mesh_id = mesh_name.split("-on-", 1)[0]
        role = "development_pilot" if mesh_id == args.pilot_id else "frozen_replication"
        if planned.get("status") != "eligible":
            results[mesh_id] = {
                "role": role,
                "status": "ineligible_frozen_protocol",
                "reason": planned.get("reason", "unspecified"),
            }
            print(json.dumps({
                "mesh": mesh_id,
                "role": role,
                "status": "ineligible_frozen_protocol",
                "reason": planned.get("reason", "unspecified"),
            }), flush=True)
            continue
        cache_path = Path(planned["pair_cache_path"])
        cache_digest = hashlib.sha256(cache_path.read_bytes()).hexdigest()
        if cache_digest != planned["pair_cache_sha256"]:
            raise RuntimeError(f"pair cache digest mismatch for {mesh_id}")
        with np.load(cache_path, allow_pickle=False) as payload:
            points = payload["points"]
            pairs = {name: payload[name] for name in ("a", "b", "dw")}
        pair_info = planned["pair_protocol"]
        predicted, answered, confidence, estimator = predict_pairs(
            sampler, points, pairs, args.umbilicus
        )
        result = PairwiseResult("E1/local-correspondence", predicted, answered, confidence)
        table = score_pairs(pairs, result)
        summary = summarize_pairs(pairs, result, table)
        answered_predictions = predicted[answered]
        summary.update({
            "role": role,
            "status": "eligible",
            "pair_cache_sha256": cache_digest,
            "pair_protocol": pair_info,
            "exact_absolute_dw1": float(np.mean(np.abs(answered_predictions) == 1)),
            "positive_sign_fraction": float(np.mean(answered_predictions > 0)),
            "prediction_histogram": {
                str(int(value)): int(count)
                for value, count in zip(*np.unique(answered_predictions, return_counts=True))
            },
        })
        results[mesh_id] = summary
        if role == "frozen_replication":
            pooled_truth.append(pairs["dw"][answered])
            pooled_predictions.append(answered_predictions)
        print(json.dumps({
            "mesh": mesh_id,
            "role": summary["role"],
            "pairs": summary["n_pairs_gt"],
            "coverage": summary["M4_coverage"],
            "exact_signed_dw1": summary["M1_exact_dw1"],
            "mae": summary["M2_mae"],
        }), flush=True)

    replication = [
        item for item in results.values()
        if item["role"] == "frozen_replication" and item.get("status") == "eligible"
    ]
    ineligible_replication = [
        item for item in results.values()
        if item["role"] == "frozen_replication" and item.get("status") != "eligible"
    ]
    if not replication:
        raise RuntimeError("no held-out mesh is eligible for the frozen protocol")
    truth = np.concatenate(pooled_truth)
    predicted = np.concatenate(pooled_predictions)
    aggregate = {
        "replication_meshes": len(replication),
        "ineligible_replication_meshes": len(ineligible_replication),
        "replication_pairs": int(len(truth)),
        "pooled_exact_signed_dw1": float(np.mean(predicted == truth)),
        "pooled_exact_absolute_dw1": float(np.mean(np.abs(predicted) == 1)),
        "pooled_mae": float(np.mean(np.abs(predicted - truth))),
        "pooled_positive_sign_fraction": float(np.mean(predicted > 0)),
        "macro_exact_signed_dw1": finite_summary(
            [float(item["M1_exact_dw1"]) for item in replication]
        ),
        "macro_mae": finite_summary([float(item["M2_mae"]) for item in replication]),
        "macro_coverage": finite_summary([float(item["M4_coverage"]) for item in replication]),
        "pooled_prediction_histogram": {
            str(int(value)): int(count)
            for value, count in zip(*np.unique(predicted, return_counts=True))
        },
    }
    output = {
        "schema_version": 1,
        "experiment": "FB06",
        "subject": "E1/local-correspondence/frozen-eight-mesh-replication",
        "primary_claim_population": "eight meshes not used to formulate FB05 protocol",
        "pilot_id_excluded_from_primary": args.pilot_id,
        "publishable_as_headline": False,
        "umbilicus_sha256": umbilicus_digest,
        "estimator": estimator,
        "frozen_protocol": {
            "stride_v": args.stride_v,
            "stride_u": args.stride_u,
            "trim_wraps": 1,
            "max_pairs_per_mesh": args.max_pairs,
            "seed": args.seed,
        },
        "primary_replication": aggregate,
        "meshes": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"primary_replication": aggregate, "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
