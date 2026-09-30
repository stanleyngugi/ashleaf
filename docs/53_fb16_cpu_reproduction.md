# FB16 CPU reproduction — fixed graph, SDT review weights, and oracle bounds

Status: retrospective research replay on existing public Paris 4 inputs. This is not the official spiral fitter and needs no GPU, Colab, or new field download. First reproduce or retain the ignored FB08 and FB15 artifacts using [FB08](40_fb08_cpu_reproduction.md) and [FB15](50_fb15_cpu_reproduction.md). The [FB16 protocol](52_fb16_sdt_soft_graph_protocol.md) fixes the 0.25 multiplier, three matched arms plus baseline, and the claims boundary. The [result report](../reports/2026-09-24_framebridge_fb16.md) is the interpretation source of truth.

Run from the repository root in PowerShell with the project Python dependencies:

```powershell
$env:PYTHONPATH='src'
python scripts/evaluate_fb16_sdt_soft_graph.py --fb08-freeze protocols/FB08_mixed_constraint_gate_freeze.json --fb15-freeze protocols/FB15_sdt_crest_v1_freeze.json --protocol-freeze protocols/FB16_sdt_soft_graph_freeze.json --candidates artifacts/framebridge/mixed_candidates.json --holdout-e1 artifacts/framebridge/FB08_holdout_e1.json --normals artifacts/framebridge/FB08_normal_alignment.json --sdt-holdout artifacts/framebridge/FB15_retrospective_FB08_holdout_gate.json --relative-annotations data/PHercParis4/relative_windings.json --output artifacts/framebridge/FB16_sdt_soft_graph.json
```

The scorer rejects a changed source-code or input hash, rechecks the original FB08 gate and the FB15 crest freeze, verifies that the 207 SDT rows are *exactly* the original gate emits, and keeps the graph identical in all four arms. Expected baseline: 1,045 nonzero E1 edges, 65 collections, 5,117 comparable point pairs, 2,222 exact, absolute error sum 4,604. Expected SDT ×0.25 treatment: 34 downweighted edges, 2,213 exact, error sum 4,602. Matched low-confidence and hash controls score 2,210 exact each, with error sums 4,651 and 4,675. Output SHA-256 should be `664b028016e27a20be04f133764ecf27b4c2ff1f0f87068830510918f4ee4d17` on byte-identical inputs and current JSON serialization.

The following are **post-hoc explanations**, not arms in the fixed FB16 test:

```powershell
python scripts/analyze_fb16_graph_topology.py --candidates artifacts/framebridge/mixed_candidates.json --holdout-e1 artifacts/framebridge/FB08_holdout_e1.json --sdt-holdout artifacts/framebridge/FB15_retrospective_FB08_holdout_gate.json --fb16-result artifacts/framebridge/FB16_sdt_soft_graph.json --output artifacts/framebridge/FB16_graph_topology.json
python scripts/analyze_fb16_oracle_repair.py --candidates artifacts/framebridge/mixed_candidates.json --holdout-e1 artifacts/framebridge/FB08_holdout_e1.json --sdt-holdout artifacts/framebridge/FB15_retrospective_FB08_holdout_gate.json --fb16-result artifacts/framebridge/FB16_sdt_soft_graph.json --relative-annotations data/PHercParis4/relative_windings.json --output artifacts/framebridge/FB16_oracle_repair.json
python scripts/export_fb15_review_queue.py --fb15-freeze protocols/FB15_sdt_crest_v1_freeze.json --retrospective-holdout artifacts/framebridge/FB15_retrospective_FB08_holdout_gate.json --output artifacts/framebridge/FB15_research_review_queue.json
python scripts/check_fb16_summary.py --fixed-graph artifacts/framebridge/FB16_sdt_soft_graph.json --topology artifacts/framebridge/FB16_graph_topology.json --oracle artifacts/framebridge/FB16_oracle_repair.json --review-queue artifacts/framebridge/FB15_research_review_queue.json
python -m unittest discover -s tests -q
git diff --check
```

Expected topology: 34/34 flagged edges lie in cycles; baseline rounded assignments match E1 on all 34, including all ten wrong flagged E1 values. Expected oracle: replacing only those ten wrong labels with known human truth gives 2,232 exact and error 4,538. This oracle is deliberately **not implementable from the SDT cue**, which only says a magnitude may be wrong and itself has false reviews. Do not compare oracle scores to an automatic method as if they were deployable. The truth-blind queue has 34 review rows—32 magnitude disagreements and two zero-crest cases—with no human truth/exactness fields and no export permission. The current suite has **107 tests**. Raw annotations and generated detailed results stay ignored under `data/` and `artifacts/`; do not publish them without a separate license/provenance review.

The compact tracked `experiments/results/framebridge_fb16_summary.json` can be checked without ignored data using `python scripts/check_fb16_summary.py`. Supplying the optional artifact paths above verifies their hashes and every headline count against the tracked summary.
