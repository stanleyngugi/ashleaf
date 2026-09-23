# September Winning Sprint — 2026-09-23

Status: **active decision record**. Supersedes any reading of the first public release as the finished September entry. Deadline: September 30, 2026, 11:59 p.m. Pacific, per the current [official prize page](https://scrollprize.org/prizes). Recheck the form and deadline immediately before submission.

## Decision and course correction

The objective is to compete for **best Progress Prize of the month**, not merely to open-source a respectable experiment. Ashleaf/FrameBridge is a strong first-phase contribution: it converts an upstream-known frame correction into a tested contract, validates sparse CT access, and makes silent support/applicability failures visible. The release is worth sharing now because independent use and criticism are valuable on their own. But the prize case is materially stronger if we can also show a *decision or downstream outcome* that a baseline would not achieve.

We should have made that distinction explicit earlier in planning. The single-target `dw=+1` diagnostic was allowed to become the principal score story even though a constant-label predictor gets 100% on that population. That does **not** make the engineering or failure analysis unimportant. It means the next experiment must use a population in which the tool has something nontrivial to decide. No amount of copywriting turns a single-class accuracy number into a discriminative result.

The public pitch is confident: FrameBridge is the trust layer that tells an unwrapping pipeline *which geometric evidence it may rely on and why*. The competition proof we now seek is whether that trust layer improves acceptance, rejection, or fitting on real mixed candidate geometry. Negative controls, baselines, and scope notes make the claim more credible; they are not apologies.

## One-week priority order

### P0 — community release, today

- Post the [owner-approved introduction](34_community_outreach_draft_2026-09-23.md) in a verified, appropriate Vesuvius Discord channel. The browser-control inventory failed on 2026-09-23, so **no Discord post has been made or channel selected by this task**. Resume only when the channel list, rules, and final delivery can be observed; otherwise the owner can post the saved copy directly.
- Ask for a precise external test: independently run the 4.5 MiB metadata quickstart or check the contract on another verified mesh. Record the channel URL, feedback, environment, failures, and fixes. Public use is evidence; an unobserved post is not.
- Link the public repository, quickstart, and one compact failure example in any subsequent prize entry.

### P1 — mixed-label evaluation, first scientific gate

Build a candidate set with independently justified `dw=0`, `+1`, `-1`, and `|dw|>1` relations where defensible. A class should not be manufactured merely to balance the table. Before scoring, freeze the candidate-generation method, label provenance, mesh/scroll split, exclusions, and duplicate/near-duplicate policy. Mark uncertain labels unknown rather than forcing a value. Prevent near-identical chords and same-mesh geometry from leaking across development and held-out splits.

Compare, at minimum, constant `+1`, class-prior/majority, distance-only, native E1 rounding, and FrameBridge's predeclared reason/geometry gate. Report confusion matrices and per-class precision/recall or error, exact accuracy and MAE where meaningful, abstention/coverage, results by mesh, and runtime/storage. A winning claim requires an advantage on the relevant utility at a disclosed coverage—not a favorable number from hand-picked easy pairs. Preserve FB05–FB07 as a separate positive-only diagnostic.

**Gate P1:** If credible mixed labels or independent verification cannot be assembled in time, do not improvise a classifier headline. Promote the strongest reproducible *failure-prevention* case instead, explicitly separate observed failure detection from fitter benefit, and continue this benchmark into October.

### P2 — physical and implementation validation

- Inspect a stratified small sample of predicted successes, failures, and abstentions on CT cross-sections or another defensible geometric reference. Record image/mesh IDs, frame transform, sample coordinates, reviewer judgment, and ambiguity. A visualization is illustrative until it has a documented selection protocol.
- Check dense versus sparse E1 parity on a pinned small case if both paths are available. Use the same rays, interpolation, decoding, orientation, and support rules. Log numerical tolerances and every mismatch; do not call a near-match exact parity.
- Confirm coordinate convention, origin, axis order, voxel-center/corner convention, and transformation provenance in each output. These checks are essential to the product claim even if mixed-label accuracy is modest.

### P3 — a usable decision boundary

Implement a small reason-coded output for candidate constraints: `accept`, `reject`, or `review/abstain`, with source and target frame IDs, CT support, estimator applicability, raw estimate, confidence or gate inputs, and explicit failure reason. Match the community's existing PointCollection/constraint schema through a narrow adapter; avoid inventing an incompatible replacement. Add a CPU fixture and an example that demonstrates one supported and one rejected candidate.

If a real spiral-fitting run is feasible within the deadline, compare the same input set with and without the predeclared gate, holding all other settings fixed. Choose a meaningful outcome—constraint conflict, fit residual, sheet-switch count, or verified geometry—before seeing the result. Report any regression. Do **not** claim fitter improvement from an exported file or a synthetic-only fixture.

**Gate P3:** If the integration cannot be exercised honestly, release the reason-coded adapter and compatibility test as a useful tool, but keep the fitting result open.

## Calendar and deliverables

| Window | Primary deliverable | Evidence gate |
|---|---|---|
| Sep 23 | Community introduction; exact public repo and quickstart; external tester request | Verified post URL or explicit unposted status |
| Sep 24–25 | Frozen mixed-candidate protocol, label provenance, baseline runner | Label audit and no leakage before outcome inspection |
| Sep 26–27 | Held-out mixed-label results; stratified failure cases; parity/registration checks | Per-mesh and per-class metrics with coverage and negatives |
| Sep 28 | Reason-coded adapter and smallest credible downstream comparison | Reproducible fixture; real fitter result only if actually run |
| Sep 29 | Fresh-clone reproducibility pass, external feedback fixes, final evidence freeze | Exact commit, commands, data pins, expected outputs |
| Sep 29–30 | Submit early enough to repair form/link mistakes | Confirmation of submission, not merely a draft |

This is a priority order, not a promise that each study can be completed in seven days. On any day, favor one clean, consequential proof over several weak or retrospectively selected scores. CPU is the default; Colab/GPU is reserved for a measured bottleneck and a pinned experiment plan.

## Submission positioning

Lead with the problem and consequence: silent frame/support mismatches and out-of-domain estimator use can inject false winding evidence downstream. Show the working remedy on public data: explicit contract, sparse acquisition proof, reason-coded gate, negative control, and a reproducible demonstration. If the mixed-label or fitter result clears its gate, put the *measured downstream difference* beside the baseline in the opening paragraph. If it does not, submit the strongest honest tool-and-failure-analysis case; do not let an unfinished stretch goal prevent entry.

The owner is responsible for the submission. Credit `constraint-gauge` and other upstream technical work where used, cite data and code, and keep claims tied to artifacts. The owner-approved community copy has no model/tool attribution line; do not add one by default. Before posting, check whether the selected channel has an applicable attribution rule; if it does, choose another suitable channel or resolve the conflict with the owner. Answer any explicit submission-form question accurately.

## Decision log to maintain

Record each new experiment under `experiments/` and `reports/`, with hypothesis, frozen choices, data/mesh IDs, commit, command, runtime, negative cases, and interpretation. Preserve failed attempts. Update this document when a gate passes or fails, rather than quietly changing the target. The final submission must distinguish completed work, observed evidence, and next-step vision.
