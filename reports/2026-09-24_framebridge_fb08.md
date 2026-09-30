# FrameBridge FB08 — empirical result and decision record

Evidence date: 2026-09-24. The full methods, separate-arm tables, spatial buffer, matched window, accepted-error analysis, CT metadata check, and limitations are in [`docs/38_fb08_frozen_gate_holdout.md`](../docs/38_fb08_frozen_gate_holdout.md). The pre-holdout development record is [`docs/37_fb08_mixed_constraint_development_2026-09-23.md`](../docs/37_fb08_mixed_constraint_development_2026-09-23.md). The local tracked freeze is [`protocols/FB08_mixed_constraint_gate_freeze.json`](../protocols/FB08_mixed_constraint_gate_freeze.json).

## Primary result

The unchanged numeric gate (`min endpoint |chord·normal| ≥0.75`, E1 confidence ≥0.75, answered nonzero E1) emits **207/1,049** relative-winding held-out candidates across **51/65** collections. **190/207 = 91.79%** are exact signed annotations. Whole-collection bootstrap interval: **86.49–95.95%** precision; candidate coverage **19.73%**, bootstrap interval **16.17–24.24%**. On the separately selected same-winding arm after a coordinate-only 16-working-voxel cross-split buffer, it emits **0/1,742** false nonzero relations across **35** eligible collections; the unbuffered arm is also **0/2,863**. This is a conditional numeric result, not production export or proof of zero future false accepts.

The matched-geometry window (`dz<1`, length 10–50 working voxels) gives **123/130 = 94.62%** exact accepted relative relations, **0/646** accepted same-winding relations. Confidence-only E1 on that window gives **143/151 = 94.70%** relative precision but **150/646** same-winding false accepts. On the full buffered population, confidence-only gives **223/256 = 87.11%** relative precision and **397/1,742** same false accepts. The normal gate is principally an **applicability discriminator**, not a universal E1 error correction.

## Failure and integration decision

There are **17 wrong accepted relative relations**, all correct-sign, off-by-one-wrap magnitude errors. The high-trust edge set is sparse: in a post-hoc fixed BFS graph diagnostic, it connects only **5.02%** of possible within-collection node pairs (91.44% exact among connected pairs) versus 88.06% pairwise connectivity for all E1 edges (33.24% exact among connected pairs). Hard-filtering by itself is **not** a downstream graph win. The next technical direction is to retain trusted edges as seeds while using soft/review evidence for connectivity, add an independently tested magnitude/cycle check, and measure a fixed fitter or winding-assignment outcome. The post-hoc graph diagnostic is exploratory, not a frozen primary metric.

The registration latch in `src/scroll_lab/constraint_gate.py` stays off. Official loader semantics, canonical CT L2 metadata, group-4 pool shape, and six deterministic CT anchors support the selected frame but do not prove exact independent registration or official dense-fitter parity. A sparse grad-magnitude per-z screen found no all-zero slices among **1,664** z slices with at least eight acquired bricks; it cannot rule out other field defects. No GPU was used or needed for FB08.

A research-only, development-only `vc_pointcollections_json` adapter generated 518 paired collections / 1,036 points from numeric proposals without copying human truth labels. The pinned local Villa point-collection loader recognized all 518 as annotated relative collections. This is **format parity only**, not a fitter run; the adapter output and sidecar state that registration is unverified and production use is blocked.

## Provenance and checks

- Raw relative annotation SHA-256: `a3243511d4eb91387a9b32f4dbff11514b08c3ae36e9b2a2b8222607b4883ac1`; same-winding SHA-256: `d9be52c5ebb42853f75f235241cbfd159738f6f34468bcd182523bc91dc91048`.
- Candidate manifest SHA-256: `2cfdd117e5e39096015eeadb94cbe3ac72341c53d25eaf1badcfa275a4dcae3c`; seven-ray plan SHA-256: `16d90c62276dbb645d5740a999d501a65e0952ec3c02a34ac57ffd02b791c4cc`.
- Normal-feature SHA-256: `f5e6824d9bb10db8c7f58ba385e73fc100b9fcbed5011d10cca659ed9904e917`; coordinate-only spatial-buffer SHA-256: `7c6de3b4d5356ef0228e3dd8e14d70da86b74b99b87adce93a48eb437cec815b`.
- The freeze pins these plus gate-source/development-comparison/CT spot-check hashes. `scripts/run_mixed_candidate_e1.py` refuses holdout without a matching freeze; `scripts/evaluate_fb08_frozen_gate.py` verifies all relevant hashes and uses `src/scroll_lab/constraint_gate.py` itself.
- All 80 unit tests passed after the gate and sparse integer-sampling additions. The full suite should be rerun at release; no external PR or GitHub push is part of this report.

Raw challenge annotations, CT chunks, and sparse field bytes remain ignored locally and are not redistributed. The data-server [license](https://dl.ash2txt.org/LICENSE.txt) and official [Villa source](https://github.com/ScrollPrize/villa) govern access and integration. Do not describe this result as improved spiral fitting or automatic production constraint generation.
