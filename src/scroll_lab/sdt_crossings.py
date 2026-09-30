"""Exploratory sheet-crest count in the public surface-SDT field.

This estimates a *magnitude cue*, not a signed winding relation. Its v1 rule
was selected on a small FB08 development pilot and must not be treated as an
official ground truth or production constraint without further validation.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks


V1_HEIGHT = 130.0
V1_PROMINENCE = 2.0
V1_MIN_DISTANCE_SAMPLES = 6


def crest_count_v1(values_u8: list[int] | np.ndarray) -> int:
    """Count prominent positive lobes on one SDT ray at 1 working-voxel steps."""

    values = np.asarray(values_u8, dtype=np.float64)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("SDT ray must contain finite one-dimensional values")
    if len(values) < 3:
        return 0
    smoothed = np.convolve(values, np.asarray([0.25, 0.5, 0.25]), mode="same")
    peaks, _ = find_peaks(
        smoothed, height=V1_HEIGHT, prominence=V1_PROMINENCE,
        distance=V1_MIN_DISTANCE_SAMPLES,
    )
    return int(len(peaks))


def multiray_crest_magnitude_v1(profiles: list[list[int]]) -> tuple[int, list[int]]:
    """Use the rounded median of seven ray counts as a nonnegative cue."""

    if len(profiles) != 7:
        raise ValueError("v1 requires exactly seven valid SDT rays")
    counts = [crest_count_v1(profile) for profile in profiles]
    return int(np.rint(np.median(counts))), counts
