# FrameBridge Public Release — 2026-09-23

Status: public research-toolkit release

Repository: <https://github.com/stanleyngugi/new_vesuvius>

## What shipped

The first public FrameBridge package was pushed to `main` on 2026-09-23 and the GitHub repository was changed from private to public. The audited release commit is `582003844fbf534e4803ea0439a328d93730cf35`, following the main implementation commit `5a41689`.

FrameBridge is presented as a trust layer under construction for virtual-unwrapping evidence. This release already provides an explicit 2.4 µm→9.6 µm coordinate contract, sparse resident-pool index validation and range planning, negative controls, E1 applicability and failure diagnostics on verified-mesh geometry, a CPU-only public-data quickstart, compact checked evidence, tests, and extensive experiment documentation.

Its strongest immediately reproducible user workflow is [the public-data demo](32_framebridge_public_demo.md): fetch hash-pinned small Paris 4 metadata, validate the sparse index/table inverse, and generate the one-mesh 717-range acquisition plan without downloading the CT payload. The full raw E1 research experiments require external public mesh TIFFs, CT bytes, and ignored pair caches and are not reproduced by the compact checker alone.

## Release verification

At publication:

- 64 unit tests passed on native Windows Python with `PYTHONPATH=src`.
- The compact release checker passed and independently recomputed FB06 exact hits/MAE from tracked histograms and FB07 fold aggregates from tracked fold rows.
- A deliberately mutated prediction histogram and a mutated FB07 aggregate both fail the checker tests.
- The FB07 SVG was regenerated from the tracked JSON and parsed as XML.
- `git diff --check` found no whitespace errors after the final fixes.
- A tracked-file privacy/secret scan found no personal home paths or common credential markers; two historical local-path mentions were generalized.
- `gh repo view` confirmed `isPrivate: false` and `main` as default branch; the local branch matched `origin/main` after the release push.

The independent GPT-6 Sol/high audit found no obvious arithmetic error in the frozen sparse E1 implementation, but identified the positive-only target, narrow eligibility, small and uneven FB07 gain, and incomplete raw reproduction/integration as material limits. [The claim audit](31_prepublication_claim_audit_2026-09-23.md) records the detailed disposition.

## The claim we can defend

FrameBridge makes coordinate support and estimator applicability failure observable and reproducible with small public metadata. On the local verified-mesh diagnostic, E1 agreement with constructed adjacent-wrap `dw=+1` pairs varies sharply by segment. Every local target is `+1`, so a constant `+1` predictor would score 100%; these results do **not** prove discriminative constraint generation, fitter benefit, or a new registration result. FB07 is internal leave-one-segment-out ranking of E1 correctness on the four already observed eligible segments, not an untouched holdout. The upstream-known scale correction is credited to `constraint-gauge`; FrameBridge's contribution is its operationalized contract, sparse support proof, and failure analysis.

## What would make it prize-competitive

The release is the beginning of the monthly-prize campaign, not the submission's endpoint. The highest-value next gates are:

1. Ask at least one external user to reproduce the public-data demo or test the frame contract on another mesh; record feedback and fix usability issues.
2. Build a genuinely mixed-label candidate set, including `dw=0`, negative, and multi-wrap relations, and compare with trivial and existing-tool baselines.
3. Inspect a stratified sample of local chords in CT cross sections and verify physical registration or dense/sparse E1 parity.
4. Evaluate a reason-coded accept/reject output in an official-compatible constraint format and measure the effect on spiral fitting.
5. Run adaptive seam trimming only as a newly named exploratory experiment; preserve the original frozen FB06 denominator and result.
6. Submit the public, documented work before the September 30 Pacific deadline with AI assistance disclosed and every metric tied to its evaluation population.

No GPU work is required for these immediate gates; Colab remains reserved for experiments with a controlled CPU baseline and a justified GPU hypothesis.
