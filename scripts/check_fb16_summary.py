#!/usr/bin/env python3
"""Verify tracked FB16 summary against its freeze and optional ignored results."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expect(actual: object, wanted: object, label: str) -> None:
    if actual != wanted:
        raise ValueError(f"{label}: expected {wanted!r}, got {actual!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path,
                        default=Path("experiments/results/framebridge_fb16_summary.json"))
    parser.add_argument("--freeze", type=Path,
                        default=Path("protocols/FB16_sdt_soft_graph_freeze.json"))
    parser.add_argument("--fixed-graph", type=Path)
    parser.add_argument("--topology", type=Path)
    parser.add_argument("--oracle", type=Path)
    parser.add_argument("--review-queue", type=Path)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    freeze = json.loads(args.freeze.read_text(encoding="utf-8"))
    expect(summary["experiment"], "FB16_retrospective_SDT_soft_graph", "experiment")
    expect(sha256(args.freeze), summary["protocol_freeze_sha256"], "protocol freeze hash")
    root = Path(__file__).resolve().parents[1]
    expect(sha256(root / freeze["scorer_source"]), freeze["scorer_source_sha256"],
           "frozen scorer source")
    checked = ["freeze", "scorer_source"]
    if args.fixed_graph is not None:
        expect(sha256(args.fixed_graph), summary["ignored_artifact_sha256"]["fixed_graph"],
               "fixed graph hash")
        result = json.loads(args.fixed_graph.read_text(encoding="utf-8"))
        expect(result["experiment"], summary["experiment"], "fixed graph experiment")
        population = summary["population"]
        expect(result["original_gate_edges"], population["original_FB08_gate_edges"],
               "original gate edges")
        expect(result["flagged_original_gate_edges"], population["SDT_flagged_gate_edges"],
               "flagged gate edges")
        for arm, expected in summary["arms"].items():
            actual = result["solver_arms"][arm]
            expect(actual["collections"], population["collections"], f"{arm}.collections")
            expect(actual["E1_edges"], population["E1_edges"], f"{arm}.E1_edges")
            expect(actual["comparable_node_pairs"], population["comparable_node_pairs_all_arms"],
                   f"{arm}.comparable")
            expect(actual["possible_node_pairs"], population["possible_node_pairs_all_arms"],
                   f"{arm}.possible")
            expect(actual["exact_comparable_node_pairs"], expected["exact_pairs"],
                   f"{arm}.exact")
            expect(actual["absolute_pairwise_error_sum"], expected["absolute_error_sum"],
                   f"{arm}.absolute_error")
            if "changed_assignment_collections" in expected:
                expect(len(actual["changed_assignment_collections"]),
                       expected["changed_assignment_collections"], f"{arm}.changed_collections")
        checked.append("fixed_graph")
    if args.topology is not None:
        expect(sha256(args.topology), summary["ignored_artifact_sha256"]["posthoc_topology"],
               "topology hash")
        actual = json.loads(args.topology.read_text(encoding="utf-8"))["summary"]
        mechanism = summary["posthoc_mechanism"]
        expect(actual["flagged_edges"] - actual["flagged_bridges"],
               mechanism["flagged_edges_in_cycles"], "flagged cycle edges")
        expect(actual["wrong_flagged_baseline_solver_agrees_with_E1"]
               + actual["correct_flagged_baseline_solver_agrees_with_E1"],
               mechanism["flagged_edges_baseline_rounded_solver_agrees_with_E1"],
               "flagged solver agreement")
        expect(actual["wrong_flagged_baseline_solver_agrees_with_E1"],
               mechanism["wrong_flagged_edges_baseline_rounded_solver_agrees_with_E1"],
               "wrong flagged solver agreement")
        checked.append("topology")
    if args.oracle is not None:
        expect(sha256(args.oracle), summary["ignored_artifact_sha256"]["posthoc_oracle"],
               "oracle hash")
        actual = json.loads(args.oracle.read_text(encoding="utf-8"))["summary"]["oracle_flagged_wrong_10"]
        mechanism = summary["posthoc_mechanism"]
        expect(actual["exact_comparable_node_pairs"],
               mechanism["oracle_correct_10_flagged_wrong_exact_pairs"], "oracle exact")
        expect(actual["absolute_pairwise_error_sum"],
               mechanism["oracle_correct_10_flagged_wrong_absolute_error_sum"], "oracle error")
        checked.append("oracle")
    if args.review_queue is not None:
        expect(sha256(args.review_queue),
               summary["ignored_artifact_sha256"]["truth_blind_review_queue"], "queue hash")
        queue = json.loads(args.review_queue.read_text(encoding="utf-8"))
        expected = summary["review_queue"]
        expect(len(queue["queue"]), expected["rows"], "queue rows")
        expect(sum(row["reason"] == "SDT_MAGNITUDE_DISAGREEMENT" for row in queue["queue"]),
               expected["magnitude_disagreement"], "magnitude review rows")
        expect(sum(row["reason"] == "SDT_ZERO_CREST_REVIEW" for row in queue["queue"]),
               expected["zero_crest_review"], "zero crest rows")
        expect(sum(any("truth" in key or "exact" in key for key in row) for row in queue["queue"]),
               expected["truth_fields"], "truth field leak")
        expect(any(row["numeric_export_permitted"] for row in queue["queue"]),
               expected["numeric_export_permitted"], "queue export latch")
        checked.append("review_queue")
    print(json.dumps({"status": "passed", "checked": checked}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
