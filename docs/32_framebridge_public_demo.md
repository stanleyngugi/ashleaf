# FrameBridge Public-Data Demo

Date: 2026-09-23

Status: release quickstart; CPU only; no CT payload or mesh-coordinate TIFF download

This demo turns the FrameBridge coordinate and sparse-I/O contract into a check that a fresh clone can run. It fetches hash-pinned public Paris 4 metadata, verifies the `respool` index/table inverse, converts a verified mesh bounding box from 2.4 µm mesh voxels to the group-4 field grid, and emits an exact byte-range plan. It does **not** claim physical registration, nonzero voxel support, E1 accuracy, or production constraint export.

## Requirements and cost

- Python 3.10+ and `numpy`; the optional `benchmark` installation also supplies the dependencies for later tests.
- Internet access to the public Paris 4 metadata endpoints.
- Approximately 4.5 MiB of index downloads, plus tiny JSON files. The planned 333.8 MiB one-mesh CT payload is **not downloaded** by these commands.
- CPU only; on this Windows machine, metadata fetch and range planning completed in under a minute. Network time varies.

## Native Windows PowerShell

From the repository root:

```powershell
python -m venv .venv-win
.\.venv-win\Scripts\python.exe -m pip install -e ".[benchmark]"
.\.venv-win\Scripts\python.exe scripts/fetch_framebridge_metadata.py
.\.venv-win\Scripts\python.exe scripts/plan_framebridge_ranges.py `
  --meta data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_meta.json `
  --coords data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_brick_coords.npy `
  --table data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_table.npy `
  --mesh-meta data/PHercParis4/benchmark_meshes/20231022170901-on-20260411134726-2.4um.tifxyz/meta.json `
  --channel-url https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/lasagna_inputs/las_008_grad_mag.ome.zarr.respool_g4/channel_0.u8 `
  --output artifacts/framebridge/public_demo_plan.json
```

If a Python environment with `numpy` and this package already exists, use `python` for the commands without creating `.venv-win`. The pre-existing `.venv` in the project owner's workspace is WSL-oriented and does not run natively in PowerShell.

## Unix or WSL shell

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[benchmark]'
.venv/bin/python scripts/fetch_framebridge_metadata.py
.venv/bin/python scripts/plan_framebridge_ranges.py \
  --meta data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_meta.json \
  --coords data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_brick_coords.npy \
  --table data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_table.npy \
  --mesh-meta data/PHercParis4/benchmark_meshes/20231022170901-on-20260411134726-2.4um.tifxyz/meta.json \
  --channel-url https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/lasagna_inputs/las_008_grad_mag.ome.zarr.respool_g4/channel_0.u8 \
  --output artifacts/framebridge/public_demo_plan.json
```

## Expected result

The metadata fetch reports `verified` or `downloaded` for each file. Both statuses mean its SHA-256 matched the value in `scripts/fetch_framebridge_metadata.py`. The planner should print:

```json
{
  "meshes": 1,
  "occupied_bricks": 10683,
  "logical_bricks": 11520,
  "payload_bytes": 350060544,
  "range_count": 717,
  "output": "artifacts/framebridge/public_demo_plan.json"
}
```

Windows prints backslashes in the output path. The generated ignored JSON records source hashes, `table_coords_exact_inverse: true`, the 2.4→9.6→38.4 µm coordinate contract, one-mesh region, and 717 inclusive HTTP ranges. A failure in the index geometry or inverse mapping raises an error instead of quietly producing a plan.

The script plans conservatively from the public mesh `meta.json` bounding box; no mesh TIFF coordinates or CT bricks are read. The exact seven-ray 19,999/19,999 support measurement in FB03 requires those larger inputs and is a separately recorded experiment, **not** reproduced by this quickstart.

## Compact evidence integrity check

After installation, run:

```powershell
.\.venv-win\Scripts\python.exe scripts/check_framebridge_release.py --fb06 experiments/results/framebridge_fb06_summary.json --fb07 experiments/results/framebridge_fb07_loso.json
```

On Unix, replace the Python executable with `.venv/bin/python`. The checker recomputes FB06 exact hits/MAE from the tracked prediction histograms and FB07 aggregates from the tracked fold table. It explicitly reports the 100% constant-`+1` label baseline. It does **not** recompute raw E1 predictions from CT data.

## Reproducing the full research pipeline

The full mesh-pair builders depend on the external `constraint-gauge` repository at commit `a72c4235862be12ae975402e7ec239713fd2b216`. This quickstart does not need it. For the raw research runners, clone it into the expected ignored location and verify the exact commit before running:

```bash
git clone https://github.com/pscamillo/constraint-gauge.git data/external/constraint-gauge
git -C data/external/constraint-gauge checkout a72c4235862be12ae975402e7ec239713fd2b216
git -C data/external/constraint-gauge rev-parse HEAD
```

The full FB05–FB07 E1 evaluation also needs public mesh TIFFs, a sparse CT byte-range payload, and the corresponding ignored pair caches. Those inputs are not bundled here. The [FB02](../reports/2026-09-22_framebridge_fb02.md), [FB03](../reports/2026-09-22_framebridge_fb03.md), [FB06](../reports/2026-09-22_framebridge_fb06.md), and [FB07](../reports/2026-09-22_framebridge_fb07.md) reports record the scientific procedure and known limitations. This is presently a validation/research toolkit, not a production PointCollections exporter or spiral-fitting improvement.
