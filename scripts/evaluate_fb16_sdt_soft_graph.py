#!/usr/bin/env python3
"""FB16 retrospective fixed-connectivity SDT review in a CPU winding solver."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
from itertools import combinations
import json
from pathlib import Path

from scroll_lab.constraint_gate import decide_relative_constraint
from scroll_lab.pointcollections import load_pointcollections
from scroll_lab.provenance import matches_frozen_text_sha256
from scroll_lab.weighted_winding import solve_weighted_winding
from scroll_lab.winding import RelativeConstraint


ARMS = ("confidence_weight", "SDT_disagreement_x0p25",
        "confidence_low_x0p25", "hash_null_x0p25")
FACTOR = 0.25


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def selected_ids(rows: list[dict], flagged: set[str]) -> dict[str, set[str]]:
    """Match flagged gate-edge count within each collection for two controls."""

    gate = [row for row in rows if row["gate_eligible"]]
    count = sum(row["id"] in flagged for row in gate)
    if count != len(flagged & {row["id"] for row in gate}):
        raise AssertionError("flag count changed")
    return {
        "confidence_weight": set(),
        "SDT_disagreement_x0p25": {row["id"] for row in gate if row["id"] in flagged},
        "confidence_low_x0p25": {row["id"] for row in sorted(
            gate, key=lambda row: (row["e1_confidence"], row["id"]))[:count]},
        "hash_null_x0p25": {row["id"] for row in sorted(
            gate, key=lambda row: hashlib.sha256(
                f"FB16-null-v1:{row['id']}".encode("utf-8")).digest())[:count]},
    }


def score_collection(rows: list[dict], truth: dict[str, int], downweighted: set[str]) -> dict:
    """Score all connected node pairs with the same edge graph in every arm."""

    nodes = {str(row[key]) for row in rows for key in ("a_point_id", "b_point_id")}
    edges = [RelativeConstraint(
        str(row["a_point_id"]), str(row["b_point_id"]),
        int(row["predicted_dw"]), float(row["e1_confidence"]), row["id"])
        for row in rows if row["e1_all"]]
    if not downweighted <= {edge.evidence_id for edge in edges}:
        raise ValueError("downweighted ID not present in E1 edge graph")
    multipliers = {edge_id: FACTOR for edge_id in downweighted}
    solved = solve_weighted_winding(edges, multipliers=multipliers)
    parent = {node: node for node in nodes}

    def root(node: str) -> str:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for edge in edges:
        a, b = root(edge.source), root(edge.target)
        if a != b:
            parent[b] = a
    comparable = correct = absolute_error = 0
    digest = hashlib.sha256()
    for a, b in combinations(sorted(nodes), 2):
        if root(a) != root(b):
            continue
        comparable += 1
        difference = solved.labels[b] - solved.labels[a]
        digest.update(f"{a}\t{b}\t{difference}\n".encode("utf-8"))
        error = difference - truth[b] + truth[a]
        correct += int(error == 0)
        absolute_error += abs(error)
    return {
        "nodes": len(nodes), "E1_edges": len(edges), "downweighted_gate_edges": len(downweighted),
        "possible_node_pairs": len(nodes) * (len(nodes) - 1) // 2,
        "comparable_node_pairs": comparable, "exact_comparable_node_pairs": correct,
        "absolute_pairwise_error_sum": absolute_error,
        "weighted_squared_edge_residual": solved.weighted_squared_residual,
        "assignment_sha256": digest.hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fb08-freeze", type=Path, required=True)
    parser.add_argument("--fb15-freeze", type=Path, required=True)
    parser.add_argument("--protocol-freeze", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--holdout-e1", type=Path, required=True)
    parser.add_argument("--normals", type=Path, required=True)
    parser.add_argument("--sdt-holdout", type=Path, required=True)
    parser.add_argument("--relative-annotations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    fb08 = json.loads(args.fb08_freeze.read_text(encoding="utf-8"))
    fb15 = json.loads(args.fb15_freeze.read_text(encoding="utf-8"))
    protocol = json.loads(args.protocol_freeze.read_text(encoding="utf-8"))
    candidates = json.loads(args.candidates.read_text(encoding="utf-8"))
    e1 = json.loads(args.holdout_e1.read_text(encoding="utf-8"))
    normals = json.loads(args.normals.read_text(encoding="utf-8"))
    sdt = json.loads(args.sdt_holdout.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[1]
    if (protocol.get("kind") != "FB16_sdt_soft_graph_freeze"
            or protocol["scorer_source_sha256"] != sha256(Path(__file__))
            or protocol["downweight_factor"] != FACTOR
            or protocol["arms"] != list(ARMS)
            or protocol["input_sha256"] != {
                "fb08_freeze": sha256(args.fb08_freeze),
                "fb15_freeze": sha256(args.fb15_freeze),
                "candidates": sha256(args.candidates),
                "holdout_e1": sha256(args.holdout_e1),
                "normals": sha256(args.normals),
                "sdt_holdout": sha256(args.sdt_holdout),
                "relative_annotations": sha256(args.relative_annotations),
            }):
        raise ValueError("FB16 local protocol/input freeze mismatch")
    if (fb08.get("kind") != "FB08_mixed_constraint_gate_protocol_freeze"
            or not matches_frozen_text_sha256(
                root / "src/scroll_lab/constraint_gate.py", fb08["gate_source_sha256"])
            or not matches_frozen_text_sha256(args.candidates, fb08["candidate_manifest_sha256"])
            or not matches_frozen_text_sha256(args.normals, fb08["normal_features_sha256"])
            or fb15.get("kind") != "FB15_sdt_crest_v1_freeze"
            or sha256(root / fb15["rule_source"]) != fb15["rule_source_sha256"]
            or e1.get("partition") != "holdout"
            or e1["protocol_freeze_sha256"] != sha256(args.fb08_freeze)
            or sdt.get("experiment") != "FB15_retrospective_original_FB08_holdout_gate"
            or sdt["provenance_sha256"]["freeze"] != sha256(args.fb15_freeze)
            or sdt["provenance_sha256"]["holdout_e1"] != sha256(args.holdout_e1)
            or candidates["arms"]["relative"]["source_sha256"]
               != sha256(args.relative_annotations)):
        raise ValueError("FB08/FB15 source provenance mismatch")
    by_e1 = {row["id"]: row for row in e1["arms"]["relative"]["rows"]}
    by_normal = {row["id"]: row for row in normals["arms"]["relative"]["rows"]
                 if row["partition"] == "holdout"}
    by_sdt = {row["id"]: row for row in sdt["rows"]}
    if len(by_sdt) != 207:
        raise ValueError("original FB08 gate SDT population changed")
    flagged = {row["id"] for row in by_sdt.values() if not row["magnitude_agreement"]}
    if len(flagged) != 34:
        raise ValueError("FB15 gate disagreement count changed")
    by_collection: dict[str, list[dict]] = defaultdict(list)
    gate_ids = set()
    for pair in candidates["arms"]["relative"]["candidates"]:
        if pair["partition"] != "holdout":
            continue
        prior, normal = by_e1[pair["id"]], by_normal[pair["id"]]
        decision = decide_relative_constraint(
            answered=prior["answered"], predicted_dw=prior["predicted_dw"],
            e1_confidence=prior["e1_confidence"],
            both_normals_valid=normal["both_normals_valid"],
            normal_chord_dot_min=normal["normal_chord_dot_min"],
            registration_verified=False,
        )
        if decision.numeric_eligible:
            gate_ids.add(pair["id"])
            if (pair["id"] not in by_sdt
                    or by_sdt[pair["id"]]["e1_predicted_dw"] != prior["predicted_dw"]):
                raise ValueError(f"SDT/E1 original gate mismatch: {pair['id']}")
        by_collection[str(pair["collection_id"])].append({
            **pair, "predicted_dw": prior["predicted_dw"],
            "e1_confidence": prior["e1_confidence"],
            "e1_all": bool(prior["answered"] and prior["predicted_dw"] not in (None, 0)),
            "gate_eligible": decision.numeric_eligible,
        })
    if gate_ids != set(by_sdt):
        raise ValueError("SDT result is not exactly the original FB08 gate")

    annotations = load_pointcollections(args.relative_annotations)
    arm_rows: dict[str, list[dict]] = {arm: [] for arm in ARMS}
    for collection_id, rows in sorted(by_collection.items(), key=lambda item: int(item[0])):
        truth = {str(pid): int(point["wind_a"])
                 for pid, point in annotations["collections"][collection_id]["points"].items()}
        chosen = selected_ids(rows, flagged)
        if len({len(chosen[arm]) for arm in ARMS[1:]}) != 1:
            raise AssertionError("matched controls changed review count")
        for arm in ARMS:
            result = score_collection(rows, truth, chosen[arm])
            result["collection_id"] = collection_id
            arm_rows[arm].append(result)

    arms = {}
    for arm in ARMS:
        rows = arm_rows[arm]
        totals = {key: sum(row[key] for row in rows) for key in (
            "nodes", "E1_edges", "downweighted_gate_edges", "possible_node_pairs",
            "comparable_node_pairs", "exact_comparable_node_pairs",
            "absolute_pairwise_error_sum", "weighted_squared_edge_residual")}
        totals["collections"] = len(rows)
        totals["exact_over_comparable"] = (
            totals["exact_comparable_node_pairs"] / totals["comparable_node_pairs"])
        totals["pairwise_mae"] = (
            totals["absolute_pairwise_error_sum"] / totals["comparable_node_pairs"])
        totals["pairwise_coverage"] = (
            totals["comparable_node_pairs"] / totals["possible_node_pairs"])
        totals["per_collection"] = rows
        arms[arm] = totals
    baseline = arms["confidence_weight"]
    for arm in ARMS[1:]:
        treatment = arms[arm]
        for key in ("nodes", "E1_edges", "possible_node_pairs", "comparable_node_pairs"):
            if treatment[key] != baseline[key]:
                raise AssertionError(f"{arm} changed graph {key}")
        treatment["delta_exact_pairs_vs_baseline"] = (
            treatment["exact_comparable_node_pairs"] - baseline["exact_comparable_node_pairs"])
        treatment["delta_absolute_error_vs_baseline"] = (
            treatment["absolute_pairwise_error_sum"] - baseline["absolute_pairwise_error_sum"])
        treatment["changed_assignment_collections"] = [
            t["collection_id"] for b, t in zip(baseline["per_collection"], treatment["per_collection"])
            if b["assignment_sha256"] != t["assignment_sha256"]]
        treatment["per_collection_delta"] = [
            {"collection_id": b["collection_id"],
             "delta_exact_pairs": t["exact_comparable_node_pairs"] - b["exact_comparable_node_pairs"],
             "delta_absolute_error": t["absolute_pairwise_error_sum"] - b["absolute_pairwise_error_sum"]}
            for b, t in zip(baseline["per_collection"], treatment["per_collection"])
            if b["assignment_sha256"] != t["assignment_sha256"]]
    output = {
        "experiment": "FB16_retrospective_SDT_soft_graph",
        "status": "exploratory_not_official_fitter_not_blind_no_production_export",
        "protocol_freeze_sha256": sha256(args.protocol_freeze),
        "input_sha256": protocol["input_sha256"],
        "fixed_downweight_factor": FACTOR,
        "flagged_original_gate_edges": len(flagged),
        "original_gate_edges": len(gate_ids),
        "solver_arms": arms,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({arm: {key: value for key, value in result.items()
                            if key not in ("per_collection", "per_collection_delta")}
                      for arm, result in arms.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
