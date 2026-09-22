#!/usr/bin/env python3
"""Render the FB07 macro accuracy-coverage curve as dependency-free SVG."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

METHODS = (
    ("distance_only", "Distance only", "#2563eb"),
    ("native_confidence", "Native E1 confidence", "#dc2626"),
    ("geometry_logistic", "Geometry logistic", "#15803d"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = json.loads(args.input.read_text(encoding="utf-8"))
    if result.get("evidence_class") != "internal_loso_post_FB06":
        raise ValueError("input is not the FB07 internal LOSO result")
    coverages = [float(item) for item in result["coverages"]]

    width, height = 980, 620
    left, right, top, bottom = 105, 35, 95, 90
    plot_w, plot_h = width - left - right, height - top - bottom
    y_min, y_max = 0.40, 1.00

    def sx(value):
        return left + (value - 0.10) / 0.90 * plot_w

    def sy(value):
        return top + (y_max - value) / (y_max - y_min) * plot_h

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#172033}.title{font-size:25px;font-weight:700}.sub{font-size:14px;fill:#526071}.axis{font-size:14px}.tick{font-size:12px;fill:#526071}.legend{font-size:13px}</style>',
        '<text class="title" x="105" y="39">FrameBridge FB07: accuracy–coverage transfer</text>',
        '<text class="sub" x="105" y="65">Four leave-one-segment-out rotations · macro exact accuracy · internal post-FB06 cross-validation</text>',
    ]
    for value in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        y = sy(value)
        lines.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="#d9dee8" stroke-width="1"/>')
        lines.append(f'<text class="tick" x="{left - 14}" y="{y + 4:.1f}" text-anchor="end">{value:.1f}</text>')
    for value in coverages:
        x = sx(value)
        lines.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" stroke="#eef1f5" stroke-width="1"/>')
        lines.append(f'<text class="tick" x="{x:.1f}" y="{top + plot_h + 25}" text-anchor="middle">{int(value * 100)}%</text>')
    lines.extend([
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#172033" stroke-width="1.5"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#172033" stroke-width="1.5"/>',
        f'<text class="axis" x="{left + plot_w / 2}" y="{height - 26}" text-anchor="middle">Selected coverage</text>',
        f'<text class="axis" transform="translate(27 {top + plot_h / 2}) rotate(-90)" text-anchor="middle">Macro exact dw=1 accuracy</text>',
    ])
    for method, label, color in METHODS:
        values = [result["aggregate"][method][f"{coverage:.2f}"]["macro_mean_accuracy"] for coverage in coverages]
        points = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in zip(coverages, values))
        lines.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
        for x, y in zip(coverages, values):
            lines.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>')
    legend_x, legend_y = 565, 118
    lines.append(f'<rect x="{legend_x - 15}" y="{legend_y - 25}" width="315" height="92" rx="7" fill="#ffffff" stroke="#cbd3df"/>')
    for index, (_, label, color) in enumerate(METHODS):
        y = legend_y + index * 25
        lines.append(f'<line x1="{legend_x}" y1="{y}" x2="{legend_x + 28}" y2="{y}" stroke="{color}" stroke-width="3"/>')
        lines.append(f'<text class="legend" x="{legend_x + 38}" y="{y + 4}">{label}</text>')
    lines.append(f'<text class="sub" x="{left}" y="{height - 5}">Full-coverage convergence is expected: ranking changes selection, not the frozen E1 predictions.</text>')
    lines.append('</svg>')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "methods": len(METHODS), "points_per_method": len(coverages)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
