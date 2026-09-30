# FB25 baseline score verified and next decision — 2026-09-30

**Evidence cutoff:** 2026-09-30 13:08 UTC (16:08 Africa/Nairobi). This report supersedes the 12:32 UTC “still scoring” operational observation. It records one completed primary outcome pair and the remaining gate; it does not claim that an FB25 treatment wins.

## Current result

The frozen `patch_only`, seed 17 fit and its held-out evaluation are complete. The fit manifest records exit code 0 and 30,000 steps in window `[15000, 16000]`; the embedded checkpoint reports 30,000 iterations. The report bundle is stored under `MyDrive/Ashleaf/FB25/primary/reports/score_patch_only_seed17_20260930_v2`.

The scoring operation ended at `2026-09-30T12:34:22.495654Z` with status `scored_and_persisted`. Its operation record binds arm `patch_only`, seed 17, window, run manifest, checkpoint, pure mesh tree, split, fit and held-out input trees, annotation and umbilicus sources, and a passing exact-memory qualification. The snapshot contains the report, annotation report, assessment bundle, binding, two overlays, and their verified byte counts and SHA-256 hashes. The persisted report's SHA-256 is `5705175a2cee005b91d52f5eb0e2b91a29f38c293bac56ffcdba340a16e730aa`; the report tree SHA-256 is `1f0d70dd86d67178582d6ee2a3aaaa95082aed6b9f0a4f6eca0d4bc9bb89c78e`.

The control baseline is:

| Frozen held-out subset | Patches | Points | Within τ=6 | Mean sheet consistency | Minimum sheet consistency |
|---|---:|---:|---:|---:|---:|
| All reportable held-out patches | 172 (746 skipped) | 330,686 | 90.90% | 0.9121 | 0.1548 |
| Unseen points, more than 2 voxels from any fit input | 130 (42 excluded for too few unseen points) | 58,821 | 69.33% | 0.5965 | 0.1292 |

The unseen subset is the FB25 primary outcome metric. It is materially harder than the all-point aggregate and exposes weak patches; it should be the reference against which the frozen treatment and confidence-control arms are judged. Winding agreement is `null` in this score, so no absolute winding identity claim follows. Intrinsic mesh checks found 177 crossings (0.31%), 1,348 collapsed gaps (2.36%), and 2,414 inflated gaps (4.23%). These are baseline diagnostics, not treatment comparisons.

## Integrity notes

The original saved score-input manifest declares internal digest `a1f5b52072a240e8753fa824b9d0969cc376b467dfdb6b76a8b5fc33d1053bc2`, while the actual serialized file bytes hash to `f3997c3da4637a3b1bb89d0a998f062ee448ba9ecce4ca5cf3484bcded52a4b9`. The scoring operation and bound report use the actual serialized-byte digest; they also independently bind the original split digest `e8688addeeec92f2420f99ce34df8316d3e35962328850dc198f9636f86cd3b5`, exact patch lists and content/geometry checks. Keep both values visible in the record. Do not edit the preserved manifest or describe its self-hash as passing.

The exact-memory native scorer parity passed on the pinned Linux environment. Qualification uses adapter SHA-256 `bac559cd53e44916b28240694ee7f95892210138f9850a4ad78b749028e4f1c3`, test SHA-256 `03be032ca3b36f450ac5e8e77e69d0cbf98fcba76ec967abb80712f0ac8bc6a5`, and parity log SHA-256 `1342eb1fd3e4e71c1cb2a61a4425c7a73b329d3fb349c9b32f51f83016cb9277`. The scorer returned `scored_and_persisted`; the UI's earlier reconnect failure occurred while the CPU operation was still completing and did not invalidate this later durable evidence.

## Prize and technical context rechecked on 2026-09-30

The official [open problems page](https://scrollprize.org/) identifies dense adjacent sheets and tears as the central virtual-unwrapping difficulty and says tracing remains semi-automated. The official [monthly prize criteria](https://scrollprize.org/prizes#progress-prizes) require a specific scroll-data problem, a clear implementation and demonstration, significant advantage over existing solutions, documentation with usage examples, and modular handling of community formats. It also explicitly favors methods released early and actually used by the community. The page sets this month's deadline at 11:59pm Pacific on September 30, 2026 (October 1, 09:59 Nairobi time).

The official [August winners](https://scrollprize.org/winners#31000-progress-prizes-august-2026) set a concrete comparison bar: the $20,000 contribution was patch-based unwrapping that checked 2D patch alignments for incompatible 3D locations and recovered about 365 cm² on PHerc. 1667. This reinforces the repository plan's requirement for usable geometry or human-effort gains and a real downstream comparison. It is my inference from these public criteria and results that a single scored control, absent a valid FB25 treatment comparison, is not a credible winning claim; the remaining submission window should be used only for a real outcome and a fully reproducible evidence package, never a weakened gate.

## Account and runtime state

On account 2 (`sngugi.research@gmail.com`), host `10c463aaaf25` is a live CPU-only runtime. It freshly mounted Drive, read the persisted operation, score and binding records, and passed an ephemeral write/read/delete probe under `MyDrive/Ashleaf/FB25`. This confirms the account-2 editor route is usable from Colab. It does **not** prove GPU availability or a fit-ready local environment. The 6,589,451,779-byte pinned-environment archive is present locally and its Drive manifest hash is `6fa35f7077cb3382aaa8238cdbc50e8abb0967e17be862b07c9252d99ab51fe8`; account 2 has not yet restored it, passed local imports/freeze checks, staged the fit queue, or launched a fit. Its saved Tesla T4 notebook output is stale; the current runtime has no `nvidia-smi` executable.

Account 3 (`ulemseewako@gmail.com`) has no active fit/score process in the inspected recovery notebook. Its connected CPU session failed a fresh Drive mount; older process output and saved notebook outputs are historical. Account 0 is disconnected. No GPU is allocated or idle. No acquisition, split regeneration, candidate regeneration, arm rebuild, or smoke rerun is needed.

## What remains and the decision order

There are **seven missing valid primary outcome pairs**. FrameBridge seed 17's earlier attempt stopped at 18,000 iterations, has no final meshes, and has an empty native input manifest; preserve it and rerun the same frozen arm/seed in a fresh attempt. The other missing pairs are `patch_only` seed 29, both seeds of `v3_unfiltered`, both seeds of `framebridge` (including the rerun), and both seeds of `confidence_control`—seven fits and seven scores in total. Do not treat the baseline alone as a pass, do not assess an incomplete matrix, and do not start replication unless the frozen gate passes.

The immediate operational decision is whether account 2 can restore the pinned archives on CPU, apply the current operational overlay without touching the frozen contract, pass imports and all 26 freeze checks, stage the existing frozen fit inputs locally, and verify a fresh local/durable attempt path. If that preparation passes, the best next incremental outcome is the invalid FrameBridge seed-17 rerun. Allocate an accelerator only if a disjoint frozen fit queue is already runnable; release it once its work completes or blocks. Score completed fits on available CPU sessions. If setup or compute prevents a valid run, record the precise blocker and preserve evidence rather than changing any scientific parameter.

The primary decision requires all four arms by both seeds. The frozen gate remains: at least 0.03 mean unseen sheet-consistency gain over both patch-only and confidence control; positive gain for each seed; within-τ loss no worse than 0.01 per seed; and no annotation-agreement regression. A full gate by the September monthly deadline (October 1, 09:59 Nairobi) is now unlikely without demonstrated multi-runtime capacity. A valid partial matrix is still useful progress, but it cannot be promoted as the final result.

Keep `numeric_export_permitted=false`. Do not publish or submit externally as part of this execution; those actions remain outside the current scope.

## Evidence locations

- Durable score bundle: `MyDrive/Ashleaf/FB25/primary/reports/score_patch_only_seed17_20260930_v2`
- Durable fit: `MyDrive/Ashleaf/FB25/primary/runs/primary_patch_only_seed17`
- Transfer archive manifest: `MyDrive/Ashleaf/FB25/gpu_runtime_transfer_20260930.json`
- Pinned environment manifest: `MyDrive/Ashleaf/FB25/gpu_pinned_environment_20260930.json`
- Current operational status: [PROJECT_STATE](../PROJECT_STATE.md)
- Frozen decision contract: [FB25 protocol](../docs/65_fb25_fitter_ab_protocol_2026-09-26.md) and [fitter freeze](../protocols/FB25_fitter_ab_freeze.json)
