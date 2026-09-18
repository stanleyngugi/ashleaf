# September 2026 Progress-Prize Release Plan

Status: private research repository; **not yet a submitted or public release**. The official [Progress Prize rules](https://scrollprize.org/prizes) list the next deadline as September 30, 2026, 11:59 p.m. Pacific. They favor early release, actual use, measurable real-data improvement, actionable diagnostics, and documentation. The aim is therefore a focused reliability contribution, not a claim that our tiny smoke sample fixes virtual unwrapping.

## Candidate contribution

**Spiral-input fit-window preflight**: given a Z interval, TIFXYZ patches, and public winding annotations, show how many patches a cached bbox selects, how many actually have usable vertices, and how many annotation points fall in that window. Flag false negatives before an expensive fit. Include metadata-only and pixel-aware modes, explicit `unknown` status for patches not scanned, and machine-readable JSON.

The present [Paris 4 reproduction](../reports/2026-09-18_fit_window_false_negative.md) proves a false-negative selection on **two selected patches**. It does not establish frequency across the corpus or quantify fitter improvement. The upstream [stale-bbox issue](https://github.com/ScrollPrize/villa/issues/1272) already documents the defect; our prospective value is the integrated preflight and reproducible workflow.

## Release gates, in execution order

1. **Reliability:** run the complete test suite; add malformed-metadata, no-mask, empty-patch, scan-limit, and boundary-window cases. Confirm status codes and JSON schema. Fix every misleading `unknown` or `pass` outcome.
2. **Breadth:** run on more public patches selected before seeing their failures. Record both per-patch and per-window confusion counts; include clean controls. Hash and version all downloaded inputs. Avoid extrapolating from the known-bad patch.
3. **Fitter relevance:** inspect current `villa` selection code and reproduce one tiny fitting or patch-selection workflow. Establish whether the current fitter itself still uses the stale cached bbox, or whether our detector mainly protects downstream/custom workflows. If the core fitter is already fixed, say so and narrow the release claim.
4. **Comparative baseline:** compare against a metadata-only selector and any maintained upstream validation. Report newly caught failures, false alarms, added runtime/memory, and cases left unknown by the size cap. Do not market another TIFXYZ linter as novel.
5. **Usability:** one-command fresh-environment demo, sample output, clear nonzero exit semantics, help text, and a small failure gallery. Package an optional pixel dependency group without forcing CT-volume downloads.
6. **External feedback:** share a public, permissively licensed release at a deliberate point; seek an upstream issue/PR or community user report; incorporate the response. Keep this private repository private until the release decision. Verify licensing and submission requirements first.
7. **Submission:** assemble a short evidence report with the exact commit, data hashes, commands, limitations, and real-data before/after comparison. Submit via the official channel before the deadline if the evidence meets the bar. A repo push alone is not a prize submission.

## Parallel research lanes

The monthly artifact is only one lane. Continue independent, falsifiable experiments in winding synchronization, Viterbi proposals, instance-aware MWS, graph/topology, implicit geometry, self-supervised representations, and GPU tiling. Use the same manifest and held-out evaluation discipline. The [external winding benchmark](18_external_winding_benchmark.md) must check accuracy *and* coverage; internal constraint agreement cannot stand in for truth. GPU work starts with CPU parity and bounded-memory I/O when hardware arrives.

## Current evidence and constraints

- Implemented: TIFXYZ metadata/pixel audit, OME-Zarr metadata audit, ROI memory planner, point-collection audit, external-benchmark adapter, and fit-window preflight.
- Measured: one known stale-bbox patch yields 50 usable vertices in a window that metadata excludes; a clean control yields none there.
- Unmeasured: full-pack prevalence, fitter outcome improvement, end-user adoption, and GPU scaling.
- No full CT chunks or GPU experiments have been run in this phase.
