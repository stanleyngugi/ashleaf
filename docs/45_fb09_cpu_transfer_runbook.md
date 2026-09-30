# FB09 — CPU fiber-transfer acquisition and scoring runbook

Status: **written before the FB09 field outcome; completed and replayable**. FB09 is a separately sourced, constructed intra-fiber `dw=0` applicability stress test, not human pairwise winding ground truth, a new signed-positive validation, or an official fitter test. Its [protocol and result](39_fb09_fiber_transfer_protocol.md) preserve the unchanged FB08 gate and thresholds. All raw fiber, normal, and grad-magnitude bytes, plus derived row artifacts, belong in ignored `data/` and `artifacts/`.

Run from repository root in PowerShell. The source server may be slow; the builder saves an ignored checkpoint after each deterministic ranked batch and verifies the index hash on resume. A source-index change is a stop condition, not permission to silently change the population. Regenerate range plans from the final strict manifest, even though the first provisional and strict manifests proved byte-identical in this local replay. The plan/download/score scripts hash-link their inputs and will reject a mismatched final manifest.

```powershell
$env:PYTHONPATH='src'
python scripts/fetch_framebridge_metadata.py --include-normal
python scripts/build_fb09_eval_fiber_pairs.py --fibers 40 --pairs-per-fiber 10 --workers 4 --batch-size 8 --output artifacts/framebridge/FB09_eval_fiber_pairs.json
```

After the builder reports **40 explicitly tagged sources**, check the selected filenames, SHA-256 hashes, source-index hash, 400 candidate IDs, coordinate mapping, and any screened skips in the ignored manifest. No normal or E1 field outcome has been consulted for this selection. The `matched_dz_lt1_length_10_to_50` count is descriptive only; it does not influence selection. If the checkpoint's index hash differs from the current server index, stop and investigate instead of overwriting the manifest.

Plan exact normal endpoint bytes for both paired channels:

```powershell
python scripts/plan_normal_endpoint_ranges.py --candidates artifacts/framebridge/FB09_eval_fiber_pairs.json --meta data/PHercParis4/lasagna_inputs/normal_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/normal_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/normal_respool_g4_table.npy --channel 0 --output artifacts/framebridge/FB09_normal_ch0_plan.json
python scripts/plan_normal_endpoint_ranges.py --candidates artifacts/framebridge/FB09_eval_fiber_pairs.json --meta data/PHercParis4/lasagna_inputs/normal_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/normal_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/normal_respool_g4_table.npy --channel 1 --output artifacts/framebridge/FB09_normal_ch1_plan.json
python scripts/fetch_respool_ranges.py --plan artifacts/framebridge/FB09_normal_ch0_plan.json --output-dir data/PHercParis4/lasagna_inputs/FB09_normal_ch0_ranges --resume
python scripts/fetch_respool_ranges.py --plan artifacts/framebridge/FB09_normal_ch1_plan.json --output-dir data/PHercParis4/lasagna_inputs/FB09_normal_ch1_ranges --resume
```

Plan the frozen E1 seven-ray grad-magnitude bytes and fetch them:

```powershell
python scripts/plan_mixed_candidate_ranges.py --candidates artifacts/framebridge/FB09_eval_fiber_pairs.json --meta data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_table.npy --channel-url https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/lasagna_inputs/las_008_grad_mag.ome.zarr.respool_g4/channel_0.u8 --output artifacts/framebridge/FB09_grad_ray_plan.json
python scripts/fetch_respool_ranges.py --plan artifacts/framebridge/FB09_grad_ray_plan.json --output-dir data/PHercParis4/lasagna_inputs/FB09_grad_ray_ranges --resume
```

The range fetcher requires HTTP 206 and correct `Content-Range`, validates byte lengths and hashes, and post-write re-hashes every file. A partial old range directory can contain extra files from an invalidated plan; only files named in a manifest linked to the **new** plan may be used. `--resume` reuses same-named complete-size files but the final sampler verifies the download-manifest/plan link. If the server fails, retry the exact same plan; never fall back to full-channel downloads by accident.

Sample normals and score the **unchanged** FB08 gate:

```powershell
python scripts/sample_fb09_fiber_normals.py --candidates artifacts/framebridge/FB09_eval_fiber_pairs.json --meta data/PHercParis4/lasagna_inputs/normal_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/normal_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/normal_respool_g4_table.npy --plan-0 artifacts/framebridge/FB09_normal_ch0_plan.json --plan-1 artifacts/framebridge/FB09_normal_ch1_plan.json --download-0 data/PHercParis4/lasagna_inputs/FB09_normal_ch0_ranges/download_manifest.json --download-1 data/PHercParis4/lasagna_inputs/FB09_normal_ch1_ranges/download_manifest.json --output artifacts/framebridge/FB09_fiber_normals.json
python scripts/run_fb09_fiber_transfer.py --freeze protocols/FB08_mixed_constraint_gate_freeze.json --candidates artifacts/framebridge/FB09_eval_fiber_pairs.json --normal artifacts/framebridge/FB09_fiber_normals.json --ray-plan artifacts/framebridge/FB09_grad_ray_plan.json --download-manifest data/PHercParis4/lasagna_inputs/FB09_grad_ray_ranges/download_manifest.json --meta data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_table.npy --umbilicus data/PHercParis4/umbilicus.json --output artifacts/framebridge/FB09_fiber_transfer.json
```

Report all 400 pairs and the predeclared matched window separately: normal availability, E1 nonzero proposals, confidence-only proposals, normal-only proposals, frozen numeric gate proposals, affected fiber count, and example IDs. If the gate emits a nonzero proposal on an intra-fiber pair, inspect the trace and field; a continuous fiber is a constructed zero cue, not infallible human winding truth. If it emits none, report the denominator and source-selection bounds—never claim zero production false-accept risk. Keep the registration latch off and do not export constraints from this stress test.
