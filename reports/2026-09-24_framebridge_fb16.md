# FrameBridge FB16 — the SDT cue has review value, but simple graph reweighting is not the bridge

Status: **negative controlled CPU downstream diagnostic; retrospective, not official fitter evidence**. The [protocol](../docs/52_fb16_sdt_soft_graph_protocol.md) and local source/input freeze were written before FB16 scoring, but after the FB08 holdout labels and FB15 SDT outcomes were known. This result must not be presented as a new blind holdout.

## Question and fixed design

FB15 flagged 34 of the 207 original FB08 holdout-gate edges as E1/SDT magnitude disagreements: 10 E1 errors and 24 correct E1 relations. Does that review signal improve a winding assignment when all edges and connectivity remain fixed? FB16 used the existing CPU weighted least-squares integer synchronization diagnostic, with the same 1,045 answered nonzero E1 edges in 65 human-annotated point collections in every arm. Treatment downweighted the 34 flagged gate edges to **0.25×** native E1 confidence. Two controls downweighted the same number of gate edges **within each collection**, choosing either lowest E1 confidence or a deterministic ID hash. The multiplier and arms were frozen before scoring. No edge was removed; all arms had 5,117 comparable node pairs out of 5,811 possible.

| Arm | Downweighted gate edges | Exact / 5,117 comparable pairs | Absolute error sum | MAE | Assignment-change collections |
|---|---:|---:|---:|---:|---:|
| E1 confidence baseline | 0 | **2,222** | 4,604 | 0.89975 | — |
| SDT disagreement ×0.25 | 34 | **2,213** (−9) | 4,602 (−2) | 0.89936 | 2/65 |
| Matched low-E1-confidence ×0.25 | 34 | 2,210 (−12) | 4,651 (+47) | 0.90893 | 3/65 |
| Matched hash null ×0.25 | 34 | 2,210 (−12) | 4,675 (+71) | 0.91362 | 2/65 |

The SDT treatment beats the two matched downweight controls on this already-known source, but **does not beat the unchanged baseline on exact winding assignment**. Its two-unit reduction in total absolute error across 5,117 connected comparisons is negligible. Only collections 93 and 149 changed: collection 93 kept the same exact count and reduced absolute error by 12; collection 149 lost nine exact pairs and added ten absolute-error units. The near-canceling total is not a fitter win. Exact counts and errors are dependent within collections, so do not attach a pairwise binomial interval.

## Why the signal barely moved the solver

A post-hoc graph check found that all 34 flagged edges sit in cycles (none is a bridge), so **lack of alternative paths is not the explanation**. More revealingly, the baseline *rounded* graph assignment already agrees with E1 on all 34 flagged edges—including the ten E1 values known to be wrong from human labels. Lowering an edge's weight cannot reliably move an integer solution when the surrounding graph currently reinforces the same difference. Thus FB15's local error signal is valuable to a reviewer, but a soft 0.25× penalty is usually insufficient to overcome a wrong graph consensus.

A deliberately nonimplementable oracle illustrates the ceiling of this specific review target. Replacing only those ten flagged wrong E1 labels with human truth, while leaving all 1,045 edges and weights present, raises exact connected pairs from 2,222 to **2,232** and lowers total absolute error from 4,604 to **4,538**. Correcting all 17 wrong original-gate edges reaches **2,239** exact and error **4,531**. There are **215** wrong E1 edges among the 1,045 graph inputs overall; correcting *all* of them yields 5,117/5,117, as an implementation sanity check, not a feasible policy. The oracle says the ten caught gate errors are real, but they do not dominate this graph's global error. Neither the oracle nor the SDT flag supplies a production correction rule.

## Strategic interpretation

FB16 closes a tempting shortcut: **do not claim a downstream winding gain by simply downweighting FB15 disagreements in this solver**. It also refines the prize story. FrameBridge is presently strongest as a transparent, sparse-data **evidence review and error-triage layer**. To show a fitter improvement, we need either (a) a way to produce reliable *corrected* signed magnitudes rather than merely disagreement flags, (b) a constrained human/automatic review workflow whose corrected edges are applied where they matter, or (c) an official fitter experiment in which the cues affect a genuinely consequential loss or candidate selection. The current CPU least-squares surrogate may not predict the official fitter's behavior; it is a stop signal for this simple policy, not a verdict on all integrations. GPU/Colab should wait for a fixed official treatment/control design.

The CT/SDT contract remains limited: the public SDT `meta.json` declares a `ct_mask` source in the Paris 4 `s1_ds2` CT package with ratio `[2,2,2]`, and its array shape matches `ceil(CT L2 shape / 2)`. That supports the chosen coordinate scale, but it does **not** reveal the field producer or prove that every crest is a physical sheet crossing. The official [curated spiral-input description](https://github.com/ScrollPrize/villa/blob/main/scrollprize.org/docs/02_data_datasets.md) identifies Paris 4 annotations and volume inputs; it does not document the SDT encoding. We found no basis to relax the `FRAME_REGISTRATION_UNVERIFIED` latch.

As a concrete review-workflow artifact, `scripts/export_fb15_review_queue.py` now exports the 34 original-gate disagreements **without reading or emitting human truth**: 32 nonzero magnitude disagreements and two zero-crest reviews. It whitelists only E1/SDT evidence, sorts by E1 confidence and ID, and marks every row `review` with `numeric_export_permitted=false`. The highest-confidence row proposes E1 −2 at confidence 0.984 while all seven SDT rays count three crests; this is precisely the kind of apparently confident disagreement a human reviewer should inspect. The queue is research-only and ignored, not an automatic correction list or a new validation score.

## Provenance and replay

- Local protocol freeze: `protocols/FB16_sdt_soft_graph_freeze.json`, SHA-256 `9e0191540f12ceb750bae806f0a48cc6e48132237a1db78dd32a1014041e5ab1`; it pins scorer source, seven input hashes, 0.25 multiplier, arms, and claim limits. Not externally timestamped.
- Ignored results: `artifacts/framebridge/FB16_sdt_soft_graph.json`, SHA-256 `664b028016e27a20be04f133764ecf27b4c2ff1f0f87068830510918f4ee4d17`; post-hoc topology `FB16_graph_topology.json`, SHA-256 `1858517231660a7a2afb404c2a175f241fee4b41ccb5fd7694276f6f41cf91fa`; post-hoc oracle `FB16_oracle_repair.json`, SHA-256 `747f998e0436eb36bb91b17911fdf1899db5160445aeace7a571180bade1afa7`.
- Truth-blind queue: `artifacts/framebridge/FB15_research_review_queue.json`, SHA-256 `a2ca212765056064722d455354e8ee389fb73dbfd90d23b7f50a185e3d786846`.
- Tracked no-download reviewer artifact: `experiments/results/framebridge_fb16_summary.json`; `python scripts/check_fb16_summary.py` verifies its freeze/source and, with optional ignored inputs, the full graph, topology, oracle, and truth-blind queue hashes and counts.
- Commands and dependencies: [FB16 CPU reproduction](../docs/53_fb16_cpu_reproduction.md). All work used existing ignored annotation/E1/SDT files; no new CT or GPU bytes were acquired. The test suite passes **107 tests**, including fixed-control selection, cycle/bridge, and truth-blind export checks.
