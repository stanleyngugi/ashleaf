"""Frozen E1 evaluation against a selectively acquired resident pool."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Callable

import numpy as np

from .sparse_sampling import SparseRespoolSampler

ENCODE_SCALE = 1000.0
GRAD_MAG_FACTOR = 0.25
DECODE = ENCODE_SCALE / GRAD_MAG_FACTOR
LASAGNA_SCALE = 4.0
K_FROZEN = 2.773
ORIENT_FROZEN = 1


def ray_integral(
    sampler: SparseRespoolSampler,
    a_xyz_working: np.ndarray,
    b_xyz_working: np.ndarray,
    *,
    sample_vx: float = 2.0,
    lasagna_scale: float = LASAGNA_SCALE,
    decode: float = DECODE,
) -> tuple[float, bool]:
    """Numerically reproduce the frozen E1 trilinear ray integral."""

    a = np.asarray(a_xyz_working, dtype=np.float64)
    b = np.asarray(b_xyz_working, dtype=np.float64)
    distance = float(np.linalg.norm(b - a))
    if not (distance > 1e-9) or not math.isfinite(distance):
        return 0.0, True
    count = max(2, int(math.ceil(distance / sample_vx)) + 1)
    t = np.linspace(0.0, 1.0, count)
    points_xyz = a[None, :] * (1.0 - t)[:, None] + b[None, :] * t[:, None]
    points_zyx = points_xyz[:, ::-1] / lasagna_scale
    shape = np.asarray(sampler.index.array_shape)
    inside = np.all((points_zyx >= 0) & (points_zyx <= shape - 1), axis=1)
    if not inside.all():
        return float("inf"), False
    density = sampler.sample(points_zyx, quantize_uint8=True).astype(np.float64) / decode
    segment = distance / (count - 1)
    integral = np.sum(0.5 * (density[:-1] + density[1:]) * segment)
    return float(integral), True


def multiray(
    sampler: SparseRespoolSampler,
    a_xyz_working: np.ndarray,
    b_xyz_working: np.ndarray,
    *,
    m_rays: int = 7,
    max_offset_vx: float = 6.0,
) -> tuple[float, bool, int]:
    a = np.asarray(a_xyz_working, dtype=np.float64)
    b = np.asarray(b_xyz_working, dtype=np.float64)
    direction = b - a
    perpendicular = np.array([-direction[1], direction[0], 0.0])
    norm = float(np.linalg.norm(perpendicular))
    if norm < 1e-9:
        perpendicular = np.array([1.0, 0.0, 0.0])
    else:
        perpendicular /= norm
    values = []
    for offset in np.linspace(-max_offset_vx, max_offset_vx, m_rays):
        value, valid = ray_integral(
            sampler, a + perpendicular * offset, b + perpendicular * offset
        )
        if valid and math.isfinite(value):
            values.append(value)
    if not values:
        return float("inf"), False, 0
    return float(np.median(values)), True, len(values)


def load_umbilicus_axis(path: str | Path) -> tuple[Callable[[float], tuple[float, float]], int]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        for key in ("control_points", "points", "umbilicus", "data"):
            if key in data and isinstance(data[key], (list, dict)):
                data = data[key]
                break
    if isinstance(data, dict):
        data = list(data.values())
    points = []
    for item in data:
        if isinstance(item, dict):
            z, x, y = item.get("z"), item.get("x"), item.get("y")
            p = item.get("p")
            if p is not None and None in (z, x, y):
                x, y, z = float(p[0]), float(p[1]), float(p[2])
        else:
            x, y, z = float(item[0]), float(item[1]), float(item[2])
        if None not in (x, y, z):
            points.append((float(z), float(x), float(y)))
    if len(points) < 2:
        raise ValueError("umbilicus requires at least two valid control points")
    points.sort()
    z_values = np.asarray([point[0] for point in points])
    x_values = np.asarray([point[1] for point in points])
    y_values = np.asarray([point[2] for point in points])

    def axis_xy(z: float) -> tuple[float, float]:
        return (
            float(np.interp(z, z_values, x_values)),
            float(np.interp(z, z_values, y_values)),
        )

    return axis_xy, len(points)


def predict_pairs(
    sampler: SparseRespoolSampler,
    points_xyz_working: np.ndarray,
    pairs: dict[str, np.ndarray],
    umbilicus_path: str | Path,
    *,
    k: float = K_FROZEN,
    orient: int = ORIENT_FROZEN,
    progress_every: int = 1000,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, object]]:
    """Return frozen E1 predictions, answered mask, confidence, and stats."""

    axis_xy, control_points = load_umbilicus_axis(umbilicus_path)
    points = np.asarray(points_xyz_working, dtype=np.float64)
    count = len(pairs["dw"])
    predictions = np.zeros(count, dtype=np.float64)
    answered = np.zeros(count, dtype=bool)
    confidence = np.zeros(count, dtype=np.float64)
    valid_ray_histogram: dict[int, int] = {}
    zero_radial_sign = 0
    for ordinal, (a_index, b_index) in enumerate(zip(pairs["a"], pairs["b"])):
        a, b = points[a_index], points[b_index]
        value, valid, valid_rays = multiray(sampler, a, b)
        valid_ray_histogram[valid_rays] = valid_ray_histogram.get(valid_rays, 0) + 1
        if not valid:
            continue
        axis_x, axis_y = axis_xy(0.5 * (a[2] + b[2]))
        radius_a = float(np.hypot(a[0] - axis_x, a[1] - axis_y))
        radius_b = float(np.hypot(b[0] - axis_x, b[1] - axis_y))
        radial_sign = 1 if radius_b > radius_a else (-1 if radius_b < radius_a else 0)
        if radial_sign == 0:
            zero_radial_sign += 1
            continue
        scaled = k * value
        predictions[ordinal] = round(scaled) * (orient * radial_sign)
        answered[ordinal] = True
        confidence[ordinal] = 1.0 - 2.0 * abs(scaled - round(scaled))
        if progress_every and (ordinal + 1) % progress_every == 0:
            print(
                f"evaluated {ordinal + 1:,}/{count:,} pairs; "
                f"answered {int(answered[:ordinal + 1].sum()):,}",
                flush=True,
            )
    return predictions, answered, confidence, {
        "k": k,
        "orient": int(orient),
        "frozen": True,
        "source": "winding-ruler concordance v1_5",
        "pairs": count,
        "answered": int(answered.sum()),
        "umbilicus_control_points": control_points,
        "zero_radial_sign": zero_radial_sign,
        "valid_ray_histogram": dict(sorted(valid_ray_histogram.items())),
    }
