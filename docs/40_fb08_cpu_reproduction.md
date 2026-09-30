# FB08 — CPU reproduction and provenance checklist

This runbook reproduces the **locally frozen** FB08 mixed-constraint experiment described in [the holdout report](38_fb08_frozen_gate_holdout.md). It is deliberately separate from FB09's independent fiber-transfer stress test. No GPU, Colab, dense CT download, or official spiral-fitting run is required. Run from the repository root in PowerShell with Python dependencies from the project setup. The commands create ignored files in `data/` and `artifacts/`; they do not push or publish anything.

The local freeze at [`protocols/FB08_mixed_constraint_gate_freeze.json`](../protocols/FB08_mixed_constraint_gate_freeze.json) was written before holdout E1 was run, but was **not** externally timestamped. Reproducing it does not convert it into a prospective public preregistration. Public server bytes are hash-pinned by the fetchers; the data-server [license](https://dl.ash2txt.org/LICENSE.txt) means the raw annotation and field payloads should remain ignored rather than committed.

## 1. Acquire and verify the public inputs

```powershell
$env:PYTHONPATH='src'
python scripts/fetch_spiral_annotations.py
python scripts/fetch_framebridge_metadata.py --include-normal
```

The first command pins `relative_windings.json` (`a3243511...`), `same_windings.json` (`d9be52c5...`), and the umbilicus. The second pins the group-4 grad-magnitude and paired normal-field indices (`meta.json`, `brick_coords.npy`, `table.npy`) in `data/PHercParis4/lasagna_inputs/`. Stop if a source hash has changed; do not silently replace the freeze's inputs.

## 2. Select label-blind candidates and acquire only their field bricks

```powershell
python scripts/build_mixed_candidate_manifest.py --relative data/PHercParis4/relative_windings.json --same data/PHercParis4/same_windings.json --output artifacts/framebridge/mixed_candidates.json
python scripts/plan_mixed_candidate_ranges.py --candidates artifacts/framebridge/mixed_candidates.json --meta data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_table.npy --channel-url https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/lasagna_inputs/las_008_grad_mag.ome.zarr.respool_g4/channel_0.u8 --output artifacts/framebridge/mixed_all_ray_plan.json
python scripts/fetch_respool_ranges.py --plan artifacts/framebridge/mixed_all_ray_plan.json --output-dir data/PHercParis4/lasagna_inputs/mixed_candidate_grad_mag_ranges --resume
```

Expected: 13,048 candidates, all seven rays in bounds, 1,523 occupied grad-magnitude rows, 526 coalesced ranges, 83,034,112 planned payload bytes. The fetcher requires HTTP 206 and matching `Content-Range`, validates lengths and SHA-256, and re-hashes files after writing. `--resume` is safe for an interrupted acquisition only when rerunning the **same plan**; the final manifest is authoritative for which range files are used.

```powershell
python scripts/plan_normal_endpoint_ranges.py --candidates artifacts/framebridge/mixed_candidates.json --meta data/PHercParis4/lasagna_inputs/normal_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/normal_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/normal_respool_g4_table.npy --channel 0 --output artifacts/framebridge/mixed_normal_ch0_plan.json
python scripts/plan_normal_endpoint_ranges.py --candidates artifacts/framebridge/mixed_candidates.json --meta data/PHercParis4/lasagna_inputs/normal_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/normal_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/normal_respool_g4_table.npy --channel 1 --output artifacts/framebridge/mixed_normal_ch1_plan.json
python scripts/fetch_respool_ranges.py --plan artifacts/framebridge/mixed_normal_ch0_plan.json --output-dir data/PHercParis4/lasagna_inputs/mixed_normal_ch0_ranges --resume
python scripts/fetch_respool_ranges.py --plan artifacts/framebridge/mixed_normal_ch1_plan.json --output-dir data/PHercParis4/lasagna_inputs/mixed_normal_ch1_ranges --resume
python scripts/sample_mixed_normal_alignment.py --candidates artifacts/framebridge/mixed_candidates.json --meta data/PHercParis4/lasagna_inputs/normal_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/normal_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/normal_respool_g4_table.npy --plan-0 artifacts/framebridge/mixed_normal_ch0_plan.json --plan-1 artifacts/framebridge/mixed_normal_ch1_plan.json --download-0 data/PHercParis4/lasagna_inputs/mixed_normal_ch0_ranges/download_manifest.json --download-1 data/PHercParis4/lasagna_inputs/mixed_normal_ch1_ranges/download_manifest.json --output artifacts/framebridge/FB08_normal_alignment.json
```

Each normal channel should require 1,089 occupied rows, 466 coalesced ranges, and 63,963,136 payload bytes. The normal sampler is a nearest-integer endpoint probe, not a claim of dense GPU-fitter parity.

## 3. Regenerate development evidence and the spatial buffer

```powershell
python scripts/run_mixed_candidate_e1.py --candidates artifacts/framebridge/mixed_candidates.json --ray-plan artifacts/framebridge/mixed_all_ray_plan.json --download-manifest data/PHercParis4/lasagna_inputs/mixed_candidate_grad_mag_ranges/download_manifest.json --meta data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_table.npy --umbilicus data/PHercParis4/umbilicus.json --partition development --output artifacts/framebridge/FB08_development_e1.json
python scripts/analyze_mixed_candidate_geometry.py --candidates artifacts/framebridge/mixed_candidates.json --e1 artifacts/framebridge/FB08_development_e1.json --umbilicus data/PHercParis4/umbilicus.json --output artifacts/framebridge/FB08_development_geometry.json
python scripts/benchmark_mixed_radial_baseline.py --geometry artifacts/framebridge/FB08_development_geometry.json --output artifacts/framebridge/FB08_development_geometry_baselines.json
python scripts/analyze_mixed_normal_development.py --geometry artifacts/framebridge/FB08_development_geometry.json --normal artifacts/framebridge/FB08_normal_alignment.json --output artifacts/framebridge/FB08_development_normal_gate_comparison.json
python scripts/plan_fb08_holdout_buffer.py --candidates artifacts/framebridge/mixed_candidates.json --radius 16 --output artifacts/framebridge/FB08_holdout_spatial_buffer.json
```

Expected development primary rule: 491/518 exact relative proposals and zero nonzero emits on 6,492 same-winding candidates. The coordinate-only buffer should retain 1,049 relative and 1,742 same-winding holdout candidates. These outputs must match the tracked freeze's provenance checks before scoring; do not recalculate a more favorable threshold or buffer after inspecting holdout labels.

## 4. Replay the frozen holdout and diagnostic

```powershell
python scripts/run_mixed_candidate_e1.py --candidates artifacts/framebridge/mixed_candidates.json --ray-plan artifacts/framebridge/mixed_all_ray_plan.json --download-manifest data/PHercParis4/lasagna_inputs/mixed_candidate_grad_mag_ranges/download_manifest.json --meta data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_table.npy --umbilicus data/PHercParis4/umbilicus.json --partition holdout --protocol-freeze protocols/FB08_mixed_constraint_gate_freeze.json --output artifacts/framebridge/FB08_holdout_e1.json
python scripts/evaluate_fb08_frozen_gate.py --freeze protocols/FB08_mixed_constraint_gate_freeze.json --candidates artifacts/framebridge/mixed_candidates.json --e1 artifacts/framebridge/FB08_holdout_e1.json --normal artifacts/framebridge/FB08_normal_alignment.json --spatial-buffer artifacts/framebridge/FB08_holdout_spatial_buffer.json --umbilicus data/PHercParis4/umbilicus.json --output artifacts/framebridge/FB08_frozen_gate_holdout.json
python scripts/evaluate_fb08_graph_impact.py --freeze protocols/FB08_mixed_constraint_gate_freeze.json --candidates artifacts/framebridge/mixed_candidates.json --e1 artifacts/framebridge/FB08_holdout_e1.json --normal artifacts/framebridge/FB08_normal_alignment.json --relative-annotations data/PHercParis4/relative_windings.json --output artifacts/framebridge/FB08_posthoc_graph_impact.json
$env:PYTHONPATH='src'; python -m unittest discover -s tests
```

The primary result should be 190/207 exact signed relative proposals at 207/1,049 coverage, with zero nonzero emits among 1,742 buffered same-winding candidates. The **post-hoc** graph diagnostic is not a frozen primary result: it shows that hard filtering reduces connected node-pair coverage to about 5%, so the gate is a source of precise seeds, not a complete fitter. All numerically eligible proposals remain `review` while `registration_verified` is false; this runbook does **not** enable production export.

## Reproduction boundaries

- The two human annotation arms were collected differently. Report them separately and include the predeclared `|Δz|<1`, chord-length 10–50 slice; do not pool them into one class-balanced accuracy metric.
- Collections, not candidate pairs, are the meaningful dependency unit. The holdout is collection-disjoint and the same arm uses an additional coordinate-only development buffer, but neither makes the population representative of automatically generated constraints.
- The frozen file pins local generated-artifact hashes. Text line endings are accepted in the freeze checks where explicitly implemented, but regenerated nested paths or source changes may still require an environment-specific provenance audit. A failed freeze check is a stop signal, not a reason to weaken it.
- The CT anchor check and sparse grad slice screen in the [holdout report](38_fb08_frozen_gate_holdout.md) are additional diagnostics. Neither proves exact registration or dense/sparse estimator parity.
