# Real-Data Fit-Window False Negative

Date: 2026-09-18

## Claim

In a 100-slice PHercParis4 window, a metadata-only selection over two pinned public patches finds zero candidates, while a pixel scan finds one patch with 50 valid vertices. This reproduces a known stale-bbox failure as an end-to-end fitting-input hazard.

## Reproduction

- Z window: `[8500, 8600)` in full-resolution voxels.
- Patches: `0003_fill_sel_20260512_105100_10` and `same_wrap000882_growpatch`.
- Both patches and annotations downloaded through pinned-hash scripts in this repository.
- Cached-bbox candidate patches: **0**.
- Actual active patches: **1**.
- False-negative metadata patches: **1**.
- Valid vertices inside the window on the omitted patch: **50**.
- Public same-winding annotation points inside: **182**.
- Public relative-winding annotation points inside: **0**.

## Practical consequence

A workflow that first chooses a Z window using cached bboxes may conclude that it has no patch evidence and either skip the patch or fit with an unintended evidence mix. The preflight catches this before a costly run. This report does not claim a new underlying dataset defect; the stale-bbox issue was already reported upstream. The new contribution is a reproducible window-level check that combines patch vertices and annotation counts.

## Limits

The test uses two selected patches, not the entire Paris 4 pack. No spiral fit was run here. The size cap means large patches can remain `unknown` until a tiled scanner is implemented. The exact fitter behavior for a given pack depends on its current filtering code and configuration.
