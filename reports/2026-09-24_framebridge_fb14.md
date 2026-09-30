# FrameBridge FB14 — signed-positive transfer on absolute anchors

Date: 2026-09-24. Status: **completed, important negative transfer result**. The source, geometry-only population, unchanged gate, and comparisons were fixed in [the local protocol](../docs/47_fb14_absolute_anchor_transfer_protocol.md) and `protocols/FB14_absolute_anchor_transfer_freeze.json` before FB14 E1 or normal outcomes were scored. This is not an externally verified preregistration, independent physical registration, or fitter evaluation.

## Why this test matters

FB08 showed a frozen trust gate rejecting inapplicable nonzero E1 proposals on human same-winding cues while retaining 190/207 exact signed proposals on held-out relative-winding candidates. FB09 repeated the rejection on separately sourced fiber-continuity zero cues. Neither established positive transfer to a **different signed-label source**. FB14 uses the official Paris 4 [`abs_winding.json`](https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/abs_winding.json), whose populated collections carry `winding_is_absolute: true`; signed pair labels are differences of the human-entered absolute values.

The frozen geometry screen yielded **90** within-collection, 10–50-working-voxel, nearly coplanar nonzero pairs: 84 from collection 1 and 6 from collection 5, with true absolute magnitudes 1:51, 2:26, 3:9, 4:4. Their deterministic hash orientation produced 45 positive and 45 negative signs. The absolute points are spatially separate from the FB08 mixed-candidate endpoints (nearest point separation about 115 working voxels), but all are on the same Paris 4 scan and the 90 pairs share endpoints heavily. They are **not 90 independent annotations**; there are only two multi-point source collections.

## Primary and fixed comparators

| Rule | Emitted / 90 | Exact signed | Precision among emitted |
|---|---:|---:|---:|
| E1 answered, nonzero, no gate | 90 | 69 | 76.7% |
| E1 confidence ≥0.75 | 19 | 14 | 73.7% |
| E1 confidence-ranked top 13, equal coverage | 13 | 9 | 69.2% |
| **Unchanged FB08 normal + confidence gate** | **13** | **9** | **69.2%** |

All 90 E1 rays were geometrically supported; both endpoint normals decoded as valid for all 90. The frozen gate did **not** improve signed precision over E1 confidence ranking at the same 13/90 coverage on this source. Its 13 numeric emits remain `review`, not production `accept`, because `FRAME_REGISTRATION_UNVERIFIED` remains true. E1's 69/90 full-coverage result exceeds the literal `+1` and `−1` controls (24/90 and 27/90 respectively) and an **oracle-sign** unit-magnitude reference (51/90); the latter is an intentionally privileged, nondeployable context check, not a fair model baseline.

By collection, gate exactness was **7/11** on collection 1 and **2/2** on collection 5. The second collection has only six possible screened pairs and cannot rescue the aggregate inference. There is no defensible collection-bootstrap confidence interval with two highly unequal clusters.

## Failure mechanism

| True magnitude | Candidate pairs | E1 exact, full | Gate emits | Gate exact |
|---:|---:|---:|---:|---:|
| 1 | 51 | 50 | 7 | 7 |
| 2 | 26 | 16 | 2 | 2 |
| 3 | 9 | 3 | 2 | 0 |
| 4 | 4 | 0 | 2 | 0 |

Every one of the four wrong gate emits is a **one-wrap undercount**: true 3→predicted 2 twice, and true 4→predicted 3 twice. Their minimum endpoint chord–normal alignments are approximately 0.89–0.97, and E1 confidences approximately 0.77–0.87. Thus neither a high normal dot nor a high rounding confidence resolves this magnitude error. Across all 90 pairs, 20 of the 21 E1 errors are one-wrap undercounts; the remaining error is a one-wrap overcount on a true-1 pair. This is a specific operational failure mode, not random sign failure. The gate's normal condition is useful for *applicability*, but is not a reliable certificate of the integer wrap count.

| Wrong accepted pair ID | Human `dw` | E1 `dw` | E1 confidence | Minimum normal dot |
|---|---:|---:|---:|---:|
| `FB14:1:27:30` | +3 | +2 | 0.800 | 0.966 |
| `FB14:1:49:52` | +3 | +2 | 0.872 | 0.940 |
| `FB14:1:49:53` | −4 | −3 | 0.854 | 0.940 |
| `FB14:1:50:54` | +4 | +3 | 0.766 | 0.892 |

The IDs refer to point IDs in the pinned official source and allow a reviewer to find exact counterexamples without this repository republishing raw coordinates or CT data. They also show repeated endpoints in one correction path, reinforcing the dependency caveat.

This result is substantially weaker than the FB08 held-out positive-arm result. The source collections, correction paths, class mix, and local field region differ, so a direct pooled accuracy is inappropriate. The result does refute a broad reading of “the frozen gate transfers as a high-precision signed-positive filter across official Paris 4 annotation sources.” It also suggests the missing research variable is magnitude evidence, not another uniform graph weight.

## Provenance, acquisition, and reproduction

The source SHA-256 is `4e566731f7cbaf8f5ec843de687b3f72f4a784c40b587ebbaf544550902172c1`. The ignored candidate manifest and scored result are `artifacts/framebridge/FB14_absolute_pairs.json` and `artifacts/framebridge/FB14_absolute_transfer.json`; the latter hash-links the tracked FB14/FB08 freezes, candidate manifest, three exact byte plans, and three verified download manifests. Each normal channel required **425,984 bytes / 5 ranges**, and gradient magnitude **589,824 bytes / 5 ranges**. The downloader required HTTP 206 and matching `Content-Range`, then rehashed the written payloads. No GPU was involved. Exact CPU commands are in [the FB14 runbook](../docs/48_fb14_cpu_reproduction.md). Raw annotations and field bytes remain ignored.

The public absolute PCL lacks a separately proven CT registration, even though its coordinate scale and bounds align with the FB08 working frame. This result is conditional on that mapping and on the human-entered absolute labels. We did not run the official GPU spiral fitter or show a downstream gain.

## Decision

Retain FB08/FB09 as evidence that FrameBridge can reject certain inapplicable E1 proposals. **Do not advertise the current gate as a general high-precision signed-winding constraint generator.** FB14 supplies real, separate-source positive failure cases with exact IDs, reason codes, class effects, and a reproducible CPU path. This makes the trust-layer diagnosis more useful and sharpens the next build target: physical or topological evidence that distinguishes an E1 count from a count one wrap higher, followed by a genuinely untouched signed-positive evaluation and, only then, a controlled fitter comparison. Changing the frozen threshold on these 90 rows would turn the test into tuning and should not be presented as FB14.
