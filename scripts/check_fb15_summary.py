#!/usr/bin/env python3
"""Verify the small tracked FB15 result against optional ignored raw artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expect(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path,
                        default=Path("experiments/results/framebridge_fb15_summary.json"))
    parser.add_argument("--validation", type=Path)
    parser.add_argument("--bootstrap", type=Path)
    parser.add_argument("--holdout", type=Path)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    expect(summary["experiment"], "FB15_frozen_surface_SDT_crest", "summary experiment")
    root = Path(__file__).resolve().parents[1]
    expect(sha256(root / "src/scroll_lab/sdt_crossings.py"),
           summary["rule_source_sha256"], "frozen rule source")
    checked = ["frozen_rule"]
    if args.validation is not None:
        expect(sha256(args.validation), summary["ignored_artifact_sha256"]["validation"],
               "validation artifact")
        arms = json.loads(args.validation.read_text(encoding="utf-8"))["arms"]
        for arm_name, summary_name in (("development_remainder", "nonpilot_development"),
                                       ("absolute_stress_seen_E1_truth", "previously_seen_FB14_stress")):
            actual = arms[arm_name]["summary"]
            expected = summary[summary_name]
            mapping = {
                "pairs": "pairs", "collections": "collections",
                "E1_signed_exact": "E1_signed_exact_full",
                "SDT_magnitude_exact": "SDT_magnitude_exact_full",
                "agreement_pairs": "agreement_pairs",
                "agreement_E1_signed_exact": "agreement_E1_signed_exact",
                "FB08_gate_pairs": "FB08_gate_pairs",
                "FB08_gate_E1_signed_exact": "FB08_gate_signed_exact",
                "FB08_gate_plus_agreement_pairs": "FB08_gate_plus_SDT_agreement_pairs",
                "FB08_gate_plus_agreement_E1_signed_exact": "FB08_gate_plus_SDT_agreement_signed_exact",
            }
            for key, source_key in mapping.items():
                expect(actual[source_key], expected[key], f"{arm_name}.{key}")
            top_key = "FB08_gate_confidence_top_64_E1_signed_exact" if arm_name == "development_remainder" else "FB08_gate_confidence_top_7_E1_signed_exact"
            expect(actual["FB08_gate_confidence_top_same_gate_plus_agreement_count_signed_exact"],
                   expected[top_key], f"{arm_name}.{top_key}")
        actual = arms["development_remainder"]["summary"]
        expected = summary["nonpilot_development"]
        for key, source_key in {
            "SDT_with_E1_sign_signed_exact": "SDT_with_E1_sign_signed_exact_full",
            "E1_wrong_magnitudes": "E1_wrong_magnitudes",
            "E1_wrong_magnitudes_flagged": "E1_wrong_magnitudes_flagged",
            "E1_correct_magnitudes_reviewed": "E1_correct_magnitudes_reviewed",
        }.items():
            expect(actual[source_key], expected[key], f"development.{key}")
        checked.append("validation")
    if args.bootstrap is not None:
        expect(sha256(args.bootstrap), summary["ignored_artifact_sha256"]["collection_bootstrap"],
               "bootstrap artifact")
        bootstrap = json.loads(args.bootstrap.read_text(encoding="utf-8"))
        metric = bootstrap["metrics"]["sdt_minus_e1_signed_accuracy"]
        expected = summary["nonpilot_development"]
        if abs(metric["point"] * 100 - expected["cluster_bootstrap_SDT_minus_E1_signed_accuracy_pp"]) > 1e-10:
            raise ValueError("bootstrap point estimate mismatch")
        for actual, target in zip(metric["percentile_95_interval"],
                                  expected["cluster_bootstrap_95_interval_pp"]):
            if abs(actual * 100 - target) > 1e-10:
                raise ValueError("bootstrap interval mismatch")
        checked.append("bootstrap")
    if args.holdout is not None:
        expect(sha256(args.holdout),
               summary["ignored_artifact_sha256"]["retrospective_FB08_holdout_gate"],
               "holdout artifact")
        actual = json.loads(args.holdout.read_text(encoding="utf-8"))["summary"]
        expected = summary["retrospective_original_FB08_holdout_gate"]
        mapping = {
            "pairs": "pairs", "collections": "collections",
            "E1_signed_exact": "original_gate_E1_exact",
            "agreement_pairs": "agreement_kept",
            "agreement_E1_signed_exact": "agreement_kept_E1_exact",
            "wrong_gate_edges_reviewed": "wrong_gate_edges_reviewed",
            "correct_gate_edges_reviewed": "correct_gate_edges_reviewed",
            "gate_confidence_top_173_E1_signed_exact": "confidence_top_same_kept_count_E1_exact",
        }
        for key, source_key in mapping.items():
            expect(actual[source_key], expected[key], f"holdout.{key}")
        expect(actual["original_gate_E1_wrong"] - actual["wrong_gate_edges_reviewed"],
               expected["wrong_gate_edges_remaining"], "holdout remaining errors")
        checked.append("holdout")
    print(json.dumps({"status": "passed", "checked": checked}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
