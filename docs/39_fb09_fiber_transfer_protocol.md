# FB09 — independent intra-fiber applicability transfer protocol

Status: **locally specified before sampling normal/E1 field outcomes for FB09; scored unchanged**. This is a separate exploratory transfer test after the FB08 frozen holdout, not a retroactive extension of its preregistered primary metric. No FB09 field score was used to set the FB08 thresholds.

## Question

Does the frozen FB08 normal-alignment rule also withhold nonzero winding proposals on a different kind of physically along-sheet geometry: two points along one official Paris 4 `eval_fibers` trace? FB08's human `same_windings.json` arm was separately collected and geometrically distinct from the relative annotations. A transfer check on traced fibers is a meaningful stress test of *source dependence*. It is not an automatic positive-constraint test or an official-fitter result.

## Population, selected without normal/E1 outcomes

`scripts/build_fb09_eval_fiber_pairs.py` reads the public [`eval_fibers` index](https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/eval_fibers/) and sorts filenames by SHA-256 of `FB09-eval-fiber-v1:<filename>`. It takes the first 40 traces with explicit `vc_open_data_coordinate_space = PHercParis4/20260411134726@L0`, source coordinate level 0, scale factor 1, and original resolution 2.4 µm, skipping untagged or incompatible files **before** reading any CT-derived field outcome. Source filenames and content hashes, including screened skips, go in a git-ignored manifest. Raw fiber JSON is streamed and not saved.

Each selected trace contributes up to ten pairs: equispaced starts along its `line_points` arclength, endpoints 120 L0 voxels apart along the line (30 working voxels), retaining only Euclidean working chords of length 10–50 voxels. L0 xyz is divided by four to the canonical 9.6 µm level-2 xyz frame. The pair selection does not inspect E1 predictions, normals, human winding labels, or whether the eventual gate accepts a pair. Normal and E1 byte plans are computed only after this candidate manifest exists.

The **constructed** target is `dw=0` because both endpoints lie on one continuous traced fiber, taken as a same-surface/same-winding cue. This is a plausible physical negative, **not** human-verified pairwise winding ground truth. Some traces could be erroneous or change sheets; any accepted nonzero proposal therefore needs inspection rather than an unqualified “false positive” claim. The sample is not randomly representative of all automatic candidates.

## Frozen comparison and outputs

The unchanged FB08 primary numeric rule is E1 answered/nonzero, valid nx/ny normals at both endpoints, minimum absolute chord–normal dot ≥0.75, and E1 confidence ≥0.75. `src/scroll_lab/constraint_gate.py` is SHA-checked against the FB08 freeze. No threshold may be adjusted based on FB09. Report pair and fiber counts, valid-normal coverage, normal-dot distribution, ungated E1 nonzero proposals, E1 confidence-only nonzero proposals, normal-only nonzero proposals, and frozen-rule nonzero proposals. Report all of these again for `|Δz|<1` and chord length 10–50 working voxels, even if that matched slice is small. Include per-fiber concentrations and any accepted-example IDs, but do not redistribute raw fiber or CT payloads.

If the gate yields zero accepted nonzero proposals, the supported conclusion is **transfer of the tangential-chord rejection heuristic to this selected traced-fiber sample**, not zero production false-accept risk. If it emits some, inspect their traces and field support; do not erase the failures. A strong FB09 result still does not fix FB08's 17 off-by-one accepted positive relations or solve the graph-connectivity collapse. The next prize-relevant bar remains a controlled downstream effect with coverage, ideally on automatic positive candidates and a fixed fitter evaluation.

## Acquisition status, 2026-09-24

No FB09 normal or E1 outcome had been scored when this protocol was written. A first 40-trace ignored manifest was assembled, then the coordinate predicate was tightened to require an **explicit unit source scale factor** as this protocol states. The first manifest was treated as provisional until strict replay; that replay subsequently selected 40 fibers / 400 pairs from the same pinned index and produced a **byte-identical manifest** (SHA-256 `d30baba84dfd49341d035ae2f36c7652d9d880ab2690877c38cff05a24b471ca`). Thus the stricter check did **not** change this selected population. The builder checkpoints after small deterministic ranked batches and checks the public index SHA before resuming. All old partial byte-range downloads were stopped before scoring; the normal and E1 range plans were regenerated from the strict manifest and hash-link to it. Selection equivalence alone was not evidence for or against the gate.

## Frozen transfer result

Exact HTTP byte plans and completed fetch manifests hash-link to the strict candidate manifest: each normal channel acquired **40,599,552** payload bytes across **300** ranges; grad-magnitude acquired **51,019,776** bytes across **334** ranges. The fetcher required HTTP 206 and matching `Content-Range` and re-hashed every range after writing. All 400 candidate pairs had seven in-bounds E1 rays. Both endpoint normals were valid for **398/400** pairs. Among those, the median minimum absolute chord–normal dot was **0.064**, 90th percentile **0.193**, and maximum **0.715**; zero reached the frozen 0.75 threshold. The predeclared matched slice contained 64 pairs from 33 fibers, 63 with valid normals; its median dot was **0.061**, maximum **0.277**.

| Selected fiber population | Pairs | E1 answered | E1 nonzero proposals | E1 nonzero with confidence ≥0.75 | Frozen gate nonzero |
|---|---:|---:|---:|---:|---:|
| All tagged intra-fiber pairs | 400 | 400 | 399 | 84 | **0** |
| `|Δz|<1`, chord length 10–50 working voxels | 64 | 64 | 63 | 14 | **0** |

`scripts/run_fb09_fiber_transfer.py` SHA-checked the unchanged FB08 gate source and all FB09 candidate/normal/ray/download links before scoring. Its reason codes were 397 `CHORD_TANGENTIAL_TO_SHEET`, one `CHORD_ALIGNMENT_BORDERLINE`, one `ZERO_RELATIVE_PROPOSAL`, and one `NORMAL_FIELD_UNAVAILABLE`. The ignored row-level artifact is `artifacts/framebridge/FB09_fiber_transfer.json`; the normal audit is `artifacts/framebridge/FB09_fiber_normals.json`. The exact reproduction commands are in [the CPU runbook](45_fb09_cpu_transfer_runbook.md).

This supports **transfer of the tangential-chord rejection heuristic** to a separately sourced official fiber-trace sample, beyond the human-selected same-winding source used in FB08. It is not proof of zero production false-accept risk: the target `dw=0` follows a fiber-continuity assumption, not verified pairwise human labels; 40 traces from one scan are not a random automatic-candidate population; and learned normals may share domain priors with the tracing system. The result does not address positive signed-winding magnitude errors or demonstrate a better graph/spiral fit. All numerical proposals remain subject to the unverified-registration review latch.

As an **explicitly post-hoc** simple-geometry control, `scripts/analyze_fb09_radial_control.py` applied the FB08 radial-fraction ≥0.75 threshold to the same frozen E1 proposals without fitting new cutoffs. It would emit nonzero on **134/400** intra-fiber pairs, or **31/400** if combined with E1 confidence ≥0.75; in the matched 64-pair slice, **18/64** and **4/64** respectively. The frozen normal gate remained at zero. This reinforces that a simple umbilicus-radial chord heuristic does not explain all of the observed transfer rejection, but it was not a prespecified FB09 primary comparator and uses constructed zero cues. The ignored result is `artifacts/framebridge/FB09_posthoc_radial_control.json`.
