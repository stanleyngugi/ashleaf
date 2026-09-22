#!/usr/bin/env python3
"""Score frozen E1 on the corrected independent FB03 pilot mesh."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GAUGE_ROOT = ROOT / "data" / "external" / "constraint-gauge"
sys.path.insert(0, str(GAUGE_ROOT))

from gauge.gt import build_pairs  # noqa: E402
from gauge.meshgt import load_mesh_gt  # noqa: E402
from gauge.pairwise import PairwiseResult, score_pairs, summarize_pairs  # noqa: E402

from scroll_lab.respool import RespoolIndex  # noqa: E402
from scroll_lab.sparse_e1 import predict_pairs  # noqa: E402
from scroll_lab.sparse_sampling import SparseRespoolSampler  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh-dir", type=Path, required=True)
    parser.add_argument("--umbilicus", type=Path, required=True)
    parser.add_argument("--meta", type=Path, required=True)
    parser.add_argument("--coords", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--download-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mesh-stride", type=int, default=10)
    parser.add_argument("--max-pairs", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    index = RespoolIndex.load(args.meta, args.coords, args.table)
    sampler = SparseRespoolSampler.from_download(index, args.download_manifest)
    mesh_xyz, winding, collection, mesh_info = load_mesh_gt(
        str(args.mesh_dir), stride=args.mesh_stride
    )
    pairs = build_pairs(
        mesh_xyz,
        winding,
        collection,
        max_pairs=args.max_pairs,
        seed=args.seed,
    )
    working_xyz = mesh_xyz / 4.0
    predicted, answered, confidence, estimator_stats = predict_pairs(
        sampler,
        working_xyz,
        pairs,
        args.umbilicus,
    )
    result = PairwiseResult("E1/held-out", predicted, answered, confidence)
    table = score_pairs(pairs, result)
    summary = summarize_pairs(pairs, result, table)
    summary.update({
        "schema_version": 1,
        "experiment": "FB04",
        "subject": "E1/held-out",
        "gt_arm": "paris4-mesh-pilot-20231022170901",
        "provenance": "independent",
        "publishable_as_headline": True,
        "coordinate_correction": "mesh xyz / 4 -> E1 9.6um working xyz",
        "pair_protocol": {
            "mesh_stride": args.mesh_stride,
            "max_pairs": args.max_pairs,
            "seed": args.seed,
        },
        "mesh_info": mesh_info,
        "estimator": estimator_stats,
        "prediction_histogram": {
            str(int(value)): int(count)
            for value, count in zip(*np.unique(predicted[answered], return_counts=True))
        },
        "true_histogram": {
            str(int(value)): int(count)
            for value, count in zip(*np.unique(pairs["dw"], return_counts=True))
        },
    })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "pairs": summary["n_pairs_gt"],
        "answered": summary["n_scorable"],
        "coverage": summary["M4_coverage"],
        "dw1_pairs": summary["n_dw1"],
        "exact_dw1": summary["M1_exact_dw1"],
        "mae": summary["M2_mae"],
        "output": str(args.output),
    }, indent=2, allow_nan=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
