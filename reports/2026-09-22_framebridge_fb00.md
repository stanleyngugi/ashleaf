# FrameBridge FB00 — Coordinate-Support Control

Date: 2026-09-22
Experiment: E0011 / FB00
Status: **passed for z-support only; field/ray support remains unproven**

## Question

Can an explicit physical-frame comparison both reproduce the historical Paris 4 no-overlap conclusion under the wrong interpretation and recover the overlap predicted by `constraint-gauge` A25 under the corrected 2.4 µm ↔ 9.6 µm interpretation?

## Pre-registered expectations

1. Treating the mesh z indices as if they were already annotation/L2 indices at 9.6 µm must produce no overlap.
2. Treating the mesh z indices in their declared 2.4 µm frame and annotation points in their measured 9.6 µm frame must produce nonempty overlap.

Both expectations were stored in the manifest before running the probe.

## Inputs

### Measured annotation input

- File: `data/PHercParis4/relative_windings.json`
- SHA-256: `a3243511d4eb91387a9b32f4dbff11514b08c3ae36e9b2a2b8222607b4883ac1`
- Points: 2,173
- Native measured bounds:
  - x: `1987.5059814453125–6602.228515625`
  - y: `1690.65380859375–6625.41064453125`
  - z: `6527.57080078125–17252.5546875`
- Frame: xyz, 9.6 µm/voxel, provisional zero origin.

### Declared mesh-band input

- Native z: `29420–73889`
- Frame: xyz, 2.4 µm/voxel, provisional zero origin.
- Evidence source: `constraint-gauge` GATE0 A17/A25.
- Important limitation: the aggregate z interval was transcribed from that benchmark and was not yet recomputed from local mesh TIFFs, because the nine mesh inputs are not present locally.

### Manifest

- File: `experiments/manifests/framebridge_paris4_support.json`
- SHA-256 at run time: `7dcf2497999c6be94abb66cd5629672a69db1c04b53435dc64c94eab58f59afd`

## Command

```bash
PYTHONPATH=src .venv/bin/python scripts/probe_frame_overlap.py \
  experiments/manifests/framebridge_paris4_support.json \
  --output artifacts/framebridge/FB00_support_probe.json
```

Environment:

- Python 3.12.3;
- WSL2 Linux 6.6.87.2;
- x86_64;
- no `nvidia-smi` available or required;
- repository base commit before working-tree changes: `c08db9ff5740e7b90d7a21f2c31e1002129c091d`.

## Result

| Comparison | Mesh interpretation | Mesh z in µm | Annotation z in µm | Overlap |
|---|---:|---:|---:|---:|
| Wrong-frame control | 9.6 µm/voxel | `282432.0–709334.4` | `62664.68–165624.53` | none |
| Corrected frame | 2.4 µm/voxel | `70608.0–177333.6` | `62664.68–165624.53` | `70608.0–165624.53` |

Corrected z-support overlap: **95,016.525 µm**, approximately **95.0 mm**.

Both pre-registered expectations passed. The wrong control reproduces the qualitative historical failure; the corrected physical interpretation restores substantial z overlap.

## Interpretation

### Verified here

- The cached relative-winding file contains 2,173 points and the bounds listed above.
- The frame implementation converts a 2.4 µm mesh coordinate to one quarter as many 9.6 µm annotation voxels.
- Under zero-origin, aligned-axis assumptions, the benchmark’s declared mesh z band overlaps the measured annotation z support by about 95.0 mm.
- The wrong 9.6 µm interpretation produces no z overlap.
- Thirteen new frame/probe tests passed during this run.

### Verified upstream

- `constraint-gauge` A25 identifies the annotation coordinates as the 9.6 µm L2 grid and records the aggregate mesh z band in the 2.4 µm frame.

### Inference

- The historical E1 zero-coverage result is consistent with a coordinate-frame error.

### Not yet verified

- That the mesh and annotation scans share zero origin and aligned axes.
- That `grad_mag` has x/y/z support for any complete mesh pair ray.
- That group `4` and the current `LASAGNA_SCALE` are being interpreted correctly after mesh-to-annotation conversion.
- That the umbilicus coordinates use the same annotation frame.
- That any E1 mesh pair becomes answerable.
- Any E1 independent accuracy result.

## Decision

FB00 passes the first support gate, so E0011 continues. It does **not** pass G2 in full because G2 requires complete field/mesh support, not only aggregate z overlap.

Next actions, in order:

1. Locate and pin actual verified-mesh directories and their registration-bearing names/metadata.
2. Obtain `grad_mag` OME-Zarr metadata only—no chunks—and record axes, group shapes, multiscale transforms, and origin information.
3. Locate/pin `umbilicus.json`, measure its bounds, and establish its frame.
4. Produce full xyz physical bounds for each mesh, the field, annotations, and umbilicus.
5. Count candidate mesh pairs whose full seven-ray envelope fits the field before loading array values.
6. Only after those checks, adapt E1 and prove annotated-arm parity.

## Why this is useful but not yet submission evidence

FB00 converts A25’s arithmetic observation into a strict, tested, machine-readable contract with a negative control. That is necessary groundwork. It is not yet a significant real-data improvement, independent score, or fitter result. Presenting it alone as the final monthly contribution would overstate the evidence.
