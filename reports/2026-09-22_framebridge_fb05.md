# FB05 — Verified-Mesh Local-Correspondence E1 Diagnostic

Date: 2026-09-22
Experiment: E0011, FrameBridge independent E1 validation
Outcome: **One-mesh positive-only diagnostic; 92.385% E1 agreement with constructed adjacent-wrap pairs at full coverage**

## Executive result

The locally specified local-correspondence protocol was run on verified pilot mesh `20231022170901`. It uses same-row nearest correspondences between adjacent wraps, orders every pair outward relative to the public umbilicus, and evaluates the frozen E1 estimator without refitting. The pair geometry was independent of E1 parameter tuning; it was not an independent scroll or blind human crossing annotation.

| Metric | Result |
|---|---:|
| Independent local pairs | 20,000 |
| Answered pairs | 20,000 |
| Coverage M4 | **1.000** |
| Exact signed `dw=1` M1 | **0.92385** |
| Exact absolute `dw=1` | **0.92385** |
| MAE M2 | **0.0794** |
| Pairs with all seven rays valid | 20,000 |

This result is substantially stronger than the failed FB04 generic-pair score as a test of where E1 recovers constructed mesh adjacency. **Every target is `dw=+1`; a constant `+1` predictor is 100% exact with zero MAE on this population.** The score is therefore not a predictive gain over a trivial label baseline. It remains a one-mesh estimator diagnostic, not evidence of unknown-pair precision or fitter improvement.

## Local protocol timing and separation from FB04

The protocol was written to `docs/26_e1_applicability_protocol.md` after observing FB04's frozen negative result but before running E1 on the local pairs. The protocol and result first entered public Git history together, so this timing is a project record rather than independently verifiable public preregistration. It declared:

- same-row adjacent-wrap nearest correspondences;
- stride 10 along row and curve;
- one-wrap seam trim;
- endpoint rejection;
- the existing mesh-spacing distance guard;
- exact endpoint deduplication;
- at most 20,000 pairs sampled without replacement using seed 1;
- outward-positive orientation from the public umbilicus;
- frozen E1 constants and sampling;
- exact signed `dw=1` accuracy as primary diagnostic.

FB05 supplements FB04. It does not erase or supersede the 0.000 accuracy observed on arbitrary all-to-all mesh chords.

## Pair construction evidence

The verified mesh yielded:

| Property | Result |
|---|---:|
| Consensus wrap count | 8 |
| Five-row counts | 7, 8, 8, 8, 7 |
| Candidate correspondences | 35,108 |
| Unique correspondences | 35,108 |
| Deterministically selected pairs | 20,000 |
| Equal-radius rejections | 0 |
| Endpoint-order swaps to outward-positive | 19,981 |

The 99.905% swap rate is consistent with the convention issue exposed by FB04: increasing mesh parameter/wrap index was almost exactly opposite the annotation arm's outward-positive direction. Pair orientation was determined geometrically before reading E1 predictions.

Pairs were distributed across the five retained adjacent-wrap gaps: 4,310, 4,112, 4,010, 3,874, and 3,694.

## Applicability match

| Distribution | Annotation `dw=1` | FB05 local mesh pairs | FB04 generic mesh pairs |
|---|---:|---:|---:|
| Median endpoint distance, working voxels | 21.23 | **19.01** | 1600.02 |
| Median angular separation | approximately 0.8° | **0.396°** | approximately 96.2° |
| p90 endpoint distance | 40.45 | **31.27** | 3257.30 |
| p99 endpoint distance | 72.76 | **49.32** | 4216.26 |

The local mesh protocol matches the spatial scale and near-radial geometry of the annotation pairs without using annotation labels or E1 outputs to select correspondences.

## Prediction distribution

| Prediction | Count | Fraction |
|---:|---:|---:|
| 0 | 963 | 4.815% |
| 1 | 18,477 | **92.385%** |
| 2 | 523 | 2.615% |
| 3 | 24 | 0.120% |
| 4 | 9 | 0.045% |
| 5 | 2 | 0.010% |
| 9 | 1 | 0.005% |
| 12 | 1 | 0.005% |

Every nonzero prediction was positive after the preregistered outward orientation. The reported `positive_sign_fraction` of 0.95185 counts zero predictions as not positive; conditional sign accuracy among nonzero predictions is 100%.

## Data and numerical fidelity

- The local support plan requested 2,171 logical bricks.
- 2,136 occupied rows were acquired; 35 absent bricks are defined zeros.
- Payload was 69,992,448 bytes (66.75 MiB) across 610 verified HTTP 206 ranges.
- Every range was checked against its exact `Content-Range`, length, and post-write SHA-256.
- The sparse sampler fails if an occupied but unacquired row is touched.
- Randomized tests match `scipy.ndimage.map_coordinates(order=1, mode="nearest")` exactly for uint8 output, including rounding.
- All 20,000 pairs had all seven rays inside the field and no missing-row exception.

## What this result supports

1. The public group-4 `grad_mag` field and frozen E1 calibration transfer strongly to independently verified mesh geometry when asked local crossing questions appropriate to the estimator.
2. The old 0% mesh coverage was a coordinate-frame artifact.
3. The subsequent catastrophic generic-pair error is explained by an applicability mismatch, not necessarily by a failed density mechanism.
4. Explicit frame and pair semantics materially change the scientific conclusion.

## What this result does not support

1. It does not establish 92.385% performance across all nine meshes.
2. It does not make FB05 directly comparable to node-based tools scored on the generic all-pairs distribution.
3. It does not validate longer `dw>1` local crossings.
4. It does not prove that the umbilicus registration is perfect everywhere.
5. It does not authorize tuning on the 7.615% errors.
6. It does not supersede FB04.

## Decision

Freeze the complete FB05 protocol and replicate it on the remaining eight meshes. Report per-mesh results before any pooled number, include heterogeneity and failure cases, and retain the pilot in the pooled set exactly once. If replication holds, package FrameBridge, sparse remote evaluation, the generic-pair negative control, and the local independent result as the September contribution.
