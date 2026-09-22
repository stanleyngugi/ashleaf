# FrameBridge Coordinate Contract

Status: active specification for experiment E0011. Implemented initially by `scroll_lab.frames`, `scroll_lab.frame_probe`, and `scripts/probe_frame_overlap.py`.

## Purpose

FrameBridge prevents a recurring class of Vesuvius errors: treating coordinates from different volumes, pyramid levels, array orders, or sampling conventions as if they were interchangeable. Its first target is the Paris 4 E1 cross-arm probe, but the contract is deliberately generic enough for point collections, TIFXYZ meshes, OME-Zarr arrays, umbilici, tracks, and fitter inputs.

The contract is not a registration algorithm. It represents a registration that has been established elsewhere, checks that it is mathematically usable, and makes every downstream conversion auditable.

## The failure being prevented

The relevant Paris 4 assets use at least three coordinate granularities:

1. verified GP meshes registered on the 2.4 µm scan;
2. winding annotations expressed on the L2 grid of that scan, 9.6 µm per voxel;
3. an E1 `grad_mag` Zarr group that is sampled at an additional pyramid factor relative to the annotation grid.

The old mesh-arm evaluation passed 2.4 µm mesh indices directly to code expecting the annotation coordinate system. Numerically large mesh coordinates were interpreted at the wrong physical scale and every ray was rejected. The problem cannot be fixed safely by scattering another `/4` through the estimator. The transform, its direction, the array group, the umbilicus frame, and the units of ray offsets must all be explicit.

## Canonical definitions

### Stored coordinate

A stored point is a three-number tuple ordered exactly as the frame’s `axis_order`. Examples:

- VC3D point collections and TIFXYZ coordinate values: usually `xyz`;
- NumPy/Zarr array indices: commonly `zyx`.

Stored coordinates are not assumed to be array indices merely because they are integers.

### Canonical physical coordinate

All frames map to canonical physical `(x, y, z)` in micrometres. Transforming source voxels to target voxels is therefore:

```text
target_voxel = inverse(target_voxel_to_physical) × source_voxel_to_physical × source_voxel
```

This composition is the only transform used by `FrameTransform.between`.

### Origin

`origin_um_xyz` is the canonical physical location of stored coordinate `(0, 0, 0)`. It is ordered `xyz` regardless of the stored `axis_order`.

Zero origin is not a universal truth. It is provisional for FB00 and must be verified against the volume metadata/registration before field sampling.

### Sample semantics

`sample_semantics` is either:

- `voxel_center`; or
- `voxel_corner`.

FrameBridge refuses to transform directly between different semantics. It does not guess a half-voxel shift. A caller must provide a frame/affine that explicitly resolves the convention.

### Bounds

`Bounds3D` stores closed coordinate bounds. Extent is `upper - lower`, a coordinate span rather than a voxel count. A general affine transforms all eight corners; transforming only min and max is incorrect under rotation, shear, or axis reversal.

For evidence that reports only one dimension, FrameBridge supports a one-axis physical interval. It refuses this operation when a general affine couples the requested physical axis to unreported axes. This prevents z-only evidence from silently inventing x/y bounds.

## Frame schema

Minimal axis-aligned example:

```json
{
  "name": "PHercParis4 verified-mesh 2.4um coordinates",
  "axis_order": ["x", "y", "z"],
  "voxel_size_um": [2.4, 2.4, 2.4],
  "origin_um_xyz": [0.0, 0.0, 0.0],
  "sample_semantics": "voxel_center",
  "source": "verified GP meshes registered on the 2.4um Paris 4 volume"
}
```

The `voxel_size_um` list follows the stored `axis_order`. If `axis_order` is `zyx`, the first value is the physical size of one stored z step.

For rotation, shear, or a known registration, include `affine_voxel_to_um_xyz`, a finite invertible 4×4 affine whose last row is `[0, 0, 0, 1]`. The affine is authoritative for transformation. `voxel_size_um` remains required as descriptive/checkable metadata and should match the affine’s intended scale.

Unknown schema fields are rejected. A misspelled or legacy field cannot be silently ignored.

## FB00 manifest schema

The first probe manifest contains:

- named frame definitions;
- artifacts attached to frames;
- either point-collection paths whose bounds will be measured or explicitly declared one-axis support intervals;
- pairwise comparisons with expected overlap controls;
- limitations carried into the result.

The current manifest is [`experiments/manifests/framebridge_paris4_support.json`](../experiments/manifests/framebridge_paris4_support.json).

Point-collection inputs are hashed and counted. Paths resolve under a declared base directory and cannot escape it. Declared intervals and measured point intervals cannot disagree.

## Required control structure

Every real cross-frame probe should contain:

1. an identity or same-frame control;
2. an intentionally wrong transform that reproduces the historical failure mode;
3. the proposed corrected transform;
4. a round-trip numerical check;
5. a support check before any array chunks are read.

FB00 implements items 2 and 3 at the z-support level and the unit tests implement items 1 and 4. Full field support and ray containment remain FB01/FB02 work.

## Current Paris 4 frames

### Annotation frame

```text
order: xyz
voxel size: 9.6 × 9.6 × 9.6 µm
provisional origin: 0,0,0 µm
semantics: voxel center
```

The 9.6 figure comes from `constraint-gauge` GATE0 A25: the coordinates are on L2 of the 2.4 µm rescan. It supersedes the earlier 7.91 µm interpretation.

### Verified-mesh frame

```text
order: xyz
voxel size: 2.4 × 2.4 × 2.4 µm
provisional origin: 0,0,0 µm
semantics: voxel center
```

### Mesh-to-annotation transform under the provisional contract

```text
x_annotation = x_mesh / 4
y_annotation = y_mesh / 4
z_annotation = z_mesh / 4
```

This is a hypothesis about index frames backed by A25 and exact physical scale, not yet proof of scan registration. The origin/affine and volume identity must still be checked.

## Units that must be resolved before E1 adaptation

The frozen E1 implementation contains parameters described as voxels:

- sample spacing: 2;
- maximum ray offset: 6;
- z-band size and margins;
- `LASAGNA_SCALE=4` for the selected array group.

When mesh endpoints are transformed into annotation coordinates, these quantities must remain in the estimator’s development-frame units if fidelity is to be preserved. Converting endpoints but leaving the umbilicus or ray offsets in mesh voxels would create a different estimator.

The adaptation must therefore declare:

| Quantity | Required frame/unit |
|---|---|
| Pair endpoints entering E1 | annotation L2 coordinates |
| Umbilicus interpolation input/output | annotation L2 coordinates unless proven otherwise |
| Ray sample spacing | frozen annotation-coordinate voxels |
| Perpendicular offsets | frozen annotation-coordinate voxels |
| `grad_mag` array indices | selected Zarr group coordinates |
| Decode factor | unchanged frozen E1 encoding contract |
| Radial sign calculation | endpoints and umbilicus in the same frame |

## Validation guarantees currently implemented

- axis order is exactly a permutation of x/y/z;
- voxel sizes are finite and positive;
- origins and matrices are finite;
- affines are 4×4, invertible, and have an affine final row;
- identity, isotropic, anisotropic, permutation, translation, shear, and inverse paths are tested;
- center/corner mismatches fail;
- full bounds transform all corners;
- z-only intervals reject coupled affines;
- manifest paths cannot escape the declared base directory;
- point-collection inputs are hashed and counted;
- controls can pre-register expected overlap and make the command fail if an expectation is violated.

## What this contract does not yet guarantee

- that the two Paris 4 scans share the same physical origin;
- that their axes have no reflection/registration offset;
- that TIFXYZ mesh values refer to the exact volume claimed by filenames;
- that `grad_mag` group `4` has the assumed transform;
- that the umbilicus is expressed in the annotation frame;
- that an overlapping z band also overlaps in x/y;
- that complete multirays, including offsets and margins, lie inside the array;
- that E1 produces a correct winding difference after support is restored.

Those are experimental gates, not conveniences to assume away.

## Commands

Run contract/probe tests:

```bash
PYTHONPATH=src python -m unittest tests.test_frames tests.test_frame_probe -v
```

Run FB00 without reading CT/Zarr chunks:

```bash
PYTHONPATH=src python scripts/probe_frame_overlap.py \
  experiments/manifests/framebridge_paris4_support.json \
  --output artifacts/framebridge/FB00_support_probe.json
```

The generated artifact is intentionally ignored by Git; the dated result report records the interpretation and reproduction command.

Validate the public sparse resident-pool indexes and create a byte-exact
acquisition plan before downloading field data:

```bash
PYTHONPATH=src python scripts/plan_framebridge_ranges.py \
  --meta data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_meta.json \
  --coords data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_brick_coords.npy \
  --table data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_table.npy \
  --mesh-meta data/PHercParis4/benchmark_meshes/20231022170901-on-20260411134726-2.4um.tifxyz/meta.json \
  --channel-url https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/lasagna_inputs/las_008_grad_mag.ome.zarr.respool_g4/channel_0.u8 \
  --output artifacts/framebridge/FB02_respool_range_plan.json
```

`scroll_lab.respool` verifies that `table.npy` and `brick_coords.npy` are exact
inverses before emitting any range. Missing logical bricks are defined by the
official format as all-zero, so a sparse evaluator must synthesize them rather
than downloading bytes that do not exist. Occupied-brick fraction is an I/O
fact, not estimator coverage.

## Change control

Any change to a frame’s resolution, origin, semantics, or affine must:

1. update the manifest and its hash;
2. state the new primary evidence;
3. rerun wrong and corrected controls;
4. rerun annotated-arm parity once E1 adaptation exists;
5. generate a new result artifact rather than overwrite the scientific interpretation silently.

Frame mistakes have already changed major conclusions in this problem more than once. The contract is intentionally stricter than a convenient loader.
