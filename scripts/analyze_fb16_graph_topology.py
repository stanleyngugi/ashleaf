#!/usr/bin/env python3
"""Post-hoc explain why FB16 edge reweighting rarely changes assignments."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from scroll_lab.weighted_winding import solve_weighted_winding
from scroll_lab.winding import RelativeConstraint


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def has_alternative_path(edges: list[tuple[str, str, str]], tested: int) -> bool:
    """True if tested edge lies in a cycle, including a parallel-edge cycle."""

    start, target, _ = edges[tested]
    adjacency: dict[str, set[str]] = defaultdict(set)
    for index, (a, b, _) in enumerate(edges):
        if index == tested:
            continue
        adjacency[a].add(b)
        adjacency[b].add(a)
    queue = [start]
    seen = {start}
    for node in queue:
        for neighbour in adjacency[node]:
            if neighbour == target:
                return True
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--holdout-e1", type=Path, required=True)
    parser.add_argument("--sdt-holdout", type=Path, required=True)
    parser.add_argument("--fb16-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidates = json.loads(args.candidates.read_text(encoding="utf-8"))
    e1 = json.loads(args.holdout_e1.read_text(encoding="utf-8"))
    sdt = json.loads(args.sdt_holdout.read_text(encoding="utf-8"))
    fb16 = json.loads(args.fb16_result.read_text(encoding="utf-8"))
    if (fb16.get("experiment") != "FB16_retrospective_SDT_soft_graph"
            or fb16["input_sha256"]["candidates"] != sha256(args.candidates)
            or fb16["input_sha256"]["holdout_e1"] != sha256(args.holdout_e1)
            or fb16["input_sha256"]["sdt_holdout"] != sha256(args.sdt_holdout)):
        raise ValueError("FB16 topology provenance mismatch")
    by_e1 = {row["id"]: row for row in e1["arms"]["relative"]["rows"]}
    by_sdt = {row["id"]: row for row in sdt["rows"]}
    by_collection = defaultdict(list)
    for candidate in candidates["arms"]["relative"]["candidates"]:
        if candidate["partition"] != "holdout":
            continue
        prior = by_e1[candidate["id"]]
        if prior["answered"] and prior["predicted_dw"] not in (None, 0):
            by_collection[str(candidate["collection_id"])].append((
                str(candidate["a_point_id"]), str(candidate["b_point_id"]), candidate["id"]))
    per_collection = []
    for collection_id, edges in sorted(by_collection.items(), key=lambda item: int(item[0])):
        bridge_ids = {edge_id for index, (_, _, edge_id) in enumerate(edges)
                      if not has_alternative_path(edges, index)}
        flagged = {edge_id for _, _, edge_id in edges
                   if edge_id in by_sdt and not by_sdt[edge_id]["magnitude_agreement"]}
        gate_ids = {edge_id for _, _, edge_id in edges if edge_id in by_sdt}
        solved = solve_weighted_winding([
            RelativeConstraint(a, b, int(by_e1[edge_id]["predicted_dw"]),
                               float(by_e1[edge_id]["e1_confidence"]), edge_id)
            for a, b, edge_id in edges])
        flagged_residuals = {}
        for a, b, edge_id in edges:
            if edge_id in flagged:
                flagged_residuals[edge_id] = (
                    solved.labels[b] - solved.labels[a] - int(by_e1[edge_id]["predicted_dw"]))
        wrong_flagged = {edge_id for edge_id in flagged
                         if not by_sdt[edge_id]["e1_signed_exact"]}
        correct_flagged = flagged - wrong_flagged
        per_collection.append({
            "collection_id": collection_id, "E1_edges": len(edges),
            "E1_bridges": len(bridge_ids), "gate_edges": len(gate_ids),
            "gate_bridges": len(gate_ids & bridge_ids), "flagged_edges": len(flagged),
            "flagged_bridges": len(flagged & bridge_ids),
            "flagged_wrong_bridges": sum(
                not by_sdt[edge_id]["e1_signed_exact"] for edge_id in flagged & bridge_ids),
            "flagged_wrong_cycle_edges": sum(
                not by_sdt[edge_id]["e1_signed_exact"] for edge_id in flagged - bridge_ids),
            "wrong_flagged_baseline_solver_agrees_with_E1": sum(
                flagged_residuals[edge_id] == 0 for edge_id in wrong_flagged),
            "correct_flagged_baseline_solver_agrees_with_E1": sum(
                flagged_residuals[edge_id] == 0 for edge_id in correct_flagged),
        })
    totals = {key: sum(row[key] for row in per_collection) for key in (
        "E1_edges", "E1_bridges", "gate_edges", "gate_bridges", "flagged_edges",
        "flagged_bridges", "flagged_wrong_bridges", "flagged_wrong_cycle_edges",
        "wrong_flagged_baseline_solver_agrees_with_E1",
        "correct_flagged_baseline_solver_agrees_with_E1")}
    output = {
        "experiment": "FB16_posthoc_edge_topology",
        "status": "mechanistic_diagnostic_after_outcomes_not_a_new_frozen_comparison",
        "input_sha256": {
            "candidates": sha256(args.candidates), "holdout_e1": sha256(args.holdout_e1),
            "sdt_holdout": sha256(args.sdt_holdout), "fb16_result": sha256(args.fb16_result),
        },
        "summary": {**totals, "collections": len(per_collection)},
        "per_collection": per_collection,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
