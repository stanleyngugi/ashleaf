# September FrameBridge Release Runbook

Date: 2026-09-22
Status: **active release plan**
Deadline: September 30, 2026, 11:59 PM Pacific
Repository state at drafting: private GitHub repository; local release candidate not yet published

## Release thesis

FrameBridge is a coordinate-safe, sparse, failure-aware evaluation toolkit for local winding evidence on Vesuvius data. Its value is not that one estimator always works. Its value is that it makes coordinate frames, acquisition support, applicability, technical coverage, accuracy, confidence, and failure modes explicit and independently checkable.

The release narrative must preserve the full evidence chain:

1. wrong-frame control gives zero support;
2. explicit 2.4 µm ↔ 9.6 µm transforms restore support;
3. generic whole-mesh chords fail even after the frame correction;
4. applicability-matched local chords can be highly accurate;
5. frozen held-out replication is heterogeneous;
6. distance and geometry provide useful cross-segment reliability ranking;
7. abstention/coverage is a first-class output, not a hidden filtering trick.

## Official-prize alignment

Checked against the official Vesuvius Challenge pages on 2026-09-22.

The [Progress Prize rules](https://scrollprize.org/prizes#progress-prizes) state that the best submission receives $20,000 each month and that favored submissions are released early, actually used, improve real-data results, reveal actionable information, and are well documented. Core requirements call for a specific problem and solution, a clear implementation path and demonstration, significant advantages over existing solutions, comprehensive documentation and examples, standard community formats, consistent outputs, and modular integration.

The official [Winding Constraints guide](https://scrollprize.org/open_problems/winding_annotations) says local accurate constraints are central to scalable unwrapping, and that an ideal generator is accurate or confidence-aware, fast, easy to verify, and general enough to integrate into global fitters.

FrameBridge alignment:

| Official preference | Current evidence | Remaining release work |
|---|---|---|
| Specific real-data problem | Silent coordinate/applicability failure in winding evidence | Put the problem in the first README screen |
| Quantitative improvement | Reliability selection from 70.98% full held-out pooled accuracy to 91%+ internal LOSO at 30% coverage | Keep frozen and internal evidence visually distinct |
| Actionable analytics | Identifies long-chord over-counting and ineligible mesh domains | Add a compact failure gallery |
| Comprehensive docs | 30 numbered docs/reports plus protocols and worklog | Add a five-minute quickstart |
| Standard formats | tifxyz, JSON PointCollections, OME-Zarr/respool metadata | Document adapter boundaries explicitly |
| Modular integration | frame types, sparse sampler, support planner, pair builder | Stabilize public function/CLI names |
| Early open source | MIT license added | Repository is still private; publication requires owner approval |
| Community use | Discord research read-only; no public post yet | Publish, request review, answer issues before deadline |

## Honest headline metrics

### Frozen FB06 evidence

- Three eligible held-out meshes; five held-out meshes outside the frozen local-pair domain.
- 46,318 held-out pairs at 100% technical coverage.
- Per-mesh exact accuracy: 45.60%, 86.72%, 92.07%.
- Pooled exact accuracy: 70.98%.
- Macro exact mean / median: 74.80% / 86.72%.

### Internal FB07 reliability evidence

- Four leave-one-segment-out rotations on already observed segments.
- Geometry ranking at 30% coverage: 91.28% macro, 82.85% worst segment.
- Distance-only at 30% coverage: 90.91% macro, 79.00% worst segment.
- Native E1 confidence at 30% coverage: 78.89% macro, 51.81% worst segment.

Never put “96% accuracy” or “92% accuracy” in a headline without the accompanying population and coverage. The 96.06% figure is a post-FB06 pooled threshold analysis at 21.47% coverage. The 92.385% result is a development pilot.

## Five-minute local verification

The compact, tracked evidence files allow this check in a fresh public clone:

```bash
PYTHONPATH=src .venv/bin/python scripts/check_framebridge_release.py \
  --fb06 experiments/results/framebridge_fb06_summary.json \
  --fb07 experiments/results/framebridge_fb07_loso.json
```

Expected first field:

```json
{"release_check": "PASS"}
```

Regenerate the publication chart directly from the pinned result:

```bash
PYTHONPATH=src .venv/bin/python scripts/render_framebridge_fb07_svg.py \
  --input experiments/results/framebridge_fb07_loso.json \
  --output reports/assets/framebridge_fb07_accuracy_coverage.svg
```

Run the full test suite:

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
```

Current expected status: 61 tests passing.

## Publication sequence

### Gate A — repository hygiene

- [x] permissive MIT license;
- [x] generated data and secrets ignored;
- [x] full test suite passing;
- [x] frozen and exploratory evidence labeled separately;
- [x] chart generated from result JSON;
- [x] fail-loudly release checker;
- [x] secret and accidental-large-file audit (no credential matches; no non-ignored file over 10 MiB);
- [x] inspect the complete staged diff;
- [x] create a local release commit (`b3c6f1e` before final documentation amendment);
- [ ] owner confirmation before making the repository public or pushing release changes.

### Gate B — first public release

- make the repository public only after approval;
- push one coherent release commit;
- create a concise GitHub release/tag only if the committed tree is reproducible;
- include the FB06 and FB07 reports, chart, quickstart, and known limitations;
- avoid uploading ignored CT payloads or pair caches unless separately hosted with appropriate licenses.

### Gate C — community feedback

- post an AI-disclosed technical summary in the appropriate Discord channel only after approval;
- lead with the tool and failure case, not a prize request;
- ask for one concrete test: another user reproducing the release check or trying the frame contract on a different mesh;
- respond quickly to questions and bugs;
- record every public issue, result, and change in a dated project note.

### Gate D — prize submission

- submit before September 30, not at the final minute;
- link the public repository and exact release commit/tag;
- explain standard-format inputs and outputs;
- provide commands, system requirements, runtime, storage, and expected checksums;
- disclose AI assistance;
- present the negative controls and five ineligible meshes;
- state which numbers are frozen held-out, development, or internal cross-validation;
- explain how the tool can prevent sheet-switch constraints from reaching spiral fitting.

## Proposed public summary

> FrameBridge is an open-source validation layer for Vesuvius winding evidence. It makes 2.4 µm/9.6 µm coordinate frames explicit, proves sparse CT support before evaluation, and reports applicability and accuracy–coverage rather than silently emitting every constraint. On frozen local-pair replication, E1 was strong on two held-out Paris 4 meshes and weak on a third; five meshes were outside the preregistered pairing domain. Leave-one-segment-out diagnostics show that simple geometry can rank reliable pairs substantially better than native E1 confidence. The release includes the negative controls, sparse byte-range verification, per-segment results, tests, and failure analysis.

## Proposed AI disclosure

> This project was developed with substantial assistance from OpenAI Codex for repository inspection, code generation, test design, documentation, web research, and experiment orchestration. The human project owner directed the objective and publication decisions. All reported numerical results were produced by the checked-in scripts against publicly identified data; frozen, exploratory, and internal-cross-validation evidence are labeled separately. No AI-generated claim is used as a substitute for the recorded artifacts, tests, or hashes.

## Known limitations to publish prominently

1. Only three held-out meshes were eligible for the frozen local protocol.
2. One eligible held-out segment scored only 45.60% at full coverage.
3. FB07 is internal cross-validation after all four segment outcomes were known.
4. Distance explains much, and the learned model improves on it only modestly.
5. The current demonstration validates pairwise evidence; it does not yet export production PointCollections into the spiral fitter.
6. Full raw reproduction requires public data downloads and substantial local storage; the compact release check uses generated summaries.

## Stop conditions

Do not publish or submit if:

- the release checker fails;
- any tracked secret or private path is found;
- frozen and exploratory results are mixed in the headline;
- the public repository lacks installation/usage instructions;
- the chart cannot be regenerated from the result artifact;
- publication would unintentionally expose data that cannot be redistributed.

## Winning assessment

The official criteria favor exactly the kind of actionable, documented real-data analytics FrameBridge now provides. The principal competitive risk is not the mixed FB06 score; it is failure to turn the work into a usable, public, community-tested tool before the deadline. The release should therefore prioritize clarity, reproducibility, integration, and early feedback over additional model sophistication.
