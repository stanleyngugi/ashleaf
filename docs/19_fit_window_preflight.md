# Spiral-Fit Window Preflight

`preflight_fit_window.py` checks whether a proposed full-resolution Z window contains usable patch and annotation evidence before a costly spiral fit.

## Why the preflight matters

The current community has documented two related traps:

1. a patch's cached `meta.json` bbox can be stale after geometry changes, so metadata-based window filtering can omit valid surface vertices;
2. a spiral fit can start from a pack containing patches but still have no patches in the selected Z window, leaving little local evidence while the run may appear to complete normally.

The preflight reports both the cached-bbox candidate count and, in pixel mode, the number of actual valid vertices in the window. It also counts official point-collection annotations in the same Z interval.

## Real-data reproduction

```bash
python3 scripts/fetch_smoke_patches.py
python3 scripts/fetch_spiral_annotations.py
.venv/bin/python scripts/preflight_fit_window.py \
  data/PHercParis4/verified_patches/0003_fill_sel_20260512_105100_10 \
  data/PHercParis4/verified_patches/same_wrap000882_growpatch \
  --z0 8500 --z1 8600 --pixels \
  --annotations data/PHercParis4/same_windings.json \
                data/PHercParis4/relative_windings.json
```

For the pinned public files, the cached-bbox count is 0 but the true active-patch count is 1. `same_wrap000882_growpatch` contributes 50 valid vertices in the window despite its recorded maximum Z being below 8500. The same-winding file contributes 182 annotation points; the relative-winding file contributes 0. The command exits with status 2 for a metadata false negative.

## Output interpretation

- `metadata_candidate_patches`: patches whose cached Z bbox intersects the half-open window.
- `actual_active_patches`: patches with at least one valid vertex inside the window, when pixel scanning is enabled.
- `false_negative_metadata_patches`: metadata says outside, real vertices say inside.
- `unknown_patches`: patches not fully scanned, often because they exceed the pixel limit.
- `annotation_points_inside`: points located in the window by their full-resolution Z coordinate.

The preflight does not prove a patch is a good geometric fit, only that it contains actual usable vertices. Its pixel mode has a configurable per-patch size cap and is suitable for targeted windows; a tiled full-corpus scanner remains future work.

## Prior work

- [Original stale-bbox issue](https://github.com/ScrollPrize/villa/issues/1272)
- [PHerc1218 constraints and zero-patch fitting caveat](https://github.com/IyanDopico/vesuvius-sheet-tools/blob/main/docs/constraints.md)
