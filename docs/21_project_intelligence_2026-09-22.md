# Project Intelligence — 2026-09-22

This is the current operating picture after a near-complete repository read, a current-upstream audit, an external benchmark reproduction, and a review of the official prize and community-project pages. It is a decision document, not a claim that the proposed September experiment has already succeeded.

## Executive decision

The repository is healthy, coherent, and unusually well documented for a new effort. Its current implementation is useful infrastructure, but its proposed September headline—**fit-window preflight for stale TIFXYZ bboxes**—has been overtaken by the community. `tifxyz-repair` has already audited all 4,922 verified PHercParis4 patches, found 106 stale bboxes (59 involving z), provided atomic repair, shipped corrected boxes, checked 40,782 unverified patches and 817 segment meshes, and supplied an upstream prevention PR. Our two-patch reproduction remains a good regression fixture and reusable input-validation component; it is not a credible “significant advantage over existing solutions” by itself.

The recommended September target is therefore:

> **FrameBridge: close the independent cross-frame validation gap for pairwise winding evidence.** Make the coordinate transforms explicit, prove or falsify overlap between the 9.6 µm annotation/field grid and 2.4 µm verified-mesh grid, rerun the frozen E1 estimator on the mesh arm, and publish the result with provenance, coverage, accuracy, calibration, failure cases, and regression tests.

This is attractive because it closes a precisely recorded open probe in `constraint-gauge` A25, attacks the highest-leverage geometry bottleneck (trustworthy local winding evidence), is primarily a reasoning/data-contract task before it is a GPU task, and has useful negative-result value. It must still pass the gates in [the execution board](22_september_execution_board.md); novelty is a hypothesis until upstream/community checks confirm it.

## What was inspected

### This repository

- All 21 pre-existing documents, all three reports, the experiment registry and fixtures, package metadata, source modules, scripts, tests, and tracked small-data artifacts.
- The complete local unit suite: **33 tests passed** under WSL on 2026-09-22.
- The pinned public-data smoke path and its known Paris 4 false-negative reproduction: a patch contributes 50 usable vertices to z `[8500, 8600)` although its cached metadata excludes that window; a selected clean control contributes none.
- The ignored local data layout, hashes/provenance records, OME-Zarr metadata snapshots, and external-project pinning.

### External benchmark

- Current `constraint-gauge` commit: `a72c423` (also the current remote head when checked).
- README, all gauge modules and runners, all self-contained tests, provenance declarations, committed summaries and pair tables, and the complete GATE0 criteria/addenda.
- All eight self-contained checks run here passed: synthetic, ground-truth tau, local tau, planar, density, mesh spacing, mesh ground truth, and pitch checks.
- Important benchmark facts:
  - `winding-sync/bfs@stride160` obtains only about **0.0169 exact dw=1 accuracy**, L1 about **0.0503**, and coverage about **0.287** on the verified-mesh arm. Because BFS and L1 use the same generated graph, the generator/localisation evidence—not only the synchronizer—is a major bottleneck.
  - `S-E-improved` reaches about **0.296 exact dw=1** at full coverage on the independent annotated arm. Better, but far from solved.
  - Frozen E1 reaches about **0.923 exact dw=1** on held-out annotated pairs, but this is **shared-parent**, not a publishable independent headline: calibration and evaluation descend from the same annotation campaign. Its present confidence score is nearly uninformative.
  - A25 corrects the annotation frame from 7.91 to **9.6 µm/voxel**, observes that annotation coordinates multiplied by four span z `26108–69012` in the 2.4 µm grid while the mesh arm spans `29420–73889`, and explicitly leaves cross-arm validation as a probe to be measured.
  - The committed E1 mesh-arm coverage of zero was computed without a robust frame adapter and is therefore likely—but not yet proven—to be an artifact.
  - A26 distinguishes fundamental inter-sheet pitch (~130–145 µm mode in the available evidence) from a longer-tailed mixture whose median is around 176–180 µm. Future geometry code must not silently treat those as the same physical quantity.

### Current official upstream

A shallow, sparse local snapshot of `ScrollPrize/villa` was taken at `c4902849470a2e4005c8492120007280f087d636` under the ignored `data/external/villa/`. It includes official site docs, the TIFXYZ specification, and current `spiral-fitting/` code and tests.

The current fitter is substantially more mature than assumptions in some of our early planning documents:

- dedicated configuration, service, session, checkpoint, and test modules;
- CUDA startup checks and input snapshotting;
- explicit source-enabled predicates;
- structural detection/warnings for dense losses that cannot operate;
- checkpoint/input preflights;
- documented `normal_zarr_group` and `lasagna_scale` hazards;
- a separate autoresearch workflow designed around multiple GPUs and long runs.

This means a generic “effective configuration” preflight is also at risk of duplicating upstream. Any fitter contribution must begin from the current source, reproduce a current failure on real data, and demonstrate an advantage.

### Current official competition state

As checked on 2026-09-22:

- Best Progress Prize submission: **$20,000 guaranteed monthly**; other award levels are possible.
- Next monthly deadline: **2026-09-30 11:59 p.m. Pacific**.
- The official preferences align tightly with our process: release early, obtain actual use, improve real data quantitatively or qualitatively, resolve live bugs with before/after evidence, reveal actionable information, and document it well.
- Core requirements include a specific problem and demonstrated advantage, comprehensive documentation/examples, standard formats, consistent output, and modular integration.
- The official winding page says the fastest route to scalable unrolling is likely accurate, fast, verifiable local constraints that the spiral fitter can reconcile globally. It explicitly welcomes classical, learned, manual, fiber, patch, and other evidence sources.
- Grand Prize deadline: **2027-06-25 11:59 p.m. Pacific**. The official whole-scroll guidance is to solve segmentation/unrolling first, then ink detection, with reproducibility, held-out validation, and strict false-positive controls.

Primary references:

- <https://scrollprize.org/prizes>
- <https://scrollprize.org/open_problems/winding_annotations>
- <https://scrollprize.org/community_projects>
- <https://github.com/ScrollPrize/villa>
- <https://github.com/pscamillo/constraint-gauge>
- <https://github.com/Nieuwlaar/tifxyz-repair>
- <https://github.com/abundantjoe/winding-sync>
- <https://github.com/pscamillo/winding-ruler>
- <https://github.com/Nicodol/spiralcheck>
- <https://github.com/7jycwjmbfn-eng/spiral-fit-consumer-gpu>

## Competitive landscape: do not duplicate

The relevant 2026 field is already strong. Before starting any implementation, compare against at least these:

| Existing project | What it already establishes | Consequence for us |
|---|---|---|
| `tifxyz-repair` | Full-corpus exact-loader bbox audit and repair | Retire bbox repair as the headline; retain regression/component value |
| TIFXYZ Doctor | Deterministic TIFXYZ QA and an isolated synthetic-defect benchmark | Do not ship a generic mesh linter without a new real-data failure class |
| `spiralcheck` | Held-out whole-fit evaluation; exposes 54.8% spatial leakage in a naive name split | Use spatial/provenance independence, not filenames, for validation |
| `winding-sync` | CT-derived structure-tensor constraints plus global L1 integer synchronization | Focus on better evidence generation/calibration or independently proving it, not another graph solver first |
| `winding-ruler` | Winding-evidence measurements and pitch atlas | Treat E1 faithfully and disclose calibration provenance |
| `constraint-gauge` | Multi-arm benchmark, density gates, provenance labels, score artifacts | Extend its unresolved cross-frame probe instead of inventing a second incompatible metric |
| `spiral-fit-consumer-gpu` | Fitter operation on 12 GB GPUs with parity checks and large point-linking speedup | Colab feasibility is plausible, but generic low-memory enablement is no longer novel |
| `vesuvius-automesh` | CPU-only, QC-gated surface harvesting with 279 cm² accepted | New surface harvesting needs stronger quality or reach, not a thin wrapper |
| Herculaneum Scroll Tools | Large-scale CT-consistency QA and spiral-input tooling | Avoid broad data-audit claims without a sharply new invariant |
| `eligible-spiral-dataset` | Current inventory of eligible scrolls with available tracks/umbilici | Use it when expanding beyond Paris 4; do not redo the inventory |

## Recommended September contribution: FrameBridge

### The specific question

Can the frozen E1 pairwise winding estimator, previously strong only on shared-parent annotations, answer pairs derived from independently verified meshes after a formally specified 2.4 µm ↔ 9.6 µm coordinate conversion?

This decomposes into four falsifiable questions:

1. Do the mesh points physically intersect the spatial support of the E1 gradient field after scale and axis conversion?
2. Does the umbilicus live in the same logical frame as the field, and can its interpolation be evaluated without mixing grids?
3. At nonzero coverage, what are exact `dw=1`, MAE, coverage, and confidence calibration on independently derived mesh pairs?
4. Are results stable under multiple verified meshes, mesh subsampling strides, boundary margins, and transform round trips?

### Minimum artifact

- A small, explicit coordinate-frame schema: axis order, voxel size, level/downsampling, origin/translation, optional affine, source artifact and hash.
- No implicit global `LASAGNA_SCALE`; sampling accepts a declared transform and converts both endpoints and umbilicus consistently.
- A transform-inspection CLI that reports source and target bounds in both voxel and physical units, overlap volume/bands, out-of-bounds causes, and round-trip error.
- A benchmark command that emits the existing `constraint-gauge` JSON/CSV result format with provenance unchanged.
- Synthetic permutation/scale/translation tests plus one public real-data result.
- A short result paper containing positive and negative findings, not only the best number.

### Success ladder

| Level | Evidence | Submission value |
|---|---|---|
| L0 | Only a transform abstraction and synthetic tests | Engineering groundwork; probably not a strong monthly entry |
| L1 | Proves why zero coverage occurred and restores measurable mesh-arm coverage | Actionable benchmark correction; credible smaller contribution |
| L2 | Independent real-data score with sensitivity/failure analysis | Strong research/benchmark contribution |
| L3 | Confidence or filtering change improves precision at fixed coverage on the independent arm | Strong Progress Prize candidate |
| L4 | Exported high-confidence constraints improve a held-out spiral fit or reduce manual verification time | Best-submission-caliber evidence if reproduced and released early enough |

No accuracy threshold is pre-promised. A low independent score is important if it overturns the shared-parent impression and localizes the estimator’s failure. We must not tune on the mesh arm and call the resulting number held-out; any tuning creates a development split and requires another untouched arm/region.

## Alternative lanes, ranked

### 1. FrameBridge / independent E1 validation — pursue now

High information gain, bounded implementation, primarily CPU/data work, direct connection to an open benchmark commitment, and clear negative-result value.

### 2. Better winding-evidence confidence — conditional follow-on

E1’s rounding-boundary confidence is weak. If FrameBridge restores coverage, study confidence based on multi-ray dispersion, local field support, boundary distance, radial-order margin, transform uncertainty, and agreement across resolutions. Freeze on a development subset; score on a spatially/provenance-independent subset.

### 3. Constraint generator rather than synchronizer — October lane

The external results suggest the evidence graph/localisation is limiting. Candidate ideas include harmonic-safe local pitch, structure-tensor cues at appropriate physical resolution, fibers, verified surface-patch crops, drawn paths, ink rows, intercolumnar gaps, and kolleiseis. Start with a small planted-defect/held-out benchmark before GPU training.

### 4. Current fitter bug with real before/after — opportunistic

Monitor current issues such as scale semantics, outer-shell sizing, and dense-loss availability. Only switch if a reproducible current bug is found and a surgical fix can be demonstrated on real data. The repository snapshot shows that several broad preflight ideas are already implemented upstream.

### 5. Spiral-fitter optimization on Colab — defer

The official autoresearch recipe assumes much more parallel compute than a normal Colab session and uses long stochastic runs. Colab is suitable later for bounded parity tests, ROI experiments, and a small fit—not for pretending to reproduce an eight-GPU optimization campaign.

## Long-term winning thesis

The project should be organized as a ladder, not as disconnected clever ideas:

```text
data/frame contracts
        ↓
independently scored local winding evidence
        ↓
confidence-aware constraint selection
        ↓
global spiral fit with leakage-safe held-out checks
        ↓
flattened surfaces with fiber continuity / no sheet jumps
        ↓
ink detection with cross-region and cross-scroll controls
        ↓
readable columns and a reproducible whole-scroll pipeline
```

The near-term work is not a detour from winning the Grand Prize. Reliable coordinate contracts and independently calibrated winding constraints are prerequisites for a global fit that does not silently jump sheets. The competitive mistake would be to train a large model or run expensive fits before knowing that the evidence, frames, and evaluation are correct.

## Repository strengths

- Strong experiment discipline: manifests, hashes, smoke tests, honest limitations, explicit CPU/GPU separation.
- Useful dependency-light geometry and input-audit modules.
- Good instinct to treat formats and provenance as contracts.
- Existing adapter/test structure can host FrameBridge without a rewrite.
- Documentation already records failures rather than hiding them.

## Repository weaknesses to fix

- The README still presents the old preflight as the active release candidate.
- Experiment registry statuses did not reflect the community’s full-corpus solution or the new cross-frame opportunity.
- No single document separated “verified fact,” “inference,” “open question,” and “decision gate.”
- No explicit coordinate-frame object/schema exists; scale constants are distributed across tools.
- No release license is currently highlighted in the root overview; this must be resolved before a public submission.
- The local `.venv` is a WSL environment, which is easy to misuse from PowerShell. Setup docs should name the execution context explicitly.
- The current repo is private/research-oriented. Public release, issue/PR coordination, Discord registration, and actual submission remain distinct steps.

## Evidence labels used from now on

Every report should mark important statements as one of:

- **Verified here:** reproduced locally with command, artifact, hash, and date.
- **Verified upstream:** supported by current official code/docs or a pinned external result.
- **Inference:** reasoned from evidence but not directly measured.
- **Hypothesis:** a testable expectation registered before the run.
- **Decision:** a project choice, not an empirical fact.

That small convention will prevent the most dangerous research failure in this domain: allowing a coordinate assumption, shared-parent result, or attractive interpretation to harden into “ground truth.”
