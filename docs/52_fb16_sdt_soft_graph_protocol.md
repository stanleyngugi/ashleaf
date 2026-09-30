# FB16 — fixed-connectivity SDT review in a CPU winding solver

Status: **exploratory, retrospective protocol written before running FB16 scoring**. Both the FB08 holdout labels and the FB15 SDT results have already been inspected. This is therefore an engineering diagnostic, not a blind held-out result or official spiral fit. Do not tune the multiplier, change the edge population, or select an arm after viewing FB16 outcomes and then describe it as prospective.

## Question

Does FB15's fixed magnitude-disagreement flag improve *downstream winding assignment*, rather than only filtering pairwise errors, when all E1 edges and all graph connections are kept? FB10's gate-first forest changed no assignments, and FB12's uniform 4× gate boost made no meaningful improvement. FB16 instead downweights only the gate edges on which E1 and the independent surface crest cue disagree. This is a small, controlled test of whether the new review information has solver value.

## Fixed input and arms

Use the original FB08 relative-winding **holdout** candidate population and frozen E1 outputs. For each annotated point collection, include every answered nonzero E1 edge with its native confidence weight in the existing CPU `solve_weighted_winding` least-squares/rounding solver. Do not remove any edges; the graph and connected-pair coverage must be identical in all arms. Evaluate exact pairwise winding differences and mean absolute pairwise error against the same human relative annotations, with per-collection outcomes and assignment digests. This is not the official Villa spiral fitter.

The FB15 SDT cue exists for the 207 original FB08 numeric-eligible gate edges. It flags 34 E1/SDT magnitude disagreements (10 wrong and 24 correct E1 proposals) and leaves 173 agreements (166 correct and seven wrong). Use its *flag only*, never replace E1's signed winding with the crest count in this experiment. Frozen treatment multiplier: **0.25×** native confidence on the 34 flagged edges. This is the reciprocal of FB12's exploratory 4× gate boost, selected for a clearly interpretable strength rather than tuned on FB16 outcomes.

Evaluate four arms:

1. `confidence_weight`: unchanged E1 confidence on all edges.
2. `SDT_disagreement_x0p25`: downweight the 34 flagged original-gate edges by 0.25, no others.
3. `confidence_low_x0p25`: within each collection, downweight the same number of gate edges as arm 2, selecting lowest E1 confidence then ID. This matches the review burden and collection structure.
4. `hash_null_x0p25`: within each collection, downweight the same count selected by SHA-256 of `FB16-null-v1:` plus edge ID. This is a deterministic structural null, not a probability interval.

All arms use identical candidate edges, node sets, components, gauge, integer rounding, and truth. Report absolute counts, coverage, MAE, per-collection changes, and differences from baseline. A positive treatment result against both matched controls would motivate an official fitter experiment; a negative result should close the simple 0.25× integration and preserve FB15 as a review tool. Neither outcome authorizes production export or proves surface-field physical semantics.

## Provenance and interpretation rules

The scorer must verify FB08 and FB15 freeze/source hashes, the human annotation hash, and the ignored FB15 retrospective result hash. Its output belongs in `artifacts/framebridge/`, with a dated decision report in `reports/`. The original FB08 gate remains registration-unverified. Pairwise node comparisons within a collection are highly dependent, so do not attach independent-binomial uncertainty or claim generalization from the number of node pairs. State the number of collections whose assignments changed and show the worst regressions as well as improvements. No GPU is required for this CPU diagnostic; Colab is reserved for a subsequent controlled official-fitter run if warranted.
