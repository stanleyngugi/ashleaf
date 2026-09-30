# FB15 CPU reproduction — frozen surface crest cue

Status: **research replay, CPU only**. This runbook reproduces [the FB15 report](../reports/2026-09-24_framebridge_fb15.md) from public Paris 4 sparse bytes and the prior FB08/FB14 artifacts. It does not fit a spiral, publish results, or enable numeric export. The method and candidate manifest were locally frozen before validation SDT acquisition; no external preregistration is claimed. Raw annotations, profiles, index arrays, and range payloads remain ignored; do not commit them.

Use a Python environment with project dependencies, NumPy, and SciPy. Run from the repository root in PowerShell; set `$env:PYTHONPATH='src'`. On Unix, use `PYTHONPATH=src` for the equivalent commands. First reproduce [FB08](40_fb08_cpu_reproduction.md) and [FB14](48_fb14_cpu_reproduction.md), or place their pinned ignored artifacts at the paths below. The **48-pair pilot artifacts** are also required to regenerate the candidate manifest byte-for-byte. For a result-only replay, use the locally retained `artifacts/framebridge/FB15_validation_candidates.json` whose SHA-256 must match the tracked freeze; do not replace it with a convenient alternative population.

## 1. Pinned SDT index and candidate provenance

```powershell
$env:PYTHONPATH='src'
python scripts/fetch_fb15_sdt_index.py
```

The index fetch verifies exact HTTP 206 ranges and the pinned SHA-256 of 657-byte metadata, 12,810,572-byte coordinates, and 19,464,320-byte table. The candidate builder below must yield 300 nonpilot relative-development pairs from 120 collections plus 90 already-seen FB14 stress pairs. It excludes all 41 collections represented in the 48-pair pilot. The primary candidate manifest must hash to `ff82e0ba2aa742dc9fe3670e0473e85309c70af99827e041fdd7a727b1ea74cc`; the tracked `protocols/FB15_sdt_crest_v1_freeze.json` enforces it. If it differs, stop and audit the source artifacts; do not edit the freeze.

The pilot itself was method development, selected by `scripts/probe_fb15_development_profiles.py` on E1-correct/wrong strata. Its exact sparse gradient acquisition is inherited from FB08. To recreate the pinned pilot-profile manifest before building validation candidates, run:

```powershell
python scripts/probe_fb15_development_profiles.py --candidates artifacts/framebridge/mixed_candidates.json --development-e1 artifacts/framebridge/FB08_development_e1.json --meta data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_table.npy --download-manifest data/PHercParis4/lasagna_inputs/mixed_candidate_grad_mag_ranges/download_manifest.json --output artifacts/framebridge/FB15_development_profiles.json
python scripts/plan_fb15_sdt_ranges.py --development-profiles artifacts/framebridge/FB15_development_profiles.json --candidates artifacts/framebridge/mixed_candidates.json --meta data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/meta.json --coords data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/brick_coords.npy --table data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/table.npy --output artifacts/framebridge/FB15_sdt_ray_plan.json
python scripts/fetch_respool_ranges.py --plan artifacts/framebridge/FB15_sdt_ray_plan.json --output-dir data/PHercParis4/lasagna_inputs/FB15_sdt_pilot_ranges --resume
python scripts/probe_fb15_sdt_profiles.py --development-profiles artifacts/framebridge/FB15_development_profiles.json --candidates artifacts/framebridge/mixed_candidates.json --plan artifacts/framebridge/FB15_sdt_ray_plan.json --meta data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/meta.json --coords data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/brick_coords.npy --table data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/table.npy --download-manifest data/PHercParis4/lasagna_inputs/FB15_sdt_pilot_ranges/download_manifest.json --output artifacts/framebridge/FB15_sdt_development_profiles.json
python scripts/analyze_fb15_sdt_crossings.py --sdt-profiles artifacts/framebridge/FB15_sdt_development_profiles.json --output artifacts/framebridge/FB15_sdt_crest_development.json
```

The expected 48-pair pilot uses 115 occupied rows and 6,193,152 sparse SDT bytes. `FB15_development_profiles.json` must hash to `9ef992beb5779180f4c30c51953013bc938ad1d38bf0573254eb4e99a0088693`; the selected crest-pilot output must hash to `7b4318912d008e51278c87dde7ff7a7d8713d33c6691cfbf2128171203cd8923`. The source report discloses its selection bias. Repeating the pilot is optional for checking the fixed validation result if the pinned pilot-profile manifest is already available.

```powershell
python scripts/build_fb15_validation_candidates.py --fb08-candidates artifacts/framebridge/mixed_candidates.json --fb15-pilot-profiles artifacts/framebridge/FB15_development_profiles.json --fb14-candidates artifacts/framebridge/FB14_absolute_pairs.json --output artifacts/framebridge/FB15_validation_candidates.json
```

## 2. Plan and fetch only the needed SDT rows

```powershell
python scripts/plan_fb15_validation_sdt_ranges.py --freeze protocols/FB15_sdt_crest_v1_freeze.json --validation-candidates artifacts/framebridge/FB15_validation_candidates.json --meta data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/meta.json --coords data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/brick_coords.npy --table data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/table.npy --output artifacts/framebridge/FB15_validation_sdt_plan.json
python scripts/fetch_respool_ranges.py --plan artifacts/framebridge/FB15_validation_sdt_plan.json --output-dir data/PHercParis4/lasagna_inputs/FB15_validation_sdt_ranges --resume
```

Expected: 390 pairs with seven valid rays each, 548 occupied rows, 220 coalesced HTTP ranges, **39,452,672 bytes** (~37.6 MiB) rather than the full ~35 GB channel. The fetcher verifies HTTP 206, `Content-Range`, lengths, and per-file SHA-256. `--resume` is only for the **same plan**; the scorer verifies the final plan hash and reads every range hash again.

## 3. Score the unchanged method and collection uncertainty

```powershell
python scripts/evaluate_fb15_sdt_crest.py --freeze protocols/FB15_sdt_crest_v1_freeze.json --validation-candidates artifacts/framebridge/FB15_validation_candidates.json --sdt-plan artifacts/framebridge/FB15_validation_sdt_plan.json --sdt-download data/PHercParis4/lasagna_inputs/FB15_validation_sdt_ranges/download_manifest.json --sdt-meta data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/meta.json --sdt-coords data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/brick_coords.npy --sdt-table data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/table.npy --fb08-development-e1 artifacts/framebridge/FB08_development_e1.json --fb08-normals artifacts/framebridge/FB08_normal_alignment.json --fb14-result artifacts/framebridge/FB14_absolute_transfer.json --output artifacts/framebridge/FB15_sdt_crest_validation.json
python scripts/bootstrap_fb15_collections.py --result artifacts/framebridge/FB15_sdt_crest_validation.json --output artifacts/framebridge/FB15_cluster_bootstrap.json
```

Expected primary-arm counts: E1 signed 229/300; SDT magnitude 267/300, SDT with E1 sign 266/300; disagreement flags 67/71 wrong E1 magnitudes and reviews 24/229 correct ones; E1/SDT agreement retains 205/209 exact signed. Original FB08 gate 72/74, gate plus agreement 64/64. Expected stress-arm counts: E1 69/90, SDT 77/90, original gate 9/13, gate plus agreement 7/7. The 5,000-replicate, seed-20260924 collection bootstrap estimates within-source uncertainty; it does not establish external transfer. Result SHA-256 values are pinned in the report.

## 4. Retrospective original-holdout-gate QA

This step was decided **after** the primary and stress results were inspected. It asks whether the fixed cue would have helped the original FB08 gate, not whether it passed an untouched holdout. Preserve that status in any presentation.

```powershell
python scripts/build_fb15_retrospective_holdout_gate.py --fb08-freeze protocols/FB08_mixed_constraint_gate_freeze.json --candidates artifacts/framebridge/mixed_candidates.json --holdout-e1 artifacts/framebridge/FB08_holdout_e1.json --normals artifacts/framebridge/FB08_normal_alignment.json --output artifacts/framebridge/FB15_FB08_holdout_gate_candidates.json
python scripts/plan_fb15_holdout_sdt_ranges.py --fb15-freeze protocols/FB15_sdt_crest_v1_freeze.json --holdout-gate-candidates artifacts/framebridge/FB15_FB08_holdout_gate_candidates.json --meta data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/meta.json --coords data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/brick_coords.npy --table data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/table.npy --output artifacts/framebridge/FB15_holdout_gate_sdt_plan.json
python scripts/fetch_respool_ranges.py --plan artifacts/framebridge/FB15_holdout_gate_sdt_plan.json --output-dir data/PHercParis4/lasagna_inputs/FB15_holdout_gate_sdt_ranges --resume
python scripts/evaluate_fb15_retrospective_holdout.py --freeze protocols/FB15_sdt_crest_v1_freeze.json --candidates artifacts/framebridge/FB15_FB08_holdout_gate_candidates.json --plan artifacts/framebridge/FB15_holdout_gate_sdt_plan.json --download data/PHercParis4/lasagna_inputs/FB15_holdout_gate_sdt_ranges/download_manifest.json --meta data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/meta.json --coords data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/brick_coords.npy --table data/PHercParis4/lasagna_inputs/surf_sdt_g1_index/table.npy --holdout-e1 artifacts/framebridge/FB08_holdout_e1.json --output artifacts/framebridge/FB15_retrospective_FB08_holdout_gate.json
```

Expected: 207 original gate emits, 51 collections; sparse plan 264 occupied rows, 104 ranges, **17,039,360 bytes**. The gate alone has 190/207 exact; agreement retains 166/173, catches 10/17 original errors and reviews 24/190 correct emits. E1 confidence top 173 *within the same gate* retains 156 exact. Seven wrong gate emits remain after SDT agreement. The ignored result includes their IDs and counts but not redistributed field bytes.

## 5. Verification and boundaries

```powershell
python -m unittest discover -s tests -q
python scripts/check_fb15_summary.py --validation artifacts/framebridge/FB15_sdt_crest_validation.json --bootstrap artifacts/framebridge/FB15_cluster_bootstrap.json --holdout artifacts/framebridge/FB15_retrospective_FB08_holdout_gate.json
git diff --check
```

The current suite has **103 tests**. The tracked compact `experiments/results/framebridge_fb15_summary.json` can also be checked without raw artifacts by running `python scripts/check_fb15_summary.py`; its optional inputs enforce full artifact hashes and counts. The scorer rejects a changed crest-source hash, candidate/index/plan/download mismatch, and source-result mismatches. Sparse sampling re-hashes each acquired byte range. This protects *reproducibility of the calculation*, not CT-to-field physical registration. The `FRAME_REGISTRATION_UNVERIFIED` latch remains false. The opt-in `scroll_lab.sdt_review.decide_sdt_review` API turns the crest count and seven ray counts into reason-coded research review; it cannot authorize numeric export. Do not quietly change crest thresholds or call this an official-fitter improvement; a new rule needs a new protocol and untouched test source.
