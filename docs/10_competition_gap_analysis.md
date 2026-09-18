# Competition Gap Analysis

Checked against the official community-project index on 2026-09-18.

## Existing work we should use, not duplicate

The community already has strong, directly relevant projects:

- `scroll-data-audit` checks catalog and Zarr integrity;
- `tifxyz-repair` repairs stale bounding boxes;
- `Herculaneum Scroll Tools` audits CT support and provides a winding annotator/verifier;
- `winding-sync` generates CT-derived relative constraints and performs robust integer synchronization;
- `spiralcheck` provides held-out spiral-fit evaluation and leakage-aware diagnostics;
- `winding-ruler` studies winding evidence and pitch across the collection;
- `vesuvius-automesh` provides QC-gated automated surface harvesting;
- `TIFXYZ Doctor` diagnoses surface-grid defects;
- several projects already cover GPU meshing, low-memory rendering, consumer-GPU spiral fitting, and GPU-native augmentations.

This is excellent news: it gives us baselines, reusable formats, and a live test of what the community values. It also changes our first-project design.

## Our differentiated target

The proposed first release is now a **cross-tool reliability and benchmark harness**, with winding evidence as the first workload. It should:

1. ingest outputs from the existing audit, synchronization, annotation, and spiral-check tools;
2. run deterministic contract checks before expensive fitting;
3. normalize provenance, versions, coordinate conventions, and confidence semantics;
4. evaluate candidate constraints and final fits on the same held-out protocol;
5. measure manual time saved, failure localization, runtime, memory, and data coverage;
6. emit a single report suitable for upstream issues, monthly submissions, and reproducible comparisons.

The contribution is the bridge and the evidence protocol, not another isolated annotator or another isolated synchronizer.

## High-value gaps suggested by the index

### 1. Cross-tool interface failures

There are many specialized tools, but a user still has to know which output is safe to feed into which next step. Coordinate conventions, spacing, bounding boxes, sentinels, scale semantics, winding direction, and scan resolution should be checked at the boundaries.

### 2. Comparable evaluation

Individual tools report useful numbers, but experiments can still be difficult to compare because they use different regions, splits, or leakage controls. A common manifest and benchmark runner can make incremental and unconventional methods directly comparable.

### 3. Human-effort accounting

The challenge explicitly values tools that are used. We should report annotation minutes, number of corrections, rejected windows, and time-to-first-usable-surface—not only geometric scores.

### 4. Negative-result and failure-mode corpus

Failures are highly informative: phantom predictions, stale metadata, fused sheets with no CT boundary, self-intersections, silent z-slice loss, and false ink. A labeled failure corpus could guide both classical rules and learned models.

## Borrowing plan

- Use `tifxyz-repair`, `TIFXYZ Doctor`, and `scroll-data-audit` as external baselines and fixtures.
- Use `winding-sync` as the robust synchronization baseline; focus our novelty on input-quality calibration, cross-tool provenance, and evaluation.
- Use `spiralcheck` as the fit-level evaluator rather than reimplementing its metrics.
- Use official `villa` formats and adapters so our harness can be consumed upstream.
- Reuse old Viterbi/MWS experiments only as branches inside the benchmark, where they must beat established baselines on held-out data.

