# FB04 — Frozen E1 on Corrected Pilot Mesh Pairs

Date: 2026-09-22
Experiment: E0011, FrameBridge independent E1 validation
Outcome: **Coverage restored; preregistered accuracy result failed**

## Executive result

The frozen E1 estimator was run once on all 19,999 deterministic pilot pairs after transforming mesh coordinates from the 2.4 µm grid to the 9.6 µm E1 working grid. The sparse sampler reproduced SciPy's order-1 interpolation, including its uint8 output quantization. No calibration parameter was refit.

| Metric | Historical wrong-frame mesh arm | Corrected FB04 pilot |
|---|---:|---:|
| Pairs | 19,998 across nine meshes | 19,999 on one pilot mesh |
| Answered coverage M4 | 0.000 | **1.000** |
| Exact `dw=1` M1 | undefined | **0.000** |
| MAE M2 | undefined | **69.844** |
| Answered `dw=1` pairs | 0 | 6,671 |

Frame correction completely resolves the operational-coverage failure but does not make the existing mesh-pair score accurate. This negative result is retained; it must not be replaced by a tuned headline.

## Frozen estimator contract

- `k = 2.773`;
- `orient = +1`;
- `ENCODE_SCALE = 1000`;
- `GRAD_MAG_FACTOR = 0.25`;
- group scale `LASAGNA_SCALE = 4`;
- samples every two E1 working voxels;
- seven parallel rays at offsets from −6 through +6 working voxels;
- trilinear interpolation with SciPy's uint8 output behavior;
- public 146-point umbilicus;
- no mesh-arm fitting or threshold choice.

Every pair had all seven valid rays, no occupied row was missing from the selective acquisition, and no pair had an exactly zero radial sign.

## Prediction behavior

Predictions ranged from −245 to +224 windings:

- 11,674 predictions were negative;
- 8,311 were positive;
- 14 were zero;
- true differences were only 1 through 5.

This is not a subtle scale miss. The ray paths being evaluated are geometrically unlike the paths on which E1 was developed.

## Post-result applicability audit

The result prompted a geometry-only comparison of the benchmark inputs. No E1 values or labels were used to choose the diagnostic.

### Annotation-arm pairs

The complete public annotation arm contains 8,156 pairs. In 9.6 µm working voxels:

| Quantity | p0 | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| Endpoint distance | 6.85 | 34.11 | 64.31 | 107.54 | 151.98 | 224.33 | 302.24 |
| Absolute z difference | 0 | 0 | 0 | 0 | 11.45 | 55.39 | 157.08 |
| Angular separation about umbilicus | 0.000° | 0.267° | 0.806° | 1.958° | 4.031° | 10.885° | 20.840° |

For annotation `dw=1` pairs, median endpoint distance is 21.23 working voxels.

Positive annotation winding direction is physically anchored: 99.926% of positive-difference pairs move outward from the public umbilicus. Median radial displacement rises monotonically from 18.66 working voxels for `dw=1` to 138.09 for `dw=6`.

### Existing pilot mesh-pair construction

The mesh arm treats the entire mesh as one collection, assigns winding levels along the arc parameter, and uses the generic `build_pairs` function. That function samples the Cartesian product of every point on winding level A with every point on winding level B. For the 19,999 pilot pairs:

| Quantity | p0 | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| Endpoint distance | 40.64 | 1070.90 | 1591.19 | 2460.39 | 3268.72 | 4220.82 | 4761.63 |
| Absolute z difference | 0.01 | 600.87 | 1304.82 | 2238.73 | 3038.89 | 3977.34 | 4392.28 |
| Angular separation about umbilicus | 0.006° | 49.277° | 96.222° | 139.222° | 163.491° | 178.464° | 179.997° |

For mesh `dw=1` pairs, median endpoint distance is 1600.02 working voxels—about 75 times the annotation `dw=1` median. Median angular separation is about 96°, versus 0.8° on annotations.

## Interpretation

E1 estimates winding difference by integrating density along the straight segment between the supplied endpoints. A label difference of one does not imply that an arbitrary chord between two points on adjacent wraps crosses only one sheet. The existing generic mesh pairing often connects points on opposite sides and different heights of the scroll. Such a chord can cross dozens or hundreds of layers, exactly matching the observed prediction scale.

This means FB04 is a valid score of E1 on the benchmark's current all-to-all pair distribution, but that distribution is not an applicability-matched test of the local ray-integral mechanism. The pairwise benchmark's claim that handing an integral estimator arbitrary ground-truth pairs is neither easier nor harder on accuracy is not supported for this mesh geometry.

There is a second convention issue: mesh winding levels increase with mesh parameter direction, which is not guaranteed to match the annotation arm's physically anchored outward-positive direction. Signed scoring needs an explicit orientation adapter independent of estimator output.

## Decision

1. Preserve FB04 as the primary result for the existing generic pair protocol.
2. Do not tune `k`, orientation, offsets, or pair filtering against FB04 outcomes.
3. Add a separately named applicability-matched diagnostic using adjacent-wrap, same-row nearest correspondences supplied by the verified mesh geometry.
4. Define positive mesh direction as outward from the public umbilicus, matching 99.926% of annotation pairs.
5. Predeclare the local-pair construction before reading its E1 scores.

The project has therefore found two distinct failures: a coordinate-frame error that destroyed coverage, and a pair-generation mismatch that makes arbitrary long chords unsuitable for a local path-integral estimator.
