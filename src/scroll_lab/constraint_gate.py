"""Reason-coded, conservative FB08 relative-winding proposal gate.

This rule is selected on FB08 development collections only. It says whether
the available evidence supports *emitting a nonzero relative constraint*;
withholding never asserts that two endpoints are on the same wrap. A verified
registration is required before an eligible proposal can be exported.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


NORMAL_MIN_ACCEPT = 0.75
NORMAL_MIN_REVIEW = 0.50
E1_CONFIDENCE_ACCEPT = 0.75


@dataclass(frozen=True)
class ConstraintGateDecision:
    action: str  # accept, review, withhold
    reason: str
    numeric_eligible: bool


def decide_relative_constraint(
    *, answered: bool, predicted_dw: int | None, e1_confidence: float | None,
    both_normals_valid: bool, normal_chord_dot_min: float | None,
    registration_verified: bool,
) -> ConstraintGateDecision:
    """Apply frozen numeric thresholds, then the external frame safety latch."""

    if not answered:
        return ConstraintGateDecision("withhold", "E1_UNANSWERED", False)
    if predicted_dw is None or type(predicted_dw) is not int:
        raise ValueError("answered E1 proposal must have an integer winding difference")
    if predicted_dw == 0:
        return ConstraintGateDecision("withhold", "ZERO_RELATIVE_PROPOSAL", False)
    if not both_normals_valid:
        return ConstraintGateDecision("withhold", "NORMAL_FIELD_UNAVAILABLE", False)
    if normal_chord_dot_min is None or not math.isfinite(normal_chord_dot_min) or not 0 <= normal_chord_dot_min <= 1:
        raise ValueError("valid endpoints require a finite normal alignment in [0,1]")
    if normal_chord_dot_min < NORMAL_MIN_REVIEW:
        return ConstraintGateDecision("withhold", "CHORD_TANGENTIAL_TO_SHEET", False)
    if normal_chord_dot_min < NORMAL_MIN_ACCEPT:
        return ConstraintGateDecision("review", "CHORD_ALIGNMENT_BORDERLINE", False)
    if e1_confidence is None or not math.isfinite(e1_confidence) or not 0 <= e1_confidence <= 1:
        raise ValueError("answered E1 proposal requires confidence in [0,1]")
    if e1_confidence < E1_CONFIDENCE_ACCEPT:
        return ConstraintGateDecision("review", "E1_CONFIDENCE_LOW", False)
    if not registration_verified:
        return ConstraintGateDecision("review", "FRAME_REGISTRATION_UNVERIFIED", True)
    return ConstraintGateDecision("accept", "ACCEPT_RELATIVE_CONSTRAINT", True)
