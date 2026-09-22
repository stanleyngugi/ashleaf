# E1 Applicability-Matched Mesh Protocol

Status: completed preregistered diagnostic protocol following the frozen negative FB04 result. It supplements and does not replace FB04. FB05 was the development pilot; frozen FB06 replication produced three eligible held-out meshes with 45.60%, 86.72%, and 92.07% exact accuracy, plus five ineligible held-out meshes. See the FB06 report; do not interpret FB05 as a universal 92% result.

## Motivation

The existing mesh arm samples arbitrary Cartesian-product pairs between winding levels across an entire verified segment. Its median pair is 1,591 E1 working voxels long and separated by 96° about the umbilicus. The annotation pairs used to develop E1 have median length 64 voxels and median angular separation 0.8°.

Because E1 integrates the physical chord between endpoints, the number of sheets crossed depends on chord geometry, not only on endpoint sheet labels. A fair mechanism test needs independently labelled endpoints whose connecting chord is a local crossing between adjacent wraps.

## Frozen input and mesh interpretation

- Pilot mesh: `20231022170901-on-20260411134726-2.4um.tifxyz`.
- Coordinate hashes: those recorded in FB03.
- Arc-axis selection, five-row wrap consensus, guard distance, wrap boundaries, and seam trimming: reuse the pinned `constraint-gauge/gauge/meshgt.py` implementation.
- Trim one wrap at each end, as in the public mesh arm.
- Transform mesh xyz to E1 working xyz by division by four.
- Public umbilicus: pinned 146-point Paris 4 file.

## Local pair construction

For every retained adjacent-wrap pair and every tenth mesh row:

1. form the two wrap curves at that same mesh row;
2. sample every tenth valid point on the inner curve;
3. find its nearest valid point on the adjacent curve in Euclidean xyz;
4. reject matches whose nearest point is a curve endpoint, because the true perpendicular foot may lie outside the represented span;
5. apply the existing mesh-spacing plausibility guard from `mesh_spacing_um`: distance must be positive and less than half the wrap interval's nominal arc span;
6. deduplicate identical endpoint-index pairs;
7. if more than 20,000 remain, choose 20,000 without replacement using seed 1.

This construction is based only on verified mesh geometry and existing benchmark rules. It does not inspect `grad_mag`, E1 predictions, confidence, or correctness.

## Sign convention

Annotation `wind_a` increases outward from the public umbilicus for 99.926% of existing annotation pairs. Mesh wrap numbering, by contrast, follows parameter direction and has no guaranteed physical orientation.

For each local mesh pair, order endpoints so B has the larger radius about the interpolated umbilicus at pair midpoint z. The declared true signed difference is then `+1`. Pairs with equal radii are rejected before scoring. This is a coordinate/label convention adapter, not a fitted E1 parameter.

## Frozen estimator

Use exactly the FB04 contract: `k=2.773`, `orient=+1`, seven rays, ±6 offset, two-working-voxel sampling, group-4 field, uint8 trilinear output, and the same sparse acquisition. No refitting or sign flip is allowed.

## Metrics and interpretation

Primary diagnostic:

- exact signed `dw=1` accuracy over all answered local pairs.

Secondary diagnostics:

- coverage;
- MAE;
- exact absolute-magnitude accuracy `abs(prediction)==1`;
- sign accuracy among nonzero predictions;
- endpoint distance and angular-separation distributions;
- prediction/confidence calibration;
- result by wrap gap and spatial row.

This protocol may show whether the E1 mechanism transfers to independent geometry. It is not directly comparable to a node-based subject's score on the generic all-pairs mesh distribution, and it must be labelled `local-correspondence diagnostic` in every report.

## Promotion criteria

- If exact signed `dw=1` accuracy is materially above chance with high coverage, extend the same frozen protocol to all nine meshes.
- If magnitude is accurate but sign is not, audit registration/umbilicus conventions without changing the recorded run.
- If both magnitude and sign fail, retain FrameBridge as a benchmark-contract/reliability contribution and do not spend GPU time on E1.
- In all cases, publish FB04 alongside this diagnostic so the negative generic-pair result remains visible.
