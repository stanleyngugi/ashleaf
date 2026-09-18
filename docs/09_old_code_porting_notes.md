# Old Code Porting Notes

## Spiral fitting

The former `analysis_work/spiral-fitting` implementation contains useful components for:

- explicit spiral coordinate construction;
- diffeomorphic transforms;
- fiber and surface-track losses;
- winding-number losses;
- normal consistency and stretch regularization;
- mesh rendering.

It is not directly portable as-is. It has hard-coded Scroll 1 paths, assumptions about volume orientation and shape, and memory-heavy operations that convert large slices to `float32`. The official `villa` spiral fitter is the current upstream implementation and should be the compatibility target.

## Viterbi

Port only behind a small adapter that returns:

- candidate surfaces;
- per-surface confidence/cost;
- coverage and failure diagnostics;
- runtime and memory measurements.

Do not make it directly emit the final binary mask by default. The old GPU report showed that a topologically attractive Viterbi-as-mask result can lose overall quality through sparse coverage and boundary misalignment.

## MWS

The old topology audit contains genuinely useful engineering fixes:

- keep MWS in Cartesian coordinates when affinities are Cartesian;
- make attractive/repulsive sign conventions explicit and test them end to end;
- avoid invalid Numba data structures;
- test thin volumes and oversized offsets;
- detect silent fallback to simpler algorithms.

The old MWS path must not be copied as an opaque binary-mask postprocessor. Its first new test should preserve instance labels and evaluate whether those labels carry information through the downstream surface interface.

## Metrics and validation

The old project has exact and fast metric modules, but some local validation used approximations or train-overlapping volumes. New code should expose metric provenance in every report and avoid mixing proxy scores with official scores.

