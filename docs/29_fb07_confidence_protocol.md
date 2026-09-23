# FB07 — Leave-One-Segment-Out Confidence Protocol

Status: **specified locally before running FB07 values; not publicly timestamped in advance**
Evidence class: internal cross-validation on already observed FB05/FB06 segments; not new held-out evidence

## Question

Can simple geometry and native E1 confidence rank local adjacent-wrap pairs by correctness across segments, or is the FB06E distance curve a segment-specific post-hoc artifact?

## Fixed population

Use the four FB06-eligible segments and their unchanged pair caches/predictions:

- `20231005123336`
- `20231012184424`
- `20231016151002`
- `20231022170901`

The binary correctness label is exactly `prediction == +1`, because every pair's declared local adjacent-wrap truth is `dw=+1`. No pair is regenerated and E1 is not rerun.

This is a positive-only estimator diagnostic. A constant `+1` predictor has 100% exact accuracy on the pair labels; the ranking exercise asks only where frozen E1 agrees with them.

## Cross-validation

Run four leave-one-segment-out rotations. For each rotation:

1. fit any learned standardization and model parameters on the other three segments only;
2. score the untouched segment without using its correctness labels for fitting;
3. rank that segment's pairs by the model score;
4. report accuracy/precision at fixed coverages 10%, 20%, 30%, 50%, 70%, and 100%;
5. preserve results for every rotation before pooling.

Selecting the top fraction uses only scores on the test segment, not its labels. It evaluates ranking at fixed operational coverage, not deployment of an absolute threshold.

## Frozen baselines

1. **Distance only:** score is negative `log1p(endpoint_distance)`.
2. **Native confidence only:** score is the frozen E1 rounding confidence.

## Learned geometry model

Use logistic regression with L2 regularization and training-fold standardization. Fixed features are:

- `log1p(endpoint_distance)`;
- native E1 confidence;
- angular separation around the public umbilicus;
- absolute z displacement divided by endpoint distance;
- radial alignment: xy chord projected onto the outward radial direction at the midpoint;
- interaction `log1p(distance) × angular separation`.

No predicted winding value is a feature. In particular, the model may not use `prediction == 1`, because that would restate the correctness label for this all-`dw=1` diagnostic.

Optimization uses deterministic SciPy L-BFGS-B with an intercept, standardized non-intercept features, L2 coefficient 1.0, and no random initialization.
The training loss gives each training segment equal total weight and each pair equal weight within its segment, so the largest segment cannot dominate the fit.

## Primary evaluation

Primary: macro mean accuracy at 30% coverage across the four held-out-segment rotations.

Secondary:

- per-segment accuracy at every fixed coverage;
- macro mean at every fixed coverage;
- worst-segment accuracy at every fixed coverage;
- pooled selected-pair accuracy, reported only after per-segment values;
- full-coverage accuracy as a consistency check against FB05/FB06.

## Interpretation gates

- **Promising:** learned geometry model exceeds both baselines in macro accuracy at 30% coverage and does not reduce worst-segment accuracy.
- **Distance sufficient:** distance-only is tied or better; do not add model complexity.
- **Non-generalizing:** no method gives a useful worst-segment improvement at 30–50% coverage; stop E1 confidence optimization.
- **Never headline as held-out:** all four segment labels were known before this protocol was written. Results guide engineering and the next data split only.

## Reproducibility

Inputs are the SHA-pinned FB06 pair caches and FB06E detail arrays. The output must include model coefficients per fold, feature standardization values, selected counts, per-fold tables, macro/worst/pooled summaries, input hashes, and the exact protocol label `internal_loso_post_FB06`.
