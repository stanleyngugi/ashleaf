# Research Worklog — 2026-09-22

Status: living dated record for the current FrameBridge work session

## Purpose

This log records material progress that is too operational for the strategy documents but important for reproducibility: completed gates, failed assumptions, storage interventions, verification state, and the exact boundary between frozen and exploratory work.

## Completed evidence chain

### FB00 — frame control

- Reproduced false no-overlap under implicit/wrong coordinates.
- Applied the explicit Paris 4 2.4 µm to E1 9.6 µm transform.
- Recovered approximately 95 mm of z support.

### FB01 — physical allocation

- Verified all nine mesh metadata sets, annotations, umbilicus, and group-4 field allocation.
- Established physical xyz overlap rather than relying on z alone.

### FB02 — resident-pool index

- Downloaded and hashed `brick_coords.npy` and `table.npy`.
- Checked the v2 inverse index contract.
- Established the full channel size as 5,105,582,080 bytes and planned selective acquisition.

### FB03 — exact pilot support

- Built 19,999 official generic mesh pairs.
- Wrong frame: 0/19,999 valid.
- Correct frame: 19,999/19,999 pairs with all seven rays valid.
- Acquired and verified the exact sparse support.

### FB04 — frozen generic-pair negative

- Coverage: 1.000.
- Exact signed `dw=1`: 0.000.
- MAE: 69.844142.
- Preserved the result rather than changing the estimator.
- Quantified that generic `dw=1` pairs were about 75× longer than annotation `dw=1` pairs.

### FB05 — preregistered local development pilot

- Wrote the applicability protocol before evaluating local-pair E1 accuracy.
- Built 20,000 same-row adjacent-wrap correspondences.
- Exact signed `dw=1`: 0.92385.
- MAE: 0.0794.
- Coverage: 1.000.
- Labeled this mesh as development, not held-out replication.

### FB06 — frozen multi-mesh replication

- Downloaded and SHA-256 recorded all 27 coordinate TIFFs: 607,697,202 bytes.
- Preserved four eligible pair caches with digest and shape checks.
- Five of eight held-out meshes were out of the frozen protocol's domain because one-wrap boundary trimming left no adjacency.
- Three held-out eligible results: 0.455969, 0.867200, and 0.920700 exact accuracy.
- Pooled held-out exact accuracy: 0.709832 across 46,318 pairs.
- Pooled held-out MAE: 0.508442.
- All eligible pairs had full technical coverage.

### FB06E — exploratory reliability analysis

- Performed only after FB06 was complete.
- Confirmed long gap length is associated with over-counting.
- Pooled held-out descriptive curve:
  - gap ≤16: 0.960583 exact at 0.214711 coverage;
  - gap ≤20: 0.931671 exact at 0.369683 coverage;
  - gap ≤24: 0.897424 exact at 0.508722 coverage;
  - gap ≤32: 0.845842 exact at 0.697029 coverage.
- Did not relabel this curve as frozen or held-out tuning.

## Data and storage intervention

The C: drive reached approximately 7 MB free during coordinate acquisition. The following project-generated caches were removed only after their reproducibility information was preserved:

- FB03 sparse range payload: approximately 117.1 MiB;
- FB05 sparse range payload: approximately 66.75 MiB;
- all-nine coordinate TIFF cache: 607,700,886 bytes including local metadata.

The coordinate cache had a full 27-file URL/byte/SHA manifest. Eligible frozen pair endpoints had been serialized, hashed, and shape-checked before TIFF removal. No source file, tracked report, user document, or unrelated directory was removed.

The FB06 union acquisition was optimized by coalescing exact ranges across gaps of at most 16 resident-pool rows:

- exact occupied rows: 10,803;
- coalescing-only rows: 3,560;
- exact ranges: 1,938;
- transmitted ranges: 1,120;
- durable payload: 470,646,784 bytes.

Every response and every post-write file passed the range, size, and SHA checks.

## Code and verification progress

Implemented or extended:

- explicit frame types and overlap probes;
- resident-pool inverse-index validation and range planning;
- exact multiray support enumeration;
- sparse trilinear sampler with SciPy uint8 parity;
- local adjacent-wrap pair construction;
- all-mesh frozen pair and ray planning;
- coalesced HTTP acquisition;
- all-mesh scorer with pilot/replication separation and eligibility recording;
- pair-level exploratory reliability analysis.

Environment dependency group `benchmark` now records NumPy, tifffile, and SciPy. The complete suite passes: **61 tests, 0 failures**.

## Current interpretation

- Coordinate correctness is solved well enough to support independent evaluation.
- E1 is not universally accurate on all eligible local chords.
- The principal observed error is positive magnitude over-counting, not sign reversal.
- Distance is a strong but incomplete reliability feature.
- The strongest honest September thesis is a failure-aware validation and selective-evidence framework.

## Immediate next gate

FB07 was preregistered and completed from the pinned FB06 caches without rerunning E1. At 30% coverage:

- distance-only macro accuracy: 0.909126; worst segment: 0.790027;
- native-confidence macro accuracy: 0.788943; worst segment: 0.518077;
- geometry-model macro accuracy: 0.912847; worst segment: 0.828495.

The geometry model passed the primary gate but improved only modestly over distance. The next gate is release engineering, not more estimator tuning: build a one-command demonstration, accuracy–coverage visualization, failure gallery, and clear submission narrative. GPU work remains unjustified.

## Release-engineering milestone

- Added an MIT license.
- Exported compact tracked FB06/FB07 evidence with hashes identical to the original generated summaries.
- Added a fail-loudly release checker that enforces the frozen-versus-internal claim boundary.
- Added a dependency-free SVG accuracy–coverage chart generated from tracked result JSON.
- Verified 61 tests, package dependency integrity, JSON parsing, SVG XML, final newlines, staged whitespace, secret patterns, and accidental large files.
- Checked the 2026-09-22 official Progress Prize and winding-constraint criteria and documented direct alignment/gaps in `docs/30_september_release_runbook.md`.
- Created a coherent local release commit on `main`; the branch is one commit ahead of the private remote.
- Did not push, change repository visibility, post to Discord, or submit a prize entry. Those external actions await explicit owner confirmation.
