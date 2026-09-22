# FB03 — Exact Pilot-Ray Support Plan

Date: 2026-09-22
Experiment: E0011, FrameBridge independent E1 validation
Outcome: **PASS; the corrected pilot has seven-ray allocation support for every frozen benchmark pair**

## Executive result

The official `constraint-gauge` mesh-ground-truth path was run on pilot mesh `20231022170901` with its default mesh stride 10, pair seed 1, and a 20,000-pair cap. It produced 41,944 points and 19,999 deterministic benchmark pairs.

Two support controls were then run without reading any gradient values:

| Control | Pairs with at least one valid ray | Pairs with all seven valid rays |
|---|---:|---:|
| Historical wrong frame: use 2.4 µm mesh indexes directly as E1 working indexes | 0 / 19,999 | 0 / 19,999 |
| Correct frame: mesh xyz ÷ 4 into the 9.6 µm E1 grid | 19,999 / 19,999 | 19,999 / 19,999 |

This reproduces the historical zero-coverage mechanism and proves that the corrected transform restores complete array allocation support for the pilot. It is still not an accuracy measurement because no `grad_mag` values have yet been integrated.

## Pilot ground truth

The pinned benchmark implementation reported:

- eight mesh wraps from five-row consensus counts `[7, 8, 8, 8, 7]`;
- one wrap trimmed at each seam end;
- 41,944 emitted points at stride 10;
- 19,999 sampled pairs at `max_pairs=20000`, seed 1;
- 6,671 pairs with true winding difference one;
- measured sampled bounds of approximately x `13789.24–20839.65`, y `15505.46–24661.14`, z `55456.57–73245.55` in 2.4 µm mesh voxels.

The three coordinate TIFFs are each 24,762,450 bytes. Their pinned SHA-256 digests are:

| File | SHA-256 |
|---|---|
| `x.tif` | `83f9285228392894ec7fbb3cae85965c45ff2ca1d434398147cfca2594088f8c` |
| `y.tif` | `f89d7f8b391e15414affff25d82520096c99ba0907fb6b8dcfd64496ef604168` |
| `z.tif` | `9a5f4bffd45f356d8341c32aae63069bf2d1cc3fe9f2a6bfaac519f84938723c` |

## Ray support algorithm

For each benchmark pair:

1. transform both endpoints from 2.4 µm mesh xyz to 9.6 µm E1 xyz by dividing by four;
2. reproduce the frozen seven offsets from −6 through +6 working voxels in the in-plane perpendicular direction;
3. map each ray to group-4 field zyx by dividing by another four and reversing axes;
4. reject a ray only if an endpoint lies outside the group-4 array—the straight segment then lies outside the convex allocation too;
5. conservatively enumerate every 32³ logical brick intersected by the continuous ray plus a one-field-voxel trilinear halo;
6. map logical bricks through the validated `table.npy` index;
7. omit absent rows, which are defined by `respool` v2 as all-zero.

The wrong-frame control performs the identical process but deliberately omits the mesh-to-working division by four.

## Acquisition result

| Quantity | FB02 rectangular pilot | FB03 actual-ray envelope |
|---|---:|---:|
| Logical bricks | 11,520 | 3,797 |
| Occupied rows | 10,683 | 3,747 |
| Absent zero bricks | 837 | 50 |
| Channel payload | 333.8 MiB | 117.1 MiB |
| HTTP ranges | 717 | 406 |
| Fraction of full 4.755 GiB channel | 6.86% | 2.41% |

The requested-brick count saturated quickly: about 3,573 bricks after 2,000 pairs, 3,784 after 10,000, and 3,797 after all 19,999. This indicates that the pair sample thoroughly covers the pilot's ray corridor rather than continuing to discover disjoint regions.

## What is now established

- The zero-coverage result is reproduced when frames are intentionally confused.
- Every corrected pilot pair has all seven rays inside the declared array allocation.
- The exact sparse channel payload is small enough for a bounded CPU download.
- The original benchmark pair generator, winding labels, trimming, stride, cap, and random seed are preserved.

## What remains unproved

- Origin and registration parity beyond the scale relationship.
- Numerical parity of a sparse sampler against the frozen dense-Zarr E1 path.
- Presence and magnitude of useful density along the rays.
- Correct winding sign from the public umbilicus after transformation.
- Exact winding accuracy, MAE, confidence calibration, and final coverage.

## Gate decision

**Advance to value acquisition and parity testing.** Download the 406 verified HTTP ranges (117.1 MiB), construct a sparse trilinear sampler, prove it against a dense synthetic fixture and an annotated-arm parity slice, then run the frozen pilot score without refitting `k` or orientation.
