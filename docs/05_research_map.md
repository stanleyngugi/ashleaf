# Research Map and Hypotheses

This is a map of experiments, not a claim that every method is appropriate.

## Geometry and winding

- Estimate local pitch from radial profiles, autocorrelation, fibers, and surface normals.
- Treat winding as a noisy integer synchronization problem rather than only a pairwise BFS.
- Compare confidence-weighted least squares, L1 integer synchronization, robust consensus, and cycle-consistency rejection.
- Evaluate variable pitch and local deformation instead of assuming one global Archimedean parameter.

## Surfaces and topology

- Compare probability masks, signed distance fields, normals, and local tangent representations.
- Test Viterbi as a proposal or confidence map rather than a final binary mask.
- Test MWS on affinity/instance outputs and preserve instance identity until the final surface interface.
- Build LOGISMOS-like graph baselines for constrained layered surfaces.
- Compare topology-aware losses against simpler post-processing on the same splits.

## Cross-disciplinary directions

- OCT retinal-layer segmentation: ordered multi-surface graph optimization.
- Connectomics: affinity graphs, agglomeration, MALIS-like objectives, and uncertainty-aware watershed.
- Computational geometry: mesh quality, self-intersection checks, parameterization, and robust projections.
- Physics-inspired optimization: elastic sheets, curvature regularization, and coupled stacked surfaces.
- Optimal transport: matching surface evidence and enforcing globally consistent correspondences.
- Neural implicit fields and level sets: continuous surfaces with differentiable geometric regularization.
- Self-supervision: masked-volume reconstruction, contrastive local geometry, DINO-style feature consistency.
- Active learning: select the next annotation by expected uncertainty reduction and winding impact.

## Evidence standard

Each direction begins with a small synthetic or public-data test. It must beat a deliberately strong simple baseline before receiving large GPU allocations.

