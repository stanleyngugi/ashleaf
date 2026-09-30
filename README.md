# FrameBridge: auditable winding-evidence QA for virtual unwrapping

FrameBridge is a coordinate-safe, sparse-support and applicability QA layer for winding evidence used in virtual unwrapping. It helps identify unsupported or inapplicable constraints before they are trusted by downstream tools.

This public release candidate demonstrates a bounded real-data QA tradeoff, not a geometry win. On the frozen Paris 4 FB08 evaluation, the gate retained 190/207 held-out relative human-annotation proposals exactly (91.79%) at 19.73% candidate coverage. On the separately selected buffered same-winding population it emitted 0/1,742 false nonzero proposals; confidence-only E1 emitted 397/1,742. In the matched window, the gate was 123/130 exact and 0/646 false nonzero; confidence-only was 143/151 exact and 150/646 false nonzero. The gate retained less coverage, and 17 accepted relative proposals had wrong wrap magnitude.

Transfer and integration limits are material. FB09 uses continuity-derived constructed zero cues, not human pair labels. FB14 did not beat equal-coverage confidence on two dependent absolute-label collections. FB16 graph downweighting did not beat its unchanged baseline. FB25 is incomplete (2/8 valid outcomes); the valid seed-17 FrameBridge treatment loses to patch-only on the frozen primary metric. No improved fitted geometry, production benefit, blind review completion, or increased reading probability is claimed. Numeric export remains disabled.

## Try the CPU metadata demo

Requires Python 3.10+, NumPy, and internet access to the public Paris 4 metadata endpoints. From the repository root, run:

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install numpy
    .\.venv\Scripts\python.exe -m pip install -e .
    .\.venv\Scripts\python.exe scripts/fetch_framebridge_metadata.py
    .\.venv\Scripts\python.exe scripts/plan_framebridge_ranges.py --meta data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_meta.json --coords data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_brick_coords.npy --table data/PHercParis4/lasagna_inputs/grad_mag_respool_g4_table.npy --mesh-meta data/PHercParis4/benchmark_meshes/20231022170901-on-20260411134726-2.4um.tifxyz/meta.json --channel-url https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/lasagna_inputs/las_008_grad_mag.ome.zarr.respool_g4/channel_0.u8 --output artifacts/framebridge/public_demo_plan.json

The planner verifies the sparse index/table inverse and produces 10,683 occupied bricks, 11,520 logical bricks, a 350,060,544-byte field plan, and 717 HTTP ranges. It does not download the planned CT/field payload, inspect mesh TIFF coordinates, establish physical registration, score winding, or generate an unwrap. See [demo details](docs/32_framebridge_public_demo.md), the [visual result](submissions/2026-09_progress_prize/demo_result.html), and the [reproduction receipt](submissions/2026-09_progress_prize/demo_receipt.md).

## Review the submission evidence

- [Form-ready statement](submissions/2026-09_progress_prize/submission_statement.md)
- [Claim ledger and limits](submissions/2026-09_progress_prize/claim_ledger.md)
- [Reviewer quickstart](submissions/2026-09_progress_prize/REVIEWER_README.md)
- [FB08 result](reports/2026-09-24_framebridge_fb08.md) and [frozen holdout protocol](docs/38_fb08_frozen_gate_holdout.md)
- [FB09 constructed-cue transfer](reports/2026-09-24_framebridge_fb09.md)
- [FB15 magnitude-review signal](reports/2026-09-24_framebridge_fb15.md)
- [FB14 transfer negative](reports/2026-09-24_framebridge_fb14.md) and [FB16 graph negative](reports/2026-09-24_framebridge_fb16.md)
- [FB25 seed-17 negative result](reports/2026-09-30_fb25_framebridge_seed17_score.md), [frozen protocol](protocols/FB25_fitter_ab_freeze.json), and [concise current status](PROJECT_STATE.md)
- [Official Progress Prize rules](https://scrollprize.org/prizes#progress-prizes)

Public challenge annotations and CT/field payloads are not bundled. Exact acquisition and full scientific reproduction requirements are documented in the linked runbooks. Constructed +1 labels, human annotations, continuity-derived zero cues, and model-field evidence are kept distinct. See [MIT license](LICENSE).
