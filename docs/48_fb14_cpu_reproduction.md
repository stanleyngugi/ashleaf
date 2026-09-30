# FB14 CPU reproduction — absolute-anchor positive transfer

Status: reproducible CPU public-data research run, with a small verified sparse-field download; it is not the metadata-only quickstart. The official `abs_winding.json` and sparse fields remain ignored and are not redistributed. Use the pinned hashes and exact HTTP byte plans; the scored output is the ignored `artifacts/framebridge/FB14_absolute_transfer.json`. The protocol and fixed selection are in [FB14](47_fb14_absolute_anchor_transfer_protocol.md), and the interpretation is in [the result report](../reports/2026-09-24_framebridge_fb14.md).

The simplest replay from a fresh clone is `python scripts/run_fb14_public_demo.py`. It orchestrates the pinned metadata/annotation fetch, exact sparse range plans and verified downloads, and the unchanged scorer. The expected total download is about **9.7 MiB**, with no full CT or full field array. Use `python scripts/run_fb14_public_demo.py --no-download` to replay from an existing cache; that mode never calls a fetcher and fails if required local inputs are absent. The result is a deliberately transparent *failure case*, not a production example. From the repository root, use a Python environment with NumPy and SciPy. The FB08 parent freeze and the tracked FB14 freeze must be present before constructing candidates.

For step-by-step inspection, set `PYTHONPATH=src` (PowerShell: `$env:PYTHONPATH='src'`) and run `python scripts/fetch_spiral_annotations.py --only-absolute` plus `python scripts/fetch_framebridge_metadata.py --include-normal` before the following commands.

## 1. Freeze-linked candidate population

```text
python scripts/build_fb14_absolute_pairs.py --source data/PHercParis4/abs_winding.json --freeze protocols/FB14_absolute_anchor_transfer_freeze.json --output artifacts/framebridge/FB14_absolute_pairs.json
```

Expected: 90 pairs, collection counts 84/6, true magnitude counts 51/26/9/4, exactly 45 positive and 45 negative labels. The builder fails if the pinned source or geometry-only population changes. Source points are already in the working/L2 xyz frame; dividing them again would be a frame error.

## 2. Exact normal and gradient plans

The compact normal/gradient metadata and index arrays can be acquired with `python scripts/fetch_framebridge_metadata.py --include-normal` if they are not already present. The default fetch intentionally omits normal indexes so the public metadata-only quickstart stays near 4.5 MiB. The three plans are:

```text
python scripts/plan_normal_endpoint_ranges.py --candidates artifacts/framebridge/FB14_absolute_pairs.json --meta data/PHercParis4/lasagna_inputs/normal_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/normal_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/normal_respool_g4_table.npy --channel 0 --output artifacts/framebridge/FB14_normal_ch0_plan.json
python scripts/plan_normal_endpoint_ranges.py --candidates artifacts/framebridge/FB14_absolute_pairs.json --meta data/PHercParis4/lasagna_inputs/normal_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/normal_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/normal_respool_g4_table.npy --channel 1 --output artifacts/framebridge/FB14_normal_ch1_plan.json
python scripts/plan_mixed_candidate_ranges.py --candidates artifacts/framebridge/FB14_absolute_pairs.json --meta data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_table.npy --channel-url https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/lasagna_inputs/las_008_grad_mag.ome.zarr.respool_g4/channel_0.u8 --output artifacts/framebridge/FB14_grad_ray_plan.json
```

Expected output plans: 13 occupied normal rows per channel, 18 occupied gradient rows, five coalesced ranges each, with 425,984 + 425,984 + 589,824 payload bytes. All 90 candidates have seven in-bounds E1 rays. Planning itself does not validate physical registration.

## 3. Verified byte acquisition

```text
python scripts/fetch_respool_ranges.py --plan artifacts/framebridge/FB14_normal_ch0_plan.json --output-dir data/PHercParis4/lasagna_inputs/FB14_normal_ch0_ranges --resume
python scripts/fetch_respool_ranges.py --plan artifacts/framebridge/FB14_normal_ch1_plan.json --output-dir data/PHercParis4/lasagna_inputs/FB14_normal_ch1_ranges --resume
python scripts/fetch_respool_ranges.py --plan artifacts/framebridge/FB14_grad_ray_plan.json --output-dir data/PHercParis4/lasagna_inputs/FB14_grad_ray_ranges --resume
```

The fetcher requires HTTP 206/`Content-Range`, checks byte lengths, hashes each range, and verifies hashes again after writing. `--resume` reuses only complete validated files. Do not commit these bytes.

## 4. Unchanged scorer

```text
python scripts/run_fb14_absolute_transfer.py --freeze protocols/FB14_absolute_anchor_transfer_freeze.json --fb08-freeze protocols/FB08_mixed_constraint_gate_freeze.json --candidates artifacts/framebridge/FB14_absolute_pairs.json --normal-meta data/PHercParis4/lasagna_inputs/normal_respool_g4_meta.json --normal-coords data/PHercParis4/lasagna_inputs/normal_respool_g4_brick_coords.npy --normal-table data/PHercParis4/lasagna_inputs/normal_respool_g4_table.npy --normal-plan-0 artifacts/framebridge/FB14_normal_ch0_plan.json --normal-plan-1 artifacts/framebridge/FB14_normal_ch1_plan.json --normal-download-0 data/PHercParis4/lasagna_inputs/FB14_normal_ch0_ranges/download_manifest.json --normal-download-1 data/PHercParis4/lasagna_inputs/FB14_normal_ch1_ranges/download_manifest.json --grad-meta data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_meta.json --grad-coords data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_brick_coords.npy --grad-table data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_table.npy --grad-plan artifacts/framebridge/FB14_grad_ray_plan.json --grad-download data/PHercParis4/lasagna_inputs/FB14_grad_ray_ranges/download_manifest.json --umbilicus data/PHercParis4/umbilicus.json --output artifacts/framebridge/FB14_absolute_transfer.json
```

The scorer rejects changed freeze, candidate, plan, or download hashes and rechecks the FB08 gate source. Expected: E1 exact 69/90 at full coverage; frozen gate exact 9/13 at 13/90 coverage; equal-coverage E1-confidence ranking also 9/13; four wrong gate emits are one-wrap undercounts. `registration_verified` stays false in every decision. Reproducing this result does not fix its two-cluster dependence or prove the CT registration.
