# Prepublication Claim Audit — 2026-09-23

Status: active, before public release

## The product vision

FrameBridge makes winding evidence across resolution levels inspectable. It attaches explicit coordinate frames to geometry, checks whether every estimator ray has data support, acquires only the needed portions of a large CT-derived field, and turns estimator disagreements into concrete failure cases. That is a useful, reusable research instrument even when an estimator performs unevenly.

## Finding: the local diagnostic has one target value

Every FB05 and FB06 local pair was constructed between adjacent mesh wraps and oriented outward, so the declared target is `dw=+1` for every pair. A constant `+1` predictor therefore has 100% exact accuracy and zero MAE on this population. This baseline was missing from the initial reports.

The FB06 numbers measure whether the frozen E1 ray integral recovers the known adjacent relation on each segment. They do not show that E1 beats a trivial classifier, labels unknown candidate pairs, or improves a spiral fit. The FB07 accuracy-at-coverage curve measures ranking of E1 correctness on these known adjacent pairs. It does not establish end-to-end constraint precision among arbitrary candidates.

This is a claim boundary, not a reason to hide the system. The frame contract, sparse evaluation, byte verification, cross-segment diagnosis, and failure analysis remain concrete contributions. A mixed-label candidate evaluation and fitter outcome would strengthen the product case.

## Evidence map

| Result | What it measures | What remains open |
|---|---|---|
| FB03 support | Whether transformed rays lie in the public field | Winding accuracy |
| FB04 generic pairs | E1 on diverse whole-mesh chords | Local mechanism quality, because chords are far outside its intended geometry |
| FB05/FB06 local pairs | E1 agreement with verified adjacent wraps | Unknown-label constraint generation |
| FB06E distance gate | Association between chord length and E1 overcounting | Preselected operating threshold |
| FB07 leave-one-segment-out | Ranking of E1 correctness on four observed eligible segments | New untouched validation and downstream benefit |

## Publication actions

1. State the constant `+1` baseline beside every local-pair exact score.
2. Present FB05/FB06 as an estimator diagnostic and the system as a reusable validator.
3. Present FB07 as internal error-ranking evidence and make its single-class target explicit.
4. Lead with frame safety, sparse reproducibility, and actionable failure detection.
5. Offer the mixed-label and downstream fitter evaluations as the next public collaboration targets.

## Independent audit and release disposition

A separate GPT-6 Sol/high Codex task reviewed the frozen local commit `5a41689` in an isolated worktree on 2026-09-23. It read the code, protocols, reports, tracked compact results, official prize criteria, recent winners, and upstream E1/mesh/respool implementation; recalculated available metrics; and ran 61 tests. Its recommendation: publish an amended research-toolkit release today, **not** the original commit as-is and **not** a high-accuracy production winding-generator claim. The review was read-only; the main task made the changes below.

### Findings and treatment

| Finding | Release treatment | Next scientific test |
|---|---|---|
| All local targets are `dw=+1`; constant baseline is 100% | Explicit beside headline scores in README, FB06/FB07 reports, runbook, chart, and the release checker | Mixed-label candidate set with `dw=0`, negative, and multiple-wrap cases |
| FB07 beats distance by only 0.372 percentage points macro at 30% coverage and loses on three of four folds | Call distance the practical baseline; describe the multifeature gain as tentative | Frozen selector on unseen segments/scrolls |
| Five of eight held-out meshes fail a fixed ≥4-wrap eligibility gate | Preserve the FB06 denominator and exclusions | Separately named exploratory adaptive trim with seam/wrap review |
| Nearest-chord labels and physical registration have not been independently inspected | Treat E1 results as mesh-constructed positive-only diagnostics; do not claim registered ground-truth crossing or fitter benefit | Stratified CT cross-section inspection, dense/sparse E1 parity, independent landmarks |
| The old release checker trusted saved aggregates | Recompute FB06 from tracked histograms and FB07 from fold rows, with mutation tests; still label this summary integrity, not raw-data reproduction | Publish a manageable pair-level capsule or reproducible raw runner |
| A fresh clone lacked a real FrameBridge demo and the raw pipeline depended on ignored external code | Add a hash-pinned public-data metadata/index planning quickstart with Windows/Unix commands and the exact `constraint-gauge` pin | Package a small fully reproducible ray-support and E1 example |
| No production PointCollections export or spiral-fit outcome | Position this as a research validation layer with a concrete integration roadmap | Export reason-coded candidates and compare downstream fits |
| Personal machine paths appeared in two documents | Replace with neutral paths before public release | Keep automated privacy scan in release checks |

The public 2.4→9.6 µm correction is credited to upstream `constraint-gauge` GATE0 A25. FrameBridge's distinctive contribution is operationalizing that frame contract in a sparse, fail-loud validation workflow and characterizing when a local estimator disagrees with constructed mesh adjacency. The FB05 and FB07 plans were locally specified before their respective runs but were not independently public-timestamped in advance; public language must not overstate preregistration.

### Resolved in this release

- [x] Positive-only target and constant-predictor baseline in the main narrative.
- [x] FB07 chart caption identifies positive-only E1 agreement and 100% baseline.
- [x] Summary checker recomputes available metrics instead of trusting stored aggregates.
- [x] CPU-only public-data quickstart, with exact outputs, pinned hashes, Windows/Unix commands, and storage boundary.
- [x] Pinned external `constraint-gauge` commit documented for the full research runners.
- [x] Personal path references removed.
- [x] No production constraint-export or fitter-improvement claim.

### Open limitations at publication

- Raw FB04–FB07 CT evaluation is not reproducible from the compact tracked JSON alone; CT bytes, pair-level caches, and mesh TIFFs remain external/ignored.
- Physical frame origin, axis parity, umbilicus registration, and group-4 mapping need independent landmark or numerical parity checks.
- The four observed segments come from the same Paris 4 scan; cross-scroll generalization is untested.
- The fixed seam-trim protocol excludes five replication meshes, so the aggregate describes only three eligible meshes.
- There is no demonstrated improvement in production winding constraints, PointCollections accepted by a fitter, or final spiral quality.

These are well-defined experiments, not reasons to diminish the engineering deliverable. The September release gives the community a usable diagnostic foundation and specific validation questions to challenge or extend.
