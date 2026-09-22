# September 2026 Execution Board

Window: 2026-09-22 through the official 2026-09-30 11:59 p.m. Pacific monthly deadline.

Primary target: **FrameBridge — independent cross-frame validation of pairwise winding evidence.**

This is a gated research plan. We submit only what the evidence supports. A public repository or upstream pull request is not, by itself, a prize submission.

## Non-negotiable rules

1. Preserve the frozen E1 estimator (`k=2.773`, `orient=+1`) for the primary test. Changing it answers a different question.
2. Never tune on all mesh-arm pairs and report that score as independent/held-out.
3. Express every coordinate transform explicitly; ban unexplained factors such as `*4` from evaluation code.
4. Keep source-frame, target-frame, axis order, voxel sizes, level, origin, and artifact hashes in result metadata.
5. Score accuracy and coverage together. Zero or selective coverage cannot be hidden.
6. Record every run, including failures, in the experiment registry or a linked report.
7. Do not start a full Colab fit until CPU contracts, transforms, and a tiny sampling probe pass.

## Work packages and gates

### WP0 — Freeze context and competitor check

Deliverables:

- Pin `villa` and `constraint-gauge` commits.
- Search current upstream issues/PRs and community projects for the same cross-frame probe.
- Write a one-paragraph novelty statement and name the nearest alternatives.

Gate G0: continue only if no current public artifact already reports a corrected independent E1-on-mesh result with reproducible transforms.

Status: **substantially complete**; repeat the search immediately before public release.

### WP1 — Frame contract

Implement a compact immutable representation with at least:

- coordinate order (`xyz` versus array `zyx`);
- voxel size in micrometres per axis;
- pyramid/downsampling factors per axis;
- origin/translation;
- optional 4×4 affine when scale+origin is insufficient;
- declared coordinate semantics (voxel centers versus corners);
- source path/URL, logical dataset/group, and hash or version.

Required tests:

- identity;
- 2.4 ↔ 9.6 isotropic scale round trip;
- anisotropic scale;
- axis permutation;
- nonzero origin;
- half-voxel convention mismatch that must fail loudly;
- bounds transformation and physical-overlap calculation;
- a deliberately wrong transform reproducing zero coverage.

Gate G1: round-trip error ≤ `1e-9` voxels for exactly representable synthetic cases; all ambiguous/missing contracts fail rather than guess.

### WP2 — Real-data overlap probe

Use pinned Paris 4 artifacts to produce a small machine-readable report containing:

- annotation, `grad_mag`, umbilicus, and mesh bounds in native voxels;
- the same bounds in micrometres and in a chosen canonical 2.4 µm frame;
- intersecting z and xyz support;
- sample endpoint counts inside/outside the field;
- first 20 rejected pairs with exact reason;
- transform provenance.

Gate G2: at least one verified-mesh collection has nonempty physical overlap and a nonzero number of rays that can be sampled fully inside the E1 field. If not, publish the corrected no-overlap finding and stop claiming E1 can be independently tested on this arm.

### WP3 — Faithful E1 adaptation

Refactor sampling so the estimator receives declared transforms rather than assuming all points are full-resolution coordinates with `LASAGNA_SCALE=4`. Preserve:

- ray spacing and offsets in a declared physical/native unit;
- trilinear interpolation and decode factor;
- seven-ray median;
- frozen magnitude calibration and radial sign rule;
- explicit unanswered status for rays that leave the field.

Handle the umbilicus in its declared frame. Include parity tests showing the refactored path is identical to the existing path on the original annotated arm.

Gate G3: bit-identical or numerically justified parity on a pinned annotated sample; any difference is explained before mesh scoring.

### WP4 — Independent benchmark

Pre-register before inspecting aggregate accuracy:

- verified meshes/collections;
- mesh trimming and stride values;
- primary metric: exact `dw=1` accuracy;
- secondary metrics: MAE, coverage, calibration bins, error by distance/z/mesh/boundary margin;
- transform and boundary sensitivity grid;
- bootstrap or collection-level uncertainty method;
- which subset, if any, is development versus final evaluation.

Run the frozen estimator. Preserve `constraint-gauge`’s pair CSV and summary JSON formats and provenance label.

Gate G4:

- L1 outcome: nonzero, explained coverage and a reproducible correction of the previous zero-coverage result;
- L2 outcome: enough independent pairs/collections to make uncertainty and failure analysis meaningful;
- otherwise report the limitation and do not oversell.

### WP5 — Confidence improvement, only after G4

The existing rounding-boundary confidence is weak. Candidate confidence signals:

- median absolute deviation across the seven rays;
- number of valid rays;
- distance to field boundary;
- local gradient-field support/energy;
- radial-order margin;
- transform uncertainty;
- agreement across sampling resolutions or ray offsets.

Use a spatially isolated development subset. Compare precision at fixed coverage and risk-coverage curves on untouched collections. Avoid a large feature model this month; simple interpretable calibration is easier to verify.

Gate G5: improvement must survive the untouched subset and at least one sensitivity perturbation. Otherwise ship the independent baseline without the confidence claim.

### WP6 — Integration evidence

Best case: export only high-confidence relative-winding constraints in an official-compatible format and show one bounded fitter/QC comparison. Acceptable alternatives if time is tight:

- demonstrate which mesh regions are safe/unsafe evidence sources;
- produce a correction/PR to `constraint-gauge` with a regression;
- produce a frame-inspection tool that another existing project can use;
- obtain upstream author review or reproduce on a second mesh.

Gate G6: at least one external-use signal, upstream review, or real downstream before/after is needed for a top-tier submission claim. Lack of it does not invalidate a smaller, honest benchmark contribution.

## Calendar

| Date | Primary outcome | Stop condition |
|---|---|---|
| Sep 22 | Intelligence pack, commits pinned, strategy pivot recorded | None |
| Sep 23 | WP1 schema/tests and WP2 bounds-only probe | Stop implementation if novelty is already closed upstream |
| Sep 24 | Corrected field/mesh overlap and reason-coded coverage probe | If no physical overlap, switch to documenting/correcting the benchmark claim |
| Sep 25 | Annotated-arm parity and first frozen mesh run | Do not tune until parity passes |
| Sep 26 | Sensitivity runs, failure gallery, confidence baseline | Drop confidence improvement if sample is too small or unstable |
| Sep 27 | Optional confidence filter and/or official-format export | Prefer a correct small artifact to unfinished fitter integration |
| Sep 28 | Fresh-environment reproduction, docs, license, public/upstream release | No new research feature after freeze |
| Sep 29 | External feedback, fixes, submission narrative and evidence table | Keep claims tied to committed artifacts |
| Sep 30 | Final reproducibility check and official submission before 11:59 p.m. PT | Submission confirmation required; GitHub publication alone is insufficient |

## Experiment matrix

Each row becomes a manifest/run record before aggregate results are examined.

| ID | Factor | Values | Purpose |
|---|---|---|---|
| FB00 | Transform | identity / known-wrong / 4× corrected | Prove test sensitivity and reproduce zero coverage |
| FB01 | Mesh stride | 8 / 10 / 16 | Density and runtime sensitivity |
| FB02 | Boundary margin | 32 / 64 / 128 field-grid voxels | Separate support loss from estimator error |
| FB03 | Ray count | frozen 7 only for headline; 3/11 diagnostic | Do not silently change the estimator |
| FB04 | Offset | frozen ±6 native voxels; physical-equivalent diagnostic | Expose unit dependence |
| FB05 | Collection | per verified mesh plus pooled | Prevent one mesh dominating the conclusion |
| FB06 | Confidence | old rounding margin / ray dispersion / support composite | Precision–coverage comparison after baseline |
| FB07 | Sign | frozen radial sign; diagnostic sign-oracle only | Separate magnitude and sign failures without inflating headline |

## Decision tree

```text
same work already exists?
├─ yes → contribute missing test/documentation or switch to a current fitter bug
└─ no
   └─ physical field/mesh overlap exists?
      ├─ no → publish a corrected frame/support audit; do not run GPU fit
      └─ yes
         └─ annotated parity passes?
            ├─ no → fix adapter; no independent score yet
            └─ yes
               └─ independent coverage meaningful?
                  ├─ no → report support limitation and reason codes
                  └─ yes
                     └─ score/calibration useful?
                        ├─ no → publish falsification + failure localization
                        └─ yes → test confidence filtering and downstream export
```

## Fallback lanes

If FrameBridge is closed or blocked, choose exactly one; do not fragment the final week.

1. A current `villa` issue with a minimal real-data reproduction, regression test, surgical fix, and before/after logs.
2. A missing `constraint-gauge` reproducibility correction that changes an actionable conclusion, not cosmetic cleanup.
3. A narrow spatial-leakage/provenance extension to an existing benchmark with held-out real data.
4. Documentation/integration contribution only if it materially enables a current tool and an external user confirms value.

## Submission evidence table template

| Claim | Baseline | New result | Data/arm | Independence | Artifact | Limitation |
|---|---|---|---|---|---|---|
| Previous mesh coverage was a frame artifact | 0.000 | TBD | Paris 4 verified meshes | independent | summary JSON + pair CSV | TBD |
| Transform is correct | implicit constants | TBD round-trip/support checks | synthetic + public metadata | n/a | tests + frame report | affine assumptions |
| Confidence predicts error | old non-monotone weak curve | TBD | untouched mesh collections | independent | risk-coverage CSV/plot | sample/collection size |
| Downstream utility | no corrected E1 mesh evidence | TBD | bounded fit/QC | declare exactly | before/after | compute/time |

## Definition of done for September

- Public, permissively licensed code or an accepted/clearly reviewable upstream contribution.
- One-command small reproduction plus explicit instructions for larger public data.
- Pinned versions and hashes, hardware/runtime/memory, and frame metadata.
- Synthetic and real-data tests.
- Accuracy, coverage, uncertainty/sensitivity, negative cases, and provenance.
- A concise release report, failure gallery, and limitations.
- Official Progress Prize form submitted on time if the evidence clears at least L1 and the contribution is not duplicated.

Anything less remains valuable internal research, but it should not be inflated into a winning claim.
