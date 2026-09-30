# FB08 — mixed winding-constraint development record

Status: **development record, retained as the pre-holdout rationale**. The unchanged-protocol holdout has since been scored and is reported separately in [`38_fb08_frozen_gate_holdout.md`](38_fb08_frozen_gate_holdout.md). This document's numbers are development-only; do not cite them as the final result.

## Objective

Test whether FrameBridge can distinguish when frozen E1 winding proposals should be trusted, rather than repeating the earlier all-`dw=+1` mesh diagnostic. The first evidence source is the public Paris 4 [`spiral-input` point collections](https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/): `relative_windings.json` and `same_windings.json`. Human annotation values are evaluation references, never gate inputs. This is a test on human-selected points, **not yet** proof about automatically generated fiber/mesh candidates or spiral-fitting impact.

## Provenance and frame contract

- Pinned local relative annotation SHA-256: `a3243511d4eb91387a9b32f4dbff11514b08c3ae36e9b2a2b8222607b4883ac1`.
- Pinned local same-winding SHA-256: `d9be52c5ebb42853f75f235241cbfd159738f6f34468bcd182523bc91dc91048`.
- Official [`villa` point-collection loader](https://github.com/ScrollPrize/villa/blob/0f7be4a4c9e449caad35537011502cc7ab7bc6fe/spiral-fitting/point_collection.py) stores `p` as given and reverses `point['p'][::-1]` for `zyx` array operations. Thus the apparent generic README `zyx` wording is **not** evidence that `p` itself is `zyx`. The local `scroll_lab.pointcollections` interpretation of `p` as `xyz` agrees with this loader.
- The [current spiral tutorial](https://scrollprize.org/tutorial_spiral) illustrates a 9.6 µm Paris 4 fitter coordinate system. The upstream [`constraint-gauge` frame correction](https://github.com/pscamillo/constraint-gauge) documents the Paris 4 annotation arm on a 9.6 µm grid of the 2.4 µm rescan. The selected grad-magnitude resident pool group 4 has shape `[4737,2044,2044]`; all candidate coordinates converted as `xyz[::-1]/4` permit all seven planned E1 rays in bounds. These facts support the intended scale/axis mapping. They do **not** independently prove exact scan registration, origin, or physical sheet placement. A CT/VC3D spot check remains required before promoting accuracy claims.
- The official [`villa` normal decoder](https://github.com/ScrollPrize/villa/blob/0f7be4a4c9e449caad35537011502cc7ab7bc6fe/spiral-fitting/losses.py) uses `(u8-128)/127` for nx/ny, sets validity if either component is nonzero, reconstructs nonnegative nz, and normalizes the `zyx` direction. The paired sparse normal field reports channel 0 nx and channel 1 ny. Our forthcoming endpoint sample is explicitly **nearest-integer exploratory sampling**, not claimed parity with the fitter's dense normal loss.
- The [data-server license](https://dl.ash2txt.org/LICENSE.txt) restricts redistribution. Raw downloaded annotations and field bytes remain git-ignored; only code, pinned hashes, commands, and derived aggregate evidence should be published unless permission changes.

## Candidate protocol, already implemented

`src/scroll_lab/candidate_pairs.py` selects an undirected union of each point's three nearest within-collection neighbors using **coordinates and collection membership only**, deduplicates pairs, and applies a stable SHA-256 orientation bit independent of labels and point-ID traversal. Only after selection does it attach the human `wind_a` difference as truth. Whole collection IDs are assigned to development or holdout by a deterministic seeded hash. The same-winding arm uses within-collection truth `dw=0` and stays separate from the relative arm. There is no automatic cross-collection truth and no fabricated negative relation.

The pinned local audit reports 254 nonempty relative collections / 2,173 annotated points and 125 nonempty same-winding collections / 5,413 points. The generated candidate manifest at `artifacts/framebridge/mixed_candidates.json` (git-ignored) has:

| Arm | Development | Holdout, not scored | Truth classes represented |
|---|---:|---:|---|
| Relative | 2,644 | 1,049 | `−3, −2, −1, +1, +2, +3` |
| Same winding | 6,492 | 2,863 | `0` only |

The relative arm's development/holdout unique endpoints have minimum cross-split separation ~25.8 working voxels and none within 16. The same-winding arm has many nearby cross-split points (585 holdout endpoints within 16 voxels of a development endpoint), so its current holdout is **not yet a spatially clean independent arm**. It can provide an applicability stress test, but its holdout must be spatially buffered or kept non-headline. Pair rows share points and collections; pair count is not the independent sample size.

Candidate lengths (working voxels): relative median ~31.8, 90th percentile ~67.1; same-winding median ~19.7, 90th percentile ~38.5. Relative `|dw|=1` candidate median is ~21.2, `|dw|=2` ~41.1, and `|dw|=3` ~62.3. The different geometries require per-arm and matched-window reporting, not a pooled accuracy headline.

## Sparse acquisition, already completed for E1

`scripts/plan_mixed_candidate_ranges.py` applied the existing conservative seven-ray brick planner to all 13,048 candidates. All 13,048 have seven geometrically in-bounds rays. For both arms, the union plan requires 1,523 occupied resident-pool rows, coalesced into 526 HTTP byte ranges and 83,034,112 payload bytes (~79.2 MiB), compared with a ~4.76 GiB full channel. `scripts/fetch_respool_ranges.py` fetched exactly those ranges into ignored `data/` and verified HTTP 206/Content-Range, byte lengths, per-file SHA-256, and post-write hashes. The complete manifest is at `data/PHercParis4/lasagna_inputs/mixed_candidate_grad_mag_ranges/download_manifest.json`.

For reproduction, set `PYTHONPATH=src`, run `scripts/build_mixed_candidate_manifest.py` with the two pinned local point-collection files, then `scripts/plan_mixed_candidate_ranges.py` with the pinned group-4 `meta.json`, `brick_coords.npy`, `table.npy`, and public channel URL. Finally run `scripts/fetch_respool_ranges.py` on that plan. The exact commands/paths are retained in this work session and should be added to the final reproduction guide once the protocol is frozen.

## Frozen E1 development result — diagnostic, not a gate result

`scripts/run_mixed_candidate_e1.py` loaded the verified sparse data and evaluated **development only**. It requires an explicit protocol-freeze file before it permits a holdout run.

| Arm | Answered | Exact signed matches among answered | Interpretation |
|---|---:|---:|---|
| Relative | 2,644 / 2,644 | 2,065 / 2,644 = **78.10%** | Mixed signed relation baseline on human-selected points. Errors increase for 2- and 3-wrap relations; no gate has improved this yet. |
| Same winding | 6,191 / 6,492 | 374 / 6,191 = **6.04%** | E1 chord-crossing integral is generally **not** an endpoint same-winding estimator. A constant `0` baseline is perfect on this source-specific arm, so do not pitch E1 as a universal relation classifier. |

The same-winding failure is unusually instructive: among its answered cases with E1 confidence ≥0.75, only 4/1,586 have true `dw=0`; at ≥0.9, 0/630 do. Conversely, relative-arm confidence ≥0.75 yields 598/670 exact matches. **Confidence alone cannot tell whether the estimator is being used in its intended geometric regime.** This is the central rationale for an explicit applicability gate, but a credible gate must be tested on held-out geometry and compared to simple features.

`scripts/analyze_mixed_candidate_geometry.py` shows relative candidates have median z separation 0 and same-winding candidates ~18.3 working voxels; that source difference is an easy shortcut. A common-support development window (`z` separation <1 voxel, chord length 10–50 voxels) still contains 1,550 relative and 1,866 same-winding candidates, with very different E1 correctness. All future applicability plots must show this or a similarly predeclared geometry-matched slice in addition to full-population statistics.

## Simple geometry baseline: a necessary correction

The sign of umbilicus-centered radial displacement agrees with the relative annotation sign on 2,638/2,644 development pairs (**99.77%**). These human point collections are organized along near-radial winding paths. That is a genuine danger for an impressive-but-trivial result. `scripts/benchmark_mixed_radial_baseline.py` uses five-fold **collection** cross-validation to fit just two magnitude cutoffs on either absolute radial displacement or chord length; it then restores the radial sign. The out-of-fold signed exact rates are **1,720/2,644 = 65.05%** and **1,757/2,644 = 66.45%**, respectively, versus E1's 78.10% development exact rate. The full-development cutoffs are recorded in the freeze for an unchanged holdout comparator. These controls do not solve applicability: neither can output a zero relation, and the source-specific same-winding arm is not a fair pooled accuracy set.

## Normal-field applicability result — development only

The fitted scroll consumes paired nx/ny predictions. A local across-sheet chord should align with the predicted sheet normal more than an along-sheet chord. `scripts/plan_normal_endpoint_ranges.py` selected group-4 nearest-integer endpoint bricks for both channels without labels. Each channel required 1,089 occupied rows, 466 coalesced ranges and 63,963,136 payload bytes (~61.0 MiB). After an interrupted fetch due to transient disk exhaustion, `--resume` reused only complete-size files produced by the same HTTP-206-validated fetcher, downloaded missing/incomplete ranges, wrote manifests, and post-write SHA-256 checked all 466 files in each channel. No raw range cache was removed; the attempted cleanup was blocked. `scripts/sample_mixed_normal_alignment.py` then decoded both normal components at both endpoints. Every candidate in both arms had two valid sampled normals.

The median minimum absolute chord–normal dot is **0.904** on relative development pairs versus **0.029** on same-winding development pairs. In the predeclared common-support window `dz < 1` and chord length 10–50 working voxels, the corresponding medians are **0.911** (1,550 relative pairs) and **0.023** (1,866 same pairs). This is a strong *source/applicability* separation, not proof that the model knows winding labels or that E1 proposals are exact. The two annotation sources were collected differently; there are no repeated `wind_a` labels within any of the 300 raw relative collections, so a same-winding negative **from the same collection source** cannot be constructed without inventing a relation.

`scripts/analyze_mixed_normal_development.py` reports unpooled gate comparisons. Every row below requires E1 to answer with a nonzero prediction. Relative values are exact signed matches among accepted proposals; same values are false nonzero accepts out of the whole same arm. Geometry-only radial fraction is about the umbilicus.

| Development condition | Relative correct / accepted | Relative coverage | Same false accepts / 6,492 |
|---|---:|---:|---:|
| No gate | 2,065 / 2,638 | 99.8% | 5,817 |
| E1 confidence ≥0.75 | 598 / 670 | 25.3% | 1,582 |
| Radial fraction ≥0.75 | 1,732 / 2,195 | 83.0% | 4,100 |
| Normal minimum dot ≥0.50 | 2,048 / 2,535 | 95.9% | 2 |
| Normal minimum dot ≥0.75 | 1,792 / 2,168 | 82.0% | 0 |
| Normal minimum dot ≥0.50 and E1 confidence ≥0.75 | 594 / 639 | 24.2% | 1 |
| **Frozen primary: normal minimum dot ≥0.75 and E1 confidence ≥0.75** | **491 / 518 = 94.79%** | **19.6%** | **0** |

In the common-support window, the frozen primary rule accepts 349 relative proposals with 341 exact (**97.7%**) and accepts **0/1,866** same-winding candidates. A geometry-only radial fraction ≥0.75 still falsely accepts **375/1,866** same-winding candidates there. This is the clearest development evidence that learned normal alignment adds information beyond a simple radial shortcut. It remains a pilot on human-selected points. The fact that the primary rule has zero observed same-arm false accepts does **not** imply zero future risk; candidates share points and collections, and the arms differ in selection process.

`src/scroll_lab/constraint_gate.py` now encodes the reason-coded rule. It withholds unanswered, zero, unavailable-normal or tangential proposals, routes borderline alignment/low E1 confidence to review, and marks numerically eligible relations `FRAME_REGISTRATION_UNVERIFIED` for review until a separate registration latch is established. Withholding a nonzero proposal never asserts same-winding truth.

## CT metadata and anchor sanity check

The canonical [Paris 4 2.4 µm CT](https://vesuvius-challenge-open-data.s3.amazonaws.com/PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr/.zattrs) declares `zyx` axes and a level-2 scale `[4,4,4]`. Its [level-2 array metadata](https://vesuvius-challenge-open-data.s3.amazonaws.com/PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr/2/.zarray) reports shape `[18946,8174,8174]`, and `ceil(shape/4)` is exactly the paired normal pool shape `[4737,2044,2044]`. SHA-256 of the two metadata objects is pinned in `artifacts/framebridge/FB08_CT_anchor_spot_check.json`.

`scripts/check_paris4_ct_anchor.py` deterministically chose the first eligible endpoint from three distinct development collections/z chunks in each arm using coordinates only, loaded six uncompressed CT chunks in memory, and measured local content along the sampled normal. All six were nonzero and locally nonflat (11³ intensity SD 18.3–41.2). This rules out gross out-of-bounds or empty-volume placement for this tiny sample. It is **not** independent proof of exact sheet seating, origin, a correct affine, or E1 parity. No raw CT bytes were saved or redistributed.

The official [Villa issue #1183](https://github.com/ScrollPrize/villa/issues/1183) also documents a historical `grad_mag` inference failure in which half of some output z chunks became zero while nx/ny remained correct. We have not established whether the pinned public `las_008` field was affected. Sparse row availability and post-write hashes alone cannot prove per-slice signal integrity. This is an explicit remaining failure mode, not an asserted defect in the current field.

## Freeze and untouched evaluation

`protocols/FB08_mixed_constraint_gate_freeze.json` was written **locally before running holdout E1**. It pins the candidate/ray/normal/buffer/gate hashes, primary and secondary thresholds, comparators, geometry-matched window, and prohibitions on retuning. This is an internal freeze, not a public or independently timestamped preregistration. `scripts/plan_fb08_holdout_buffer.py` uses coordinates only: exclude a holdout pair if either endpoint is within 16 working voxels of any development endpoint in the same arm. It retains all **1,049/1,049** relative holdout candidates and **1,742/2,863** same-winding holdout candidates. The unbuffered same arm will be reported as a sensitivity analysis only.

The next step in this historical record was to run `scripts/run_mixed_candidate_e1.py --partition holdout --protocol-freeze protocols/FB08_mixed_constraint_gate_freeze.json` and then `scripts/evaluate_fb08_frozen_gate.py` without changing the freeze. That run is now documented in `docs/38_fb08_frozen_gate_holdout.md`. No claim of better spiral fitting or production fiber-constraint accuracy follows from the development results alone.
