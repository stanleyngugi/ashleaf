# FB06 — Frozen Multi-Mesh Replication and Reliability Curve

Date: 2026-09-22
Experiment: E0011, FrameBridge independent E1 validation
Outcome: **mixed frozen replication; two strong held-out meshes, one weak held-out mesh, five out of domain**

## Executive result

The complete FB05 local-correspondence protocol was frozen and applied without estimator changes to the other eight verified Paris 4 meshes. Five held-out meshes were ineligible under the predeclared one-wrap boundary trim. Three were eligible and produced 46,318 fully answered pairs.

| Primary frozen metric | Result |
|---|---:|
| Eligible held-out meshes | 3 of 8 |
| Ineligible held-out meshes | 5 of 8 |
| Held-out pairs | 46,318 |
| Coverage on eligible pairs | **1.000** |
| Pooled exact signed `dw=1` | **0.709832** |
| Macro exact mean / median | **0.747956 / 0.867200** |
| Pooled MAE | **0.508442** |
| Macro MAE mean / median | **0.434796 / 0.154700** |
| Pooled positive predictions | 0.976294 |

This does not replicate the pilot's 92.385% as a universal score. It does establish that the frozen mechanism transfers strongly on two held-out segments and fails materially on a third. The result is therefore a heterogeneous reliability result, not a general-accuracy claim.

**Single-target baseline (2026-09-23 audit):** all local pairs were constructed and oriented with true `dw=+1`. A constant `+1` predictor scores 100% exact with zero MAE on this diagnostic. The FB06 score measures E1's agreement with known mesh adjacency, not its ability to label unknown candidate pairs. See [the claim audit](../docs/31_prepublication_claim_audit_2026-09-23.md).

## Per-mesh results, reported before pooling

| Mesh | Role | Status | Pairs | Exact signed | MAE | Median gap |
|---|---|---|---:|---:|---:|---:|
| `20230702185753` | held-out | ineligible | — | — | — | — |
| `20230929220926` | held-out | ineligible | — | — | — | — |
| `20231005123336` | held-out | eligible | 18,714 | **0.455969** | 1.054344 | 33.96 |
| `20231012184424` | held-out | eligible | 20,000 | **0.867200** | 0.154700 | 20.90 |
| `20231016151002` | held-out | eligible | 7,604 | **0.920700** | 0.095345 | 18.80 |
| `20231022170901` | development pilot | eligible | 20,000 | **0.923850** | 0.079400 | 19.01 |
| `20231031143852` | held-out | ineligible | — | — | — | — |
| `20231106155351` | held-out | ineligible | — | — | — | — |
| `20231221180251` | held-out | ineligible | — | — | — | — |

Every eligible pair had all required sparse rows and was answered. The pilot is excluded from every primary aggregate above.

## Eligibility is part of the result

The protocol trims one wrap at each mesh boundary before forming adjacent-wrap pairs. This rule was inherited from the pinned public mesh benchmark and frozen before FB05. It requires at least four detected wraps.

- `20230702185753`, `20230929220926`, and `20231221180251` had two consensus wraps.
- `20231031143852` and `20231106155351` had three consensus wraps.
- The four eligible meshes had four, four, four, and eight wraps.

The trim was not relaxed after observing held-out eligibility. These five exclusions limit external validity and must accompany any reported score.

## Frozen protocol integrity

No E1 parameter changed from FB04/FB05:

- `k=2.773`;
- `orient=+1`;
- seven rays with ±6 working-voxel offsets;
- two-working-voxel sampling;
- group-4 `grad_mag`;
- uint8 trilinear interpolation matching SciPy output semantics;
- outward-positive endpoint orientation from the public umbilicus;
- stride 10, one-wrap seam trim, endpoint rejection, exact deduplication;
- maximum 20,000 pairs per mesh, sampled with seed 1.

The remaining eight meshes were not used to choose these settings. The development pilot was excluded from the primary replication aggregate.

## Sparse acquisition and storage evidence

The all-mesh plan requested 10,949 logical bricks. Of those, 10,803 mapped to occupied resident-pool rows and 146 were defined-zero bricks.

The exact rows initially formed 1,938 HTTP ranges and 353,992,704 requested bytes. To reduce request latency without changing scientific support, ranges separated by at most 16 rows were coalesced:

| Acquisition property | Result |
|---|---:|
| Exact occupied rows | 10,803 |
| Extra coalescing rows | 3,560 |
| Acquired rows | 14,363 |
| Exact range count | 1,938 |
| Coalesced range count | 1,120 |
| Durable payload | 470,646,784 bytes (448.84 MiB) |

All 1,120 responses were required to be HTTP 206, match the requested `Content-Range`, contain whole brick rows, match expected byte counts, and pass SHA-256 both before and after writing. Extra rows only optimize acquisition; the requested-brick semantics and estimator are unchanged.

The original 27 coordinate TIFFs totaled 607,697,202 bytes and were individually hashed in `all_mesh_tiff_manifest.json`. After pair construction, the four eligible endpoint arrays were compressed, hashed, shape-checked, and used as immutable scoring inputs. The redownloadable TIFF cache was then removed to make room for the sparse field payload.

Pinned upstream commits:

- `constraint-gauge`: `a72c4235862be12ae975402e7ec239713fd2b216`
- `villa`: `c4902849470a2e4005c8492120007280f087d636`

## Failure anatomy

The weak mesh differs visibly in pair geometry and prediction distribution.

| Mesh | Exact | Median gap | p90 gap | Main behavior |
|---|---:|---:|---:|---|
| weak held-out `20231005123336` | 0.455969 | 33.96 | 60.43 | frequent over-counts 2–5 |
| held-out `20231012184424` | 0.867200 | 20.90 | 36.71 | mostly 1; modest 2 tail |
| held-out `20231016151002` | 0.920700 | 18.80 | 30.53 | concentrated at 1 |
| development pilot | 0.923850 | 19.01 | 31.27 | concentrated at 1 |

The weak mesh still has 98.07% positive predictions. Its failure is therefore primarily magnitude over-counting, not sign reversal. A plausible mechanism is that longer Euclidean chords integrate multiple field peaks even though their endpoint labels are adjacent in the mesh parameterization.

## FB06E exploratory distance analysis

After the frozen result was complete, fixed descriptive gap thresholds were evaluated. This is explicitly exploratory and does not replace FB06.

| Maximum gap | Held-out pairs | Coverage | Exact signed | MAE |
|---:|---:|---:|---:|---:|
| 12 | 3,528 | 0.0762 | **0.9586** | 0.0414 |
| 16 | 9,945 | 0.2147 | **0.9606** | 0.0394 |
| 20 | 17,123 | 0.3697 | **0.9317** | 0.0687 |
| 24 | 23,563 | 0.5087 | **0.8974** | 0.1053 |
| 32 | 32,285 | 0.6970 | **0.8458** | 0.1678 |
| 40 | 37,137 | 0.8018 | **0.8155** | 0.2157 |
| 48 | 40,563 | 0.8758 | **0.7805** | 0.2913 |
| 64 | 44,866 | 0.9687 | **0.7264** | 0.4555 |

At gap ≤16, each held-out mesh independently exceeds 93.7% exact accuracy, but the weak mesh retains only 9.27% of its pairs. This supports distance as a useful reliability variable, not as a complete solution. The threshold curve was observed after FB06 and cannot be described as held-out tuning.

## What is now supported

1. The coordinate-frame repair and sparse sampling implementation work across multiple independent meshes at full technical coverage.
2. Frozen E1 transfers strongly to two held-out meshes and the development pilot when chord geometry is favorable.
3. Cross-segment performance is heterogeneous; long local chords are a major, measurable failure mode.
4. A simple geometric variable produces a useful accuracy–coverage curve, reaching 96.06% pooled held-out accuracy at 21.47% coverage.
5. Pair applicability and confidence must be first-class parts of any exported winding constraint.

## What is not supported

1. A universal 92% accuracy claim across Paris 4 meshes.
2. An all-nine evaluation claim; five held-out meshes are outside the frozen protocol's domain.
3. Replacing the FB04 generic-pair negative result.
4. Calling the post-hoc gap thresholds a new held-out estimator.
5. Spending GPU time before a new confidence/path-model hypothesis is preregistered and can be tested on genuinely untouched evidence.

## Decision

Retain FrameBridge as the active September release candidate, but change the headline from “E1 replicates at 92%” to **“explicit frames plus applicability-aware sparse evaluation expose when local winding evidence is reliable.”**

The next experiment must target long-chord failure without changing the frozen FB06 record. The preferred route is a geometry-only confidence model or a locally curved path model, evaluated with leave-one-segment-out calibration and per-segment reporting. GPU work remains gated; this is still a CPU reasoning and validation problem.

## Reproducibility artifacts

- `artifacts/framebridge/all_mesh_tiff_manifest.json`
- `artifacts/framebridge/FB06_all_mesh_local_ray_plan.json`
- `artifacts/framebridge/FB06_pair_cache/*.npz`
- `artifacts/framebridge/FB06_all_mesh_local_e1_summary.json`
- `artifacts/framebridge/FB06_error_analysis.json`
- `artifacts/framebridge/FB06_error_details/*.npz`
- `data/PHercParis4/lasagna_inputs/FB06_grad_mag_ranges/download_manifest.json`

Large artifacts and source data remain ignored by Git; small tracked reports and scripts define how to reconstruct them.
