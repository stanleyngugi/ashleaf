#!/usr/bin/env python3
"""Run the preregistered local-correspondence E1 mesh diagnostic."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GAUGE_ROOT = ROOT / "data" / "external" / "constraint-gauge"
sys.path.insert(0, str(GAUGE_ROOT))

from gauge.pairwise import PairwiseResult, score_pairs, summarize_pairs  # noqa: E402

from scroll_lab.local_mesh_pairs import build_local_adjacent_pairs  # noqa: E402
from scroll_lab.respool import RespoolIndex  # noqa: E402
from scroll_lab.sparse_e1 import load_umbilicus_axis, predict_pairs  # noqa: E402
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
    parser.add_argument("--stride-v", type=int, default=10)
    parser.add_argument("--stride-u", type=int, default=10)
    parser.add_argument("--max-pairs", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    axis, _ = load_umbilicus_axis(args.umbilicus)
    points, pairs, pair_info = build_local_adjacent_pairs(
        args.mesh_dir,
        axis,
        constraint_gauge_root=GAUGE_ROOT,
        stride_v=args.stride_v,
        stride_u=args.stride_u,
        max_pairs=args.max_pairs,
        seed=args.seed,
    )
    print(json.dumps({"pair_geometry": pair_info}, indent=2), flush=True)
    index = RespoolIndex.load(args.meta, args.coords, args.table)
    sampler = SparseRespoolSampler.from_download(index, args.download_manifest)
    predicted, answered, confidence, estimator = predict_pairs(
        sampler, points, pairs, args.umbilicus
    )
    result = PairwiseResult("E1/local-correspondence", predicted, answered, confidence)
    table = score_pairs(pairs, result)
    summary = summarize_pairs(pairs, result, table)
    answered_predictions = predicted[answered]
    summary.update({
        "schema_version": 1,
        "experiment": "FB05",
        "subject": "E1/local-correspondence",
        "gt_arm": "paris4-mesh-pilot-20231022170901-local-adjacent",
        "provenance": "independent diagnostic",
        "publishable_as_headline": False,
        "does_not_replace": "FB04 generic mesh-pair result",
        "pair_protocol": pair_info,
        "estimator": estimator,
        "exact_absolute_dw1": float(np.mean(np.abs(answered_predictions) == 1))
        if len(answered_predictions) else float("nan"),
        "positive_sign_fraction": float(np.mean(answered_predictions > 0))
        if len(answered_predictions) else float("nan"),
        "prediction_histogram": {
            str(int(value)): int(count)
            for value, count in zip(*np.unique(answered_predictions, return_counts=True))
        },
    })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "pairs": summary["n_pairs_gt"],
        "answered": summary["n_scorable"],
        "coverage": summary["M4_coverage"],
        "exact_signed_dw1": summary["M1_exact_dw1"],
        "exact_absolute_dw1": summary["exact_absolute_dw1"],
        "mae": summary["M2_mae"],
        "positive_sign_fraction": summary["positive_sign_fraction"],
        "output": str(args.output),
    }, indent=2, allow_nan=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
