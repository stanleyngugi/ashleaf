# FB25: split-safe winding evidence to official fitter A/B

Date frozen: 2026-09-26. Status: implementation and preflight; no target-window fit result exists. This is a research protocol, not permission to export numeric constraints for production or submit a prize entry.

## Question and decision

Can the existing FrameBridge FB08 gate plus the FB15 surface-SDT magnitude cue select winding-ruler v3 pairs that improve an **official Villa spiral fit** on held-out verified patch geometry, beyond both a patches-only fit and a same-count native-E1-confidence control? The full 30,000-step fitter output decides the result. Internal E1/SDT agreement, PCL loading, fit input satisfaction, and visible overlays are diagnostics.

The primary region is PHercParis4 full-resolution z **[15000,16000)**, replication z **[12000,13000)**. Before this freeze, local relative-winding files showed 396 labeled points in the first region and 217 in the second. We chose the richer relative-annotation region rather than estimate patch density from public `meta.json` bboxes, because [Villa issue #1272](https://github.com/ScrollPrize/villa/issues/1272) documents stale bboxes. These annotations have already informed earlier FB08 research, so they are **not** pristine holdout truth. Verified patch surfaces withheld before generation are the primary output-side evidence. Do not choose a region after inspecting fitted outputs.

## Source and frame

| Component | Pin / frozen rule |
| --- | --- |
| Official fitter | `ScrollPrize/villa` commit `c4902849470a2e4005c8492120007280f087d636`; current `spiral-fitting/fit_spiral.py` |
| Candidate source | `pscamillo/winding-ruler` commit `2d34dcb02dbfe7e8bce8d9c9c44285b434c08996`, `generators/ruler_generate_v3.py`, defaults except target z window and output path |
| Candidate calibration | v3 uses human relative annotations at **z [8000,9000)** (W1), then generates in a disjoint target region. Its published default generation region is z [10000,11000) (W2), not its calibration region. |
| Candidate label | The v3 source emits `wind_a: 1,2`, hence a fixed +1 relation, and a rounded `residual`. The residual is not E1 confidence. Source label and endpoint order are never changed. |
| Native E1 | Existing frozen `scroll_lab.sparse_e1.predict_pairs`, seven rays, group-4 gradient field, W1-frozen `k=2.773`. Require `answered`, native `predicted_dw == +1`, native confidence ≥0.75. |
| Endpoint normal gate | Existing FB08 nearest group-4 normal endpoint sampling; both valid, minimum absolute chord alignment ≥0.75. |
| Surface-SDT cue | Existing FB15 v1 crest count, seven valid rays at one working-voxel samples in group-1 SDT; magnitude exactly 1. No tuning on target outputs. |
| Output evaluator | `Nicodol/spiralcheck` commit `d1b50e2957409a870225fb9f5dcc5e25f7a0f9da`, `split` and `score` with fit-input leakage audit and unseen-only aggregate. |

The unverified FB08 registration latch remains in force: every generated PCL has `research_only: true`, `registration_verified: false`, and `numeric_export_permitted: false` in metadata. Villa may load these files in an isolated research fit; a positive fit result would still require an independent physical-frame audit before any production export claim.

## Leakage boundary

1. Use `spiralcheck split --src <all_verified_patches> --out <split> --frac 0.2 --seed 20260926` **before** running v3. Keep the split manifest and patch content/geometry hashes.
2. Stage a v3 generator dataset in which `verified_patches/` points only to `split/fit/`. The generator's patch-density feature uses `meta.json` bboxes; letting it inspect withheld patch metadata would leak output evidence even if Villa itself never loads those patches. This changes v3's data environment relative to its original published run, but keeps its code and settings fixed. Describe this arm as a split-safe reproduction of the v3 generator, not a byte reproduction of the published result.
3. The generator sees original `relative_windings.json` only to calibrate in W1. The four fit roots never see that original document. They all link exactly the same `split/fit/` patch directory. Other annotation-role files are absent.
4. Score every fit against `split/heldout/`, pass `--manifest` and `--fit-inputs`, and report both the all-heldout and genuinely unseen aggregates. The primary metric uses unseen points, at least 2 CT voxels from fit-input surfaces. A score without a passing hash and leakage audit is invalid.
5. Record the exact source bucket snapshot. The [official tutorial](https://scrollprize.org/tutorial_spiral) lists a ~90 GB Paris4 package, Python 3.14, and a 1,000-slice fit as a reasonable initial bounded run. Do not silently substitute a later dataset version between arms.

## Four arms and compute order

All runs use the same Villa commit, split, data snapshot, z window, seed, patch-only non-winding input configuration, model settings, and step count. Only relative PCL input differs:

1. `patch_only`: no relative PCL.
2. `v3_unfiltered`: all split-safe v3 +1 pairs.
3. `framebridge`: only pairs where native E1 agrees with +1, FB08 gate is numeric-eligible, and FB15 crest magnitude is 1 on seven valid rays.
4. `confidence_control`: among v3 pairs with native E1 +1, choose highest native E1 confidence in each 128-voxel midpoint z bin, exactly matching the FrameBridge arm's count in that bin. No normal or SDT score enters its ranking. Tie by stable candidate ID. Overlap with treatment is allowed and reported.

Run a 1,500-step smoke in the primary region first, primarily to prove loading, memory, output structure, and nondegenerate fit behavior; do not select a winner from smoke. Then run 30,000 steps for all four arms at seeds **17 and 29**. Run the replication region after primary results are frozen, subject to available compute before the monthly deadline. A missing replication fit is a stated limitation, not an implicit success.

The fitter configuration explicitly enables verified patches and the arm's relative PCL, while disabling unverified patches, tracks, fibers, same/absolute/drawn PCLs, dense normal/SDT/gradient losses, winding inference, and outer shell. This makes the first arm literally patch-only and holds other sources fixed. If Villa cannot fit this configuration, record the error and amend the protocol **before** reading target scores; do not silently change only one arm.

## Primary success gate

Use `spiralcheck score` on the **pure fitted** `wNNN` meshes (`--variant plain`), the same held-out split, `tau=6`, and `--unseen-min-dist=2`. The primary statistic is unseen-only `mean_sheet_consistency`. Treatment succeeds only if:

- its mean across seeds exceeds both patches-only and same-count confidence control by at least **0.03 absolute** (3 percentage points);
- treatment minus each comparator is **positive in each seed**;
- unseen `frac_within_tau` is no more than **0.01 absolute** below either comparator, for either seed;
- relative annotation agreement, scored from the output meshes against original target-window annotations as a *secondary, previously seen research signal*, does not decrease against either comparator; and
- replication, if complete, has a positive treatment-minus-control mean in the same primary statistic. Claim cross-region success only with replication complete.

Report unseen point counts, skipped patches, leakage fraction, all-heldout metrics, distance p50/p90, normal-angle p90, intrinsic topology alerts, and per-seed deltas even when the gate fails. Do not count a zero denominator or undecidable annotation comparison as satisfying a gate. A promising but incomplete result is labeled preliminary.

## Decision after evidence

If the gate passes, audit at least one high-leverage location in CT/mesh overlays, establish that treatment constraints actually loaded and changed the fit, and prepare a reproducible public release and Progress Prize draft for user review. If the gate fails, measure whether the selected constraints were loaded, satisfied, and spatially active; test a specific fitter mechanism only with a new preregistered run. After FB16's weak graph leverage, no further threshold sweep is justified by E1 precision alone.

The [winding-ruler submission](https://github.com/pscamillo/winding-ruler/blob/main/docs/SUBMISSION_winding_evidence.md) reports that accurate generated labels can degrade the official fit, making this A/B necessary. The [spiralcheck project](https://github.com/Nicodol/spiralcheck) explains why patch-distance alone misses full-wrap identity errors and why a name-level patch split can leak geometry. These are external context, not Ashleaf results.
