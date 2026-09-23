# FrameBridge FB06 Decision — 2026-09-22

**2026-09-23 claim update:** the local-pair targets are all constructed `dw=+1`, so a constant `+1` predictor scores 100%. Read this decision as an E1 agreement diagnostic, not as evidence of predictive improvement. See the [prepublication claim audit](31_prepublication_claim_audit_2026-09-23.md) for the controlling release interpretation.

**2026-09-23 execution update:** the public release is complete. The [winning sprint](36_september_winning_sprint_2026-09-23.md) supersedes the release-work and outreach instructions below; those remain as the historical decision record.

Status: **active strategy decision**
Supersedes: the expectation that frozen FB05 would replicate uniformly across the remaining meshes

## Decision in one sentence

FrameBridge remains the September candidate, but the winning claim is now a reproducible **reliability and applicability framework** with honest heterogeneous replication—not a universal 92% E1 accuracy claim.

## Why this remains worth pursuing

The project now has a coherent evidence chain that few one-off benchmark submissions provide:

1. a known-wrong coordinate control that produces zero support;
2. an explicit 2.4 µm ↔ 9.6 µm frame contract that restores support;
3. verified allocation overlap across nine independent meshes;
4. an exact remote sparse-acquisition system with byte and hash verification;
5. a preserved generic-pair negative result;
6. a preregistered local-pair development pilot;
7. frozen held-out replication with per-segment heterogeneity;
8. a post-result accuracy–coverage analysis clearly separated from the primary result.

That chain is useful to the community even where the estimator fails. It turns silent coordinate/applicability errors into reason-coded outcomes and provides a practical way to export only high-confidence evidence.

## Why it is not yet a winning package

- Only three of eight held-out meshes are eligible under the frozen protocol.
- One eligible held-out mesh scores 45.60% exact accuracy.
- The attractive 96.06% figure operates at only 21.47% held-out coverage and is exploratory.
- No clean one-command public demo, failure visualization, upstream integration, or public discussion artifact exists yet.
- The distance gate explains substantial error but does not fully explain the weak segment.

## Current competitive assessment

The repository is now scientifically credible and potentially prize-worthy as infrastructure, but it is not the obvious monthly winner in its current form. A result-only submission centered on the pilot would be fragile and easy to challenge. A transparent toolkit centered on frames, sparse reproducibility, applicability, and failure-aware confidence has a stronger chance because its utility survives the mixed score.

The correct posture is:

- **high confidence** that the work is real, reproducible, and useful;
- **moderate confidence** that it can become a strong September submission;
- **low confidence** that the current unpolished state would win outright;
- **no honest basis** for claiming likely victory until a release artifact and independent-use story exist.

## Next experiment: FB07

Question: can geometry-only reliability features predict E1 failure across segments without fitting on the evaluated segment?

Candidate features:

- endpoint Euclidean distance;
- chord angle relative to local radial direction;
- angular separation about the umbilicus;
- endpoint and midpoint z;
- local mesh tangent/normal alignment;
- ray disagreement and E1 confidence already produced by the estimator;
- peak multiplicity or dispersion along the seven rays.

Required validation:

1. leave one eligible segment out;
2. fit/calibrate only on the other eligible segments;
3. report precision/accuracy at fixed coverage on the held-out segment;
4. report all three rotations, not only the favorable split;
5. compare against distance-only and estimator-confidence-only baselines;
6. preserve the full-coverage FB06 score beside any selective result;
7. treat three segments as a small-sample diagnostic, not definitive generalization.

FB07 should remain CPU-first. There is no justification for Colab GPU use until a learned representation is shown necessary and the evaluation split is fixed.

## Release work after FB07

**Outcome notice:** FB07 passed its preregistered gate. The geometry model reached 91.28% macro accuracy at 30% coverage with 82.85% worst-segment accuracy, versus 90.91% and 79.00% for distance alone. The improvement is modest; distance remains the default transparent baseline. Proceed to release work without GPU training.

If a simple confidence baseline generalizes:

- add a one-command small-data demonstration;
- produce a plot of accuracy versus coverage by held-out segment;
- render a weak-segment failure gallery showing long chords and over-counts;
- package frame schemas and support planning as reusable library interfaces;
- prepare an AI-disclosed technical write-up;
- ask before posting to Discord or opening any upstream pull request.

If confidence does not generalize:

- stop estimator optimization;
- release FrameBridge as a validation/data-contract toolkit;
- make the mixed FB06 result the worked case study;
- redirect research to E0003/E0004 winding evidence and synchronization.

## Resource policy

Local disk was nearly exhausted during FB06. The project therefore retains hashed endpoint caches and manifests while allowing redownloadable TIFF/range caches to be removed when superseded. Future acquisition plans must check free space before starting and should coalesce request ranges under an explicit byte budget.
