# FB02 — Sparse Resident-Pool Range Plan

Date: 2026-09-22
Experiment: E0011, FrameBridge independent E1 validation
Outcome: **PASS for index integrity and deterministic acquisition planning**

## Executive result

The current public Paris 4 group-4 `grad_mag` resident-pool indexes are structurally valid and mutually consistent. They allow exact reconstruction of any requested region from fixed HTTP byte ranges while synthesizing omitted logical bricks as zeros, as required by the official format.

The full channel is 5,105,582,080 bytes (4.755 GiB). A conservative union of all nine ray-padded mesh bounding boxes would require 1,677,164,544 bytes (1.562 GiB) across 2,496 contiguous HTTP ranges. The smallest one-mesh pilot is `20231022170901`, requiring at most 350,060,544 bytes (333.8 MiB) before using actual ray coordinates.

The box plan is intentionally an upper bound. The next step reads that mesh's coordinate TIFFs, constructs the actual frozen benchmark pairs, rasterizes the seven-ray envelopes into logical bricks, and requests only those rows.

## Format proof

The implementation was read directly from the pinned official Villa source:

- `pack_resident_pools.py` writes one reserved zero row, then one fixed-size row per occupied brick;
- `table.npy` maps logical `(z,y,x)` brick coordinates to pool rows;
- `brick_coords.npy` is the inverse row-to-coordinate mapping;
- absent table entries map to row zero and therefore read as no-data/all-zero;
- `sparse_cuda_cache.py` gathers samples by table row and C-order local voxel offset.

For this field:

| Property | Value |
|---|---:|
| Format | `respool` v2 |
| Array shape, zyx | 4737 × 2044 × 2044 |
| Brick shape, zyx | 32 × 32 × 32 |
| Brick payload | 32,768 bytes |
| Grid shape, zyx | 149 × 64 × 64 |
| Rows including reserved zero | 155,810 |
| Occupied rows | 155,809 |
| Full channel bytes | 5,105,582,080 |
| HTTP range support | `Accept-Ranges: bytes` |

The validator proved:

1. metadata geometry is internally consistent;
2. both NPY arrays have the declared dtype and shape;
3. row zero is exactly `(-1,-1,-1)`;
4. every occupied coordinate is unique and inside the grid;
5. every table value is a valid row;
6. `table[brick_coords[row]] == row` for every occupied row;
7. the table has exactly 155,809 nonzero cells.

## Pinned index inputs

| File | Bytes | SHA-256 |
|---|---:|---|
| `brick_coords.npy` | 1,869,848 | `bfe74a188964bfa188e61ae7e55d32309d645f579b2c9d47066cbd3c9cd87a10` |
| `table.npy` | 2,441,344 | `90edae136224642c7aeee02939dc05911e4c4a97fdfcb7390de539feac180848` |

The two indexes total only 4.11 MiB and are now part of the hash-pinned metadata fetch command.

## Coordinate and sampling envelope

One group-4 field voxel corresponds to:

```text
38.4 µm = 16 mesh voxels at 2.4 µm
          = 4 E1 working voxels at 9.6 µm
```

The frozen E1 uses seven in-plane rays with maximum offset ±6 working voxels. FB02 therefore expands each mesh bounding box by ±1.5 group-4 voxels in x and y, adds one voxel of trilinear interpolation halo, clips to the array, then selects intersecting logical bricks.

## Per-mesh conservative costs

These values cover full rectangular mesh boxes, not actual rays:

| Mesh | Payload MiB | Ranges | Occupancy |
|---|---:|---:|---:|
| `20231022170901` | 333.8 | 717 | 92.7% |
| `20231031143852` | 464.6 | 1,062 | 100.0% |
| `20231016151002` | 487.6 | 1,174 | 93.8% |
| `20231221180251` | 489.8 | 1,045 | 100.0% |
| `20231106155351` | 525.2 | 1,121 | ~100.0% |
| `20230929220926` | 933.2 | 1,393 | 91.4% |
| `20230702185753` | 979.9 | 2,227 | 91.4% |
| `20231005123336` | 986.2 | 1,639 | 89.5% |
| `20231012184424` | 1,288.5 | 2,476 | 88.8% |

Selection of `20231022170901` as the pilot is objective: it has the lowest box-level payload, and its three coordinate TIFFs total approximately 70.9 MiB.

## Important semantic correction

An absent resident-pool brick does not mean the field is undefined there. It means the entire brick is zero after source sparsity and CT masking. A correct sparse evaluator supplies zeros without a network request. Conversely, an occupied brick only means at least one byte is nonzero; it does not prove a particular ray has signal.

Therefore FB02 reports occupancy and acquisition cost, not “coverage.” True estimator coverage is decided after constructing and sampling the actual rays.

## Reproduction

Run `scripts/plan_framebridge_ranges.py` with the three pinned index paths, the public channel URL, an output path, and one repeated `--mesh-meta` argument for every mesh to include. The recorded all-nine artifact is `artifacts/framebridge/FB02_respool_range_plan.json`.

## Gate decision

**Advance to the actual-ray pilot.** Do not download the 333.8 MiB rectangle. First derive the real benchmark pairs from the selected mesh and reduce the plan to touched bricks.
