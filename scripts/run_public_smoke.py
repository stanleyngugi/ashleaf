#!/usr/bin/env python3
"""One-command, pinned-data smoke check for the September reliability toolkit."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scroll_lab.fit_window import preflight_fit_window  # noqa: E402
from scroll_lab.pointcollections import audit_pointcollections, load_pointcollections  # noqa: E402
from scroll_lab.tifxyz import audit_tifxyz  # noqa: E402
from scroll_lab.zarr_meta import audit_omezarr_v2  # noqa: E402
from scroll_lab.zarr_roi import plan_roi  # noqa: E402

from fetch_smoke_patches import FILES as PATCH_HASHES, main as fetch_patches  # noqa: E402
from fetch_smoke_zarr_metadata import HASHES as ZARR_HASHES, RELATIVE as ZARR_RELATIVE, main as fetch_zarr  # noqa: E402
from fetch_spiral_annotations import HASHES as ANNOTATION_HASHES, main as fetch_annotations  # noqa: E402


def run_smoke(*, fetch: bool, data_root: Path) -> dict:
    """Run independent audits, then assert the pinned fit-window regression."""

    if fetch:
        for fetcher in (fetch_patches, fetch_annotations, fetch_zarr):
            if fetcher() != 0:
                raise RuntimeError(f"fetcher failed: {fetcher.__name__}")

    patch_root = data_root / "PHercParis4" / "verified_patches"
    patches = [patch_root / name for name in PATCH_HASHES]
    patch_audits = [audit_tifxyz(path, scan_pixels=True) for path in patches]
    annotations = [data_root / "PHercParis4" / name for name in ANNOTATION_HASHES]
    annotation_audits = [audit_pointcollections(load_pointcollections(path)) for path in annotations]
    zarr_audit = audit_omezarr_v2(data_root / ZARR_RELATIVE)
    level3 = next((level for level in zarr_audit.levels if level.path == "3"), None)
    roi = plan_roi(level3, (0, 0, 0), (256, 256, 256)) if level3 else None
    window = preflight_fit_window(
        patches, z0=8500, z1=8600, annotation_paths=annotations[:2], scan_pixels=True,
    )
    checks = {
        "clean_patch_passes": patch_audits[0].ok,
        "known_patch_has_stale_bbox": any(issue.code == "stale_bbox" for issue in patch_audits[1].issues),
        "annotations_pass": all(audit.ok for audit in annotation_audits),
        "zarr_metadata_passes": zarr_audit.ok and len(zarr_audit.levels) == 6,
        "roi_is_bounded": roi is not None and roi.touched_chunks == 8 and roi.estimated_chunk_bytes_upper_bound == 16_777_216,
        "window_false_negative_reproduced": (
            window.metadata_candidate_patches == 0
            and window.actual_active_patches == 1
            and window.false_negative_metadata_patches == 1
            and window.unknown_patches == 0
            and window.patches[1].actual_vertices_inside == 50
            and window.annotation_points_inside.get(str(annotations[0])) == 182
        ),
    }
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip() or None
    dirty = bool(subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip())
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_revision": revision,
        "git_dirty": dirty,
        "data_sha256": {
            "patches": PATCH_HASHES,
            "annotations": ANNOTATION_HASHES,
            "zarr_metadata": ZARR_HASHES,
        },
        "checks": checks,
        "pass": all(checks.values()),
        "patches": [{"path": audit.path, "ok": audit.ok, "stats": audit.stats,
                     "issues": [asdict(issue) for issue in audit.issues]} for audit in patch_audits],
        "annotation_counts": [asdict(audit) | {"issues": [asdict(issue) for issue in audit.issues]}
                              for audit in annotation_audits],
        "zarr": {"root": zarr_audit.root, "axes": zarr_audit.axes, "level_count": len(zarr_audit.levels),
                 "issues": [asdict(issue) for issue in zarr_audit.issues]},
        "level3_roi": asdict(roi) if roi else None,
        "window": asdict(window),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-fetch", action="store_true", help="use previously downloaded data")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "public_smoke.json")
    args = parser.parse_args()
    try:
        report = run_smoke(fetch=not args.no_fetch, data_root=ROOT / "data")
    except (OSError, ValueError, RuntimeError, ImportError, StopIteration) as exc:
        parser.exit(2, f"smoke failed before report: {exc}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "checks": report["checks"], "report": str(args.output)}, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
