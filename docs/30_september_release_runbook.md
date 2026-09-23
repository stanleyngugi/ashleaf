# September FrameBridge Release Runbook

Date: 2026-09-22
Status: **first public release complete; community and submission gates remain active**
Deadline: September 30, 2026, 11:59 PM Pacific
Repository state at drafting: private GitHub repository; public release completed on 2026-09-23 (see [release record](33_public_release_2026-09-23.md))

## Release thesis

FrameBridge is a coordinate-safe, sparse, failure-aware validation layer for local winding evidence on Vesuvius data. It catches a silent, high-impact class of geometry error before it can reach a fitter: points may look valid in mesh coordinates while estimator rays miss the CT-derived field. It makes coordinate frames, acquisition support, applicability, technical coverage, agreement with verified adjacency, confidence, and failure modes explicit and independently checkable. The ambition is a reusable trust layer between candidate geometry and downstream unwrapping.

The release narrative must preserve the full evidence chain:

1. wrong-frame control gives zero support;
2. explicit 2.4 µm ↔ 9.6 µm transforms restore support;
3. generic whole-mesh chords fail even after the frame correction;
4. on applicability-matched, known-adjacent local chords, E1 sometimes recovers the known relation and sometimes fails;
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
| Quantitative diagnostic | Cross-segment E1 agreement and a coverage-aware ranking of where E1 recovers known adjacency | Do not portray this single-target test as predictive improvement |
| Actionable analytics | Identifies long-chord over-counting and ineligible mesh domains | Add a compact failure gallery |
| Comprehensive docs | 30 numbered docs/reports plus protocols and worklog | Add a five-minute quickstart |
| Standard formats | tifxyz, JSON PointCollections, OME-Zarr/respool metadata | Document adapter boundaries explicitly |
| Modular integration | frame types, sparse sampler, support planner, pair builder | Stabilize public function/CLI names |
| Early open source | MIT license added | Publish the audited release promptly |
| Community use | Discord research read-only; no public post yet | Publish, request review, answer issues before deadline |

## Honest headline metrics

### Frozen FB06 evidence

- Three eligible held-out meshes; five held-out meshes outside the frozen local-pair domain.
- 46,318 held-out pairs at 100% technical coverage.
- Per-mesh exact accuracy: 45.60%, 86.72%, 92.07%.
- Pooled exact accuracy: 70.98%.
- Macro exact mean / median: 74.80% / 86.72%.
- Every local pair has a constructed `dw=+1` target. A constant `+1` baseline gets 100% accuracy and zero MAE; the percentages above are **E1 agreement with verified adjacency**, not gains over that baseline.

### Internal FB07 reliability evidence

- Four leave-one-segment-out rotations on already observed segments.
- Geometry ranking at 30% coverage: 91.28% macro, 82.85% worst segment.
- Distance-only at 30% coverage: 90.91% macro, 79.00% worst segment.
- Native E1 confidence at 30% coverage: 78.89% macro, 51.81% worst segment.
- This ranks E1 correctness on known-adjacent `dw=+1` pairs. It does not measure precision among unknown candidate constraints.

Never put “96% accuracy” or “92% accuracy” in a headline without the accompanying population, coverage, and constant `+1` baseline. The 96.06% figure is a post-FB06 pooled threshold analysis at 21.47% coverage. The 92.385% result is a development pilot. The top-line claim is the validated failure-detection workflow, not superiority on an all-`+1` classification task.

## Five-minute local verification

The compact, tracked summary files allow this integrity check in a fresh public clone. It recomputes FB06 counts and MAE from tracked prediction histograms and FB07 aggregates from tracked fold rows. It does **not** rerun E1 against raw CT data:

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

Current expected status: 64 tests passing after the release-checker mutation tests.

The [public-data quickstart](32_framebridge_public_demo.md) separately verifies hash-pinned Paris 4 metadata and produces a conservative one-mesh sparse byte-range plan without CT payload download. It includes tested Windows PowerShell and Unix commands and the pinned external research dependency.

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
- [x] create and audit the local release commits (`5a41689`, then `5820038`);
- [x] owner directed publication on 2026-09-23, contingent on independent audit and fixes.

### Gate B — first public release

- [x] make the repository public after resolving material audit findings;
- [x] push the audited release to `main`;
- create a concise GitHub release/tag only if the committed tree is reproducible;
- include the FB06 and FB07 reports, chart, quickstart, and known limitations;
- avoid uploading ignored CT payloads or pair caches unless separately hosted with appropriate licenses.

### Gate C — community feedback

- use the owner-approved community introduction in [document 34](34_community_outreach_draft_2026-09-23.md) once the channel and posting rules are verified;
- if a channel requires attribution for this type of post, do not silently override either its rule or the owner's chosen copy; select another suitable channel or resolve the conflict with the owner;
- lead with the tool and failure case, not a prize request;
- ask for one concrete test: another user reproducing the release check or trying the frame contract on a different mesh;
- respond quickly to questions and bugs;
- record every public issue, result, and change in a dated project note.

### Gate D — prize submission

- submit before September 30, not at the final minute;
- link the public repository and exact release commit/tag;
- explain standard-format inputs and outputs;
- provide commands, system requirements, runtime, storage, and expected checksums;
- identify the human project owner as responsible for the submission and cite the code, data, upstream contributions, and reproducible evidence where relevant; do not add a tool-credit line to the outreach or submission by default;
- present the negative controls and five ineligible meshes;
- state which numbers are frozen held-out, development, or internal cross-validation;
- explain how the tool can prevent sheet-switch constraints from reaching spiral fitting.

## Proposed public summary

> FrameBridge is an open-source trust layer for Vesuvius winding evidence. It makes 2.4 µm/9.6 µm coordinate frames explicit, proves sparse CT support before evaluation, and exposes when a candidate pair falls outside an estimator's reliable operating regime. The wrong-frame control had zero supported rays; the corrected transform supported all seven rays for 19,999/19,999 pilot pairs. On verified adjacent-wrap pairs, E1 agreement varies sharply across segments, and geometry helps identify where it fails. The release includes reproducible frame and sparse-I/O checks, negative controls, per-segment diagnostics, and a path toward confidence-aware constraint generation. These diagnostic pairs all have target `dw=+1`, so the current accuracy figures are not a gain over a constant-label predictor; mixed-label candidate and downstream fitter tests are the next application milestones.

## Known limitations to publish prominently

1. Every FB05/FB06/FB07 local pair has target `dw=+1`; a constant `+1` predictor scores 100%, and unknown-pair constraint generation is not yet validated.
2. Only three held-out meshes were eligible for the frozen local protocol.
3. One eligible held-out segment scored only 45.60% at full coverage.
4. FB07 is internal cross-validation after all four segment outcomes were known.
5. Distance explains much, and the learned model improves on it only modestly.
6. The current demonstration diagnoses pairwise evidence; it does not yet export production PointCollections into the spiral fitter.
7. Full raw reproduction requires public data downloads and substantial local storage; the compact release check checks generated summaries.

## Stop conditions

Do not publish or submit if:

- the release checker fails;
- any tracked secret or private path is found;
- frozen and exploratory results are mixed in the headline;
- E1 agreement on all-`+1` pairs is presented as predictive improvement;
- the public repository lacks installation/usage instructions;
- the chart cannot be regenerated from the result artifact;
- publication would unintentionally expose data that cannot be redistributed.

## Winning assessment

The official criteria favor actionable, documented real-data analytics, and FrameBridge has a compelling system-level story: it exposes and tests failure modes that can silently poison downstream geometry work. The central competitive risk is that its strongest quantitative diagnostic currently uses a single constructed target and has no fitter integration. Publication should foreground the working validation system, invite use on other meshes, and make mixed-label candidate evaluation and fitter impact the next concrete milestones. That is an ambitious pitch grounded in what we built, not an apology for it.
