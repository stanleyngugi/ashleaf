"""Opt-in FB15 research review adapter for a frozen FB08 gate decision.

This adapter never authorizes production numeric export. A crest is a field
feature, not a verified physical sheet crossing; agreement is a research cue.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .constraint_gate import ConstraintGateDecision


@dataclass(frozen=True)
class SDTReviewDecision:
    action: str  # review or withhold; never accept
    reason: str
    base_reason: str
    research_agreement: bool
    numeric_export_permitted: bool
    crest_magnitude: int | None
    ray_counts: tuple[int, ...]
    ray_count_range: int | None


def decide_sdt_review(
    *,
    base: ConstraintGateDecision,
    predicted_dw: int | None,
    crest_magnitude: int | None,
    ray_counts: Sequence[int] | None,
) -> SDTReviewDecision:
    """Add a reason-coded magnitude review without weakening the FB08 gate.

    Missing ray data is reviewed, never treated as a zero-winding label. The
    ``research_agreement`` flag is useful for controlled analysis only; the
    export latch stays closed regardless of input registration status.
    """

    if predicted_dw is not None and type(predicted_dw) is not int:
        raise ValueError("predicted winding difference must be an integer or None")
    if crest_magnitude is not None and (type(crest_magnitude) is not int or crest_magnitude < 0):
        raise ValueError("crest magnitude must be nonnegative integer or None")
    counts = tuple(ray_counts) if ray_counts is not None else ()
    if any(type(count) is not int or count < 0 for count in counts):
        raise ValueError("ray counts must be nonnegative integers")
    count_range = max(counts) - min(counts) if counts else None

    if not base.numeric_eligible:
        return SDTReviewDecision(
            action=base.action, reason=base.reason, base_reason=base.reason,
            research_agreement=False, numeric_export_permitted=False,
            crest_magnitude=crest_magnitude, ray_counts=counts, ray_count_range=count_range,
        )
    if predicted_dw in (None, 0):
        raise ValueError("numeric-eligible FB08 decision requires nonzero E1 prediction")
    if crest_magnitude is None or len(counts) != 7:
        reason = "SDT_RAYS_UNAVAILABLE"
        agreement = False
    elif crest_magnitude == 0:
        reason = "SDT_ZERO_CREST_REVIEW"
        agreement = False
    elif crest_magnitude != abs(predicted_dw):
        reason = "SDT_MAGNITUDE_DISAGREEMENT"
        agreement = False
    else:
        reason = "SDT_MAGNITUDE_AGREEMENT_RESEARCH_ONLY"
        agreement = True
    return SDTReviewDecision(
        action="review", reason=reason, base_reason=base.reason,
        research_agreement=agreement, numeric_export_permitted=False,
        crest_magnitude=crest_magnitude, ray_counts=counts, ray_count_range=count_range,
    )
