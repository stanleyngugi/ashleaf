#!/usr/bin/env python3
"""Run preregistered FB07 leave-one-segment-out confidence ranking."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

from scroll_lab.sparse_e1 import load_umbilicus_axis

COVERAGES = (0.10, 0.20, 0.30, 0.50, 0.70, 1.00)
FEATURE_NAMES = (
    "log1p_distance",
    "native_confidence",
    "angular_separation_degrees",
    "absolute_dz_fraction",
    "radial_alignment",
    "log_distance_x_angular",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def features(points: np.ndarray, pairs: dict[str, np.ndarray], confidence: np.ndarray, axis) -> np.ndarray:
    a, b = points[pairs["a"]], points[pairs["b"]]
    chord = b - a
    distance = np.linalg.norm(chord, axis=1)
    midpoint = 0.5 * (a + b)
    centers = np.asarray([axis(float(z)) for z in midpoint[:, 2]])
    va, vb = a[:, :2] - centers, b[:, :2] - centers
    angular = np.abs(np.arctan2(
        va[:, 0] * vb[:, 1] - va[:, 1] * vb[:, 0],
        np.sum(va * vb, axis=1),
    )) * 180.0 / np.pi
    radial = midpoint[:, :2] - centers
    chord_xy = chord[:, :2]
    radial_alignment = np.sum(chord_xy * radial, axis=1) / np.maximum(
        np.linalg.norm(chord_xy, axis=1) * np.linalg.norm(radial, axis=1), 1e-12
    )
    log_distance = np.log1p(distance)
    return np.column_stack([
        log_distance,
        confidence,
        angular,
        np.abs(chord[:, 2]) / np.maximum(distance, 1e-12),
        radial_alignment,
        log_distance * angular,
    ])


def fit_logistic(x: np.ndarray, y: np.ndarray, weights: np.ndarray):
    mean, scale = x.mean(axis=0), x.std(axis=0)
    scale[scale < 1e-12] = 1.0
    z = (x - mean) / scale
    design = np.column_stack([np.ones(len(z)), z])
    weights = weights / weights.sum()

    def objective(beta):
        linear = design @ beta
        loss = np.sum(weights * (np.logaddexp(0.0, linear) - y * linear))
        penalty = 0.5 * np.sum(beta[1:] ** 2)
        probability = expit(linear)
        gradient = design.T @ (weights * (probability - y))
        gradient[1:] += beta[1:]
        return float(loss + penalty), gradient

    result = minimize(
        objective,
        np.zeros(design.shape[1]),
        method="L-BFGS-B",
        jac=True,
        options={"maxiter": 1000, "ftol": 1e-12, "gtol": 1e-9},
    )
    if not result.success:
        raise RuntimeError(f"logistic fit failed: {result.message}")
    return result.x, mean, scale, float(result.fun), int(result.nit)


def rank_metrics(score: np.ndarray, correct: np.ndarray) -> dict[str, object]:
    order = np.argsort(-score, kind="stable")
    output = {}
    for coverage in COVERAGES:
        count = min(len(order), max(1, int(np.ceil(coverage * len(order)))))
        selected = order[:count]
        output[f"{coverage:.2f}"] = {
            "selected": int(count),
            "realized_coverage": float(count / len(order)),
            "accuracy": float(np.mean(correct[selected])),
        }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--umbilicus", type=Path, required=True)
    parser.add_argument("--ray-plan", type=Path, required=True)
    parser.add_argument("--error-analysis", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    plan = json.loads(args.ray_plan.read_text(encoding="utf-8"))
    analysis = json.loads(args.error_analysis.read_text(encoding="utf-8"))
    axis, _ = load_umbilicus_axis(args.umbilicus)
    segments: dict[str, dict[str, object]] = {}
    for mesh_name, planned in sorted(plan["meshes"].items()):
        if planned.get("status") != "eligible":
            continue
        mesh_id = mesh_name.split("-on-", 1)[0]
        cache_path = Path(planned["pair_cache_path"])
        detail_path = Path(analysis["meshes"][mesh_id]["detail_path"])
        if sha256(cache_path) != planned["pair_cache_sha256"]:
            raise RuntimeError(f"pair cache digest mismatch: {mesh_id}")
        if sha256(detail_path) != analysis["meshes"][mesh_id]["detail_sha256"]:
            raise RuntimeError(f"detail digest mismatch: {mesh_id}")
        with np.load(cache_path, allow_pickle=False) as payload:
            points = payload["points"]
            pairs = {name: payload[name] for name in ("a", "b", "dw")}
        with np.load(detail_path, allow_pickle=False) as payload:
            predicted = payload["predicted"]
            confidence = payload["confidence"]
        x = features(points, pairs, confidence, axis)
        correct = predicted == 1
        segments[mesh_id] = {
            "x": x,
            "correct": correct,
            "distance_score": -x[:, 0],
            "native_score": confidence,
            "pair_cache_sha256": sha256(cache_path),
            "detail_sha256": sha256(detail_path),
        }

    folds: dict[str, object] = {}
    selected_correct: dict[str, dict[str, list[np.ndarray]]] = {
        method: {f"{coverage:.2f}": [] for coverage in COVERAGES}
        for method in ("distance_only", "native_confidence", "geometry_logistic")
    }
    for test_id in sorted(segments):
        train_ids = [item for item in sorted(segments) if item != test_id]
        train_x = np.concatenate([segments[item]["x"] for item in train_ids])
        train_y = np.concatenate([segments[item]["correct"] for item in train_ids]).astype(float)
        train_weights = np.concatenate([
            np.full(len(segments[item]["correct"]), 1.0 / len(segments[item]["correct"]))
            for item in train_ids
        ])
        beta, mean, scale, objective, iterations = fit_logistic(
            train_x, train_y, train_weights
        )
        test_x = segments[test_id]["x"]
        geometry_score = expit(
            beta[0] + ((test_x - mean) / scale) @ beta[1:]
        )
        scores = {
            "distance_only": segments[test_id]["distance_score"],
            "native_confidence": segments[test_id]["native_score"],
            "geometry_logistic": geometry_score,
        }
        correct = segments[test_id]["correct"]
        method_metrics = {name: rank_metrics(score, correct) for name, score in scores.items()}
        for method, score in scores.items():
            order = np.argsort(-score, kind="stable")
            for coverage in COVERAGES:
                count = min(len(order), max(1, int(np.ceil(coverage * len(order)))))
                selected_correct[method][f"{coverage:.2f}"].append(correct[order[:count]])
        folds[test_id] = {
            "train_segments": train_ids,
            "test_pairs": len(correct),
            "full_accuracy": float(correct.mean()),
            "model": {
                "feature_names": list(FEATURE_NAMES),
                "coefficients_intercept_then_standardized_features": beta.tolist(),
                "training_feature_mean": mean.tolist(),
                "training_feature_scale": scale.tolist(),
                "weighted_objective": objective,
                "iterations": iterations,
            },
            "methods": method_metrics,
        }
        print(json.dumps({
            "held_out_segment": test_id,
            "full_accuracy": float(correct.mean()),
            "accuracy_at_30pct": {
                name: values["0.30"]["accuracy"] for name, values in method_metrics.items()
            },
        }), flush=True)

    aggregate: dict[str, object] = {}
    for method in selected_correct:
        coverage_summary = {}
        for coverage in COVERAGES:
            key = f"{coverage:.2f}"
            per_fold = [folds[mid]["methods"][method][key]["accuracy"] for mid in sorted(folds)]
            pooled = np.concatenate(selected_correct[method][key])
            coverage_summary[key] = {
                "macro_mean_accuracy": float(np.mean(per_fold)),
                "macro_median_accuracy": float(np.median(per_fold)),
                "worst_segment_accuracy": float(np.min(per_fold)),
                "best_segment_accuracy": float(np.max(per_fold)),
                "pooled_accuracy": float(np.mean(pooled)),
                "pooled_selected_pairs": int(len(pooled)),
            }
        aggregate[method] = coverage_summary

    output = {
        "schema_version": 1,
        "experiment": "FB07",
        "evidence_class": "internal_loso_post_FB06",
        "not_new_heldout_evidence": True,
        "primary_metric": "macro_mean_accuracy_at_30pct_coverage",
        "feature_names": list(FEATURE_NAMES),
        "coverages": list(COVERAGES),
        "inputs": {
            "ray_plan": str(args.ray_plan),
            "ray_plan_sha256": sha256(args.ray_plan),
            "error_analysis": str(args.error_analysis),
            "error_analysis_sha256": sha256(args.error_analysis),
            "umbilicus": str(args.umbilicus),
            "umbilicus_sha256": sha256(args.umbilicus),
            "segments": {
                key: {
                    "pair_cache_sha256": value["pair_cache_sha256"],
                    "detail_sha256": value["detail_sha256"],
                }
                for key, value in segments.items()
            },
        },
        "folds": folds,
        "aggregate": aggregate,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "primary_30pct": {method: values["0.30"] for method, values in aggregate.items()},
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
