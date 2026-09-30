#!/usr/bin/env python3
"""Export a truth-blind, research-only FB15 magnitude-disagreement review queue."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scroll_lab.constraint_gate import ConstraintGateDecision
from scroll_lab.sdt_review import decide_sdt_review


BASE = ConstraintGateDecision("review", "FRAME_REGISTRATION_UNVERIFIED", True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_queue(rows: list[dict]) -> list[dict]:
    """Whitelist only prediction-side evidence; never read human truth fields."""

    queue = []
    for row in rows:
        decision = decide_sdt_review(
            base=BASE,
            predicted_dw=row["e1_predicted_dw"],
            crest_magnitude=row["sdt_crest_magnitude"],
            ray_counts=row["sdt_ray_counts"],
        )
        if decision.research_agreement:
            continue
        queue.append({
            "id": row["id"], "collection_id": row["collection_id"],
            "e1_predicted_dw": row["e1_predicted_dw"],
            "e1_confidence": row["e1_confidence"],
            "sdt_crest_magnitude": decision.crest_magnitude,
            "sdt_ray_counts": list(decision.ray_counts),
            "sdt_ray_count_range": decision.ray_count_range,
            "action": decision.action, "reason": decision.reason,
            "numeric_export_permitted": decision.numeric_export_permitted,
        })
    queue.sort(key=lambda row: (-row["e1_confidence"], row["collection_id"], row["id"]))
    for rank, row in enumerate(queue, start=1):
        row["review_priority_rank"] = rank
    return queue


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fb15-freeze", type=Path, required=True)
    parser.add_argument("--retrospective-holdout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    freeze = json.loads(args.fb15_freeze.read_text(encoding="utf-8"))
    source = json.loads(args.retrospective_holdout.read_text(encoding="utf-8"))
    if (freeze.get("kind") != "FB15_sdt_crest_v1_freeze"
            or source.get("experiment") != "FB15_retrospective_original_FB08_holdout_gate"
            or source["provenance_sha256"]["freeze"] != sha256(args.fb15_freeze)
            or source["summary"]["pairs"] != 207
            or len(source["rows"]) != 207):
        raise ValueError("FB15 review queue source mismatch")
    queue = build_queue(source["rows"])
    if len(queue) != source["summary"]["pairs"] - source["summary"]["agreement_kept"]:
        raise ValueError("review queue count does not match fixed SDT agreement rule")
    output = {
        "schema_version": 1,
        "kind": "FB15_truth_blind_research_review_queue",
        "status": "retrospective_source_truth_fields_explicitly_excluded_no_production_export",
        "fb15_freeze_sha256": sha256(args.fb15_freeze),
        "source_result_sha256": sha256(args.retrospective_holdout),
        "ranking": "descending_E1_confidence_then_collection_and_ID_no_truth_used",
        "candidate_count": source["summary"]["pairs"],
        "review_count": len(queue),
        "queue": queue,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"candidates": output["candidate_count"],
                      "review_count": output["review_count"],
                      "reasons": {reason: sum(item["reason"] == reason for item in queue)
                                  for reason in sorted({item["reason"] for item in queue})},
                      "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
