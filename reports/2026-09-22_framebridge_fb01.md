# FB01 — Paris 4 Full-Bounds Metadata Probe

Date: 2026-09-22
Experiment: E0011, FrameBridge independent E1 validation
Outcome: **PASS at the metadata/full-bounds gate; no estimator claim yet**

## Executive result

After expressing every asset in canonical physical xyz micrometres, the nine verified Paris 4 benchmark meshes, the winding annotations, the public umbilicus, and the packed `grad_mag` group-4 allocation overlap in three dimensions. The earlier statement that the mesh arm lies outside the E1 field is not supported once the 2.4 µm and 9.6 µm coordinate frames are distinguished.

This experiment establishes geometric feasibility only. It does not establish that occupied field bricks cover every ray, that scan origins are registered exactly, or that E1 predicts the correct winding difference.

## Inputs and provenance

The probe used pinned local copies fetched from current public sources:

| Asset | Evidence | Important digest |
|---|---|---|
| Relative winding annotations | 2,173 measured JSON points | `a3243511d4eb91387a9b32f4dbff11514b08c3ae36e9b2a2b8222607b4883ac1` |
| Umbilicus | 146 measured control points | `c5f30b0d135c1d333f8170e592079a3d5a636e0071c0dcce560eecebb0ee2602` |
| Benchmark meshes | Nine official TIFXYZ `meta.json` bounding boxes | Per-file digests are embedded in the result artifact |
| Gradient field | Villa `respool` v2 metadata for `las_008_grad_mag.ome.zarr/4` | `c2558e4e60fc9abfcbd4299f52d263a384c3a64b2243428f0cd8474c590a932b` |
| Manifest | Explicit frames, expectations, and limitations | `0bc9afcd93dcd29f126dc15ad7e94855c4b7839933993dba4e9399a1f979bda7` |

The generated machine-readable result is `artifacts/framebridge/FB01_metadata_probe.json`. Generated artifacts and large inputs are intentionally Git-ignored; this report and the fetch/probe commands are the durable record.

## Declared coordinate frames

| Frame | Stored order | Resolution | Provisional origin |
|---|---|---:|---:|
| Annotation / umbilicus working grid | xyz | 9.6 µm | (0,0,0) µm |
| Verified mesh volume `20260411134726` | xyz | 2.4 µm | (0,0,0) µm |
| `grad_mag` OME group 4 | zyx | 38.4 µm | (0,0,0) µm |

The 38.4 µm field spacing is the frozen E1 relationship `9.6 × LASAGNA_SCALE(4)`. Zero origin and matching axis direction remain hypotheses to validate, not hidden assumptions.

## Measured native bounds

| Asset | x | y | z |
|---|---:|---:|---:|
| Annotations, 9.6 µm grid | 1987.506–6602.229 | 1690.654–6625.411 | 6527.571–17252.555 |
| Umbilicus, 9.6 µm grid | 3142–4908 | 3295–5965 | 563–18240 |
| Nine meshes, 2.4 µm grid | 12715.932–23517.967 | 10383.837–25505.549 | 29384.689–73931.617 |
| `grad_mag`, group-4 zyx array | x 0–2043 | y 0–2043 | z 0–4736 |

The `grad_mag` allocation shape is `(4737, 2044, 2044)` in zyx order.

## Physical comparisons

All four preregistered expectations passed:

| Comparison | Result | Physical overlap extent xyz |
|---|---|---:|
| Mesh aggregate vs field allocation | overlap | 25.925 × 36.292 × 106.913 mm |
| Annotations vs field allocation | overlap | 44.301 × 47.374 × 102.960 mm |
| Umbilicus vs field allocation | overlap | 16.954 × 25.632 × 169.699 mm |
| Mesh aggregate vs annotations | overlap | 25.925 × 36.292 × 95.101 mm |

The final row is the decisive correction to the historical comparison. Mesh z coordinates must not be compared numerically to annotation z coordinates until their respective voxel sizes have been applied.

## Interpretation

FB01 upgrades the hypothesis from “the z ranges might overlap after dividing by four” to “the declared assets occupy a common three-dimensional physical region under the current frame contract.” It therefore justifies an independent mesh-arm E1 rerun.

It does not justify loading all 4.755 GiB of the packed gradient channel. A rectangular allocation can contain zero-valued or absent sparse bricks, and a mesh bounding box is much larger than the actual collection of sampled rays. FB02 therefore validates the sparse indexes and derives exact range requests before any channel payload is acquired.

## Known limitations

1. Mesh bounds came from official metadata, not yet from rereading the three coordinate TIFFs.
2. All origins and axis directions are provisionally aligned.
3. Array allocation is not a nonzero-density map.
4. Aggregate overlap does not imply that every benchmark pair or all seven offset rays are in bounds.
5. The public umbilicus frame must be confirmed because it determines prediction sign.
6. A support pass is not an accuracy result.

## Reproduction

```bash
python scripts/fetch_framebridge_metadata.py
PYTHONPATH=src python scripts/probe_frame_overlap.py \
  experiments/manifests/framebridge_paris4_metadata.json \
  --output artifacts/framebridge/FB01_metadata_probe.json
```

## Gate decision

**Advance to FB02.** The old zero-overlap explanation is falsified under the corrected scale contract, while the remaining uncertainty is narrow enough to test with sparse-index analysis and one mesh pilot.
