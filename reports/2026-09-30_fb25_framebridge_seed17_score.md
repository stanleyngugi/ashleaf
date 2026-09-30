# FB25 FrameBridge seed-17 held-out score — 2026-09-30

**Status: valid, persisted single-seed outcome; negative on the primary mean-sheet-consistency metric.** The frozen fitter and evaluation contract was not changed. This report records the first valid FrameBridge held-out score; it does not establish a general treatment effect or pass the eight-outcome gate.

## Result

The verified FrameBridge seed-17 treatment scored **0.573944679621 mean unseen sheet consistency**, compared with **0.596538651162** for the bound patch-only seed-17 control. The paired difference is **−0.022593971541** (−2.26 percentage points). This is in the wrong direction and fails the frozen requirement for at least +0.03 gain over patch-only for this seed. The within-τ fraction was **0.725132180684** versus **0.693272810731** (+3.19 percentage points); this secondary improvement does not offset failure of the primary metric. Both reports scored the same 130 unseen patches and 58,821 points.

Annotation agreement did not regress on this seed: FrameBridge scored **271/328 = 0.826219512195**, while patch-only scored **262/326 = 0.803680981595**. Both reports cover 2,173 source points, 396 in-window points, and 40 informative/decidable collections. These annotation statistics do not reverse the primary metric loss.

The frozen gate requires FrameBridge gains of at least 0.03 over **both** patch-only and confidence-control, positive gain for each seed, within-τ degradation no greater than 0.01 per seed, and no annotation-agreement regression across the complete four-arm/two-seed matrix. The seed-17 FrameBridge result already violates the patch-only gain requirement. The full matrix is incomplete, so report this as a valid negative treatment result for one seed; do not claim the complete experiment or a general negative conclusion. Conditional replication is not authorized by the frozen gate unless the primary comparison passes.

## Run and provenance

The fit ran with the frozen FrameBridge arm, seed 17, window `[15000,16000]`, 30,000 iterations, and all **2,532/2,532** expected relative PCL loads. Fit operation exit code is 0. Checkpoint SHA-256 is `b593aa6b583143ff9264d0130a7caa9246352a7518ee0e3d255adaba0d0380e2`; run-manifest SHA-256 is `6c25a0f2542e5dfa298675b6be50b48bbb9b8be2a31d6405ce4c365a4c3463a0`; relative-PCL input SHA-256 is `27dab91fb043c38acaabf152fe77e813c8d95409a25bf334a3491ea7ae55b9a7`.

The CPU scorer completed on account 3 host `a867781b0893` from 16:11:43.136 UTC through 16:41:20.004 UTC. Wrapper PID 63228 terminated with **exit status 0**, independently read as `si_status=0`. Both local and Drive operation records report `scored_and_persisted` with the same bytes. The report snapshot has eight files, 1,715,207 bytes, and tree SHA-256 `75dc0df59621b59f9c612e3a603de28dbd7cb7be6912367f414516ed61b77dcd`. Independent checks matched every report file byte-for-byte between local and Drive, recomputed the local and durable snapshot inventories, and validated the report, annotation, assessment-bundle, binding, checkpoint, run-manifest, and mesh-tree hashes.

The report bundle files are:

| File | SHA-256 |
|---|---|
| `report.json` | `3943cce2a6ee0467296e693ae23f6bd2b5fd52452e612b56b31d1cecd8f50f99` |
| `annotations.json` | `cd28b9e30442fffad7a1482eaa35f9d0a15596a7f79851d401e2dee9b39e185c` |
| `assessment_bundle.json` | `7b5ac22ec81b80413a71d44384dce2f40bd3b5e69bfb4e8e1210fc159a0cb2a2` |
| `binding.json` | `2a9c3065eec43f6c13f79a02b629735bcf865b0fe71c29c5153c5acdfe32541d` |

The two bounded stage logs and independent exit verification were separately
copied to
`MyDrive/Ashleaf/FB25/primary/reports/score_framebridge_seed17_20260930_v5_execution_evidence`.
The copy was verified before and after Drive transfer: three files, 3,177 bytes,
tree SHA-256 `027e27701ca470939eb8855dfd2f96c176e2cb3fc3959c5f5d38d43f3ac43267`.
`score_stage_0.log` SHA-256 is
`e85197666e9b675534c24865a2694078f31ef4addfcb20a7ee81a488c7053fad`;
`score_stage_1.log` SHA-256 is
`df3bb874e35058f83ed9d96b5c26e4062fe980b8d1cc0510d24b2455549e59af`.
The execution-verification record binds the wrapper PID, exit code 0, operation
completion timestamp, score/annotation report hashes, and report snapshot tree.

The binding records arm `framebridge`, seed 17, window `[15000,16000]`, checkpoint/run-manifest/mesh-tree hashes above, and `numeric_export_permitted=false`. The report uses variant `plain`, τ=6, unseen minimum distance 2, a clean fit-input hash audit, and no patch-load or fit-input-load errors. Recomputed split, serialized score-input-manifest, fit-tree, held-out-tree, umbilicus, and annotation hashes all match the binding. The scorer commit is `d1b50e2957409a870225fb9f5dcc5e25f7a0f9da`.

The actual serialized score-input-manifest hash is `f3997c3da4637a3b1bb89d0a998f062ee448ba9ecce4ca5cf3484bcded52a4b9`, distinct from the manifest's preexisting declared self-digest. This discrepancy was documented before outcomes and remains bound as the actual byte digest. No frozen source or index hash was modified.

## Interpretation and next work

The treatment improves the within-τ fraction and annotation agreement while reducing the primary mean consistency. The metrics answer different questions; do not select the favorable metric after seeing this result. There is no independent physical registration, human review, production constraint export, or readable unwrapped-surface result. Keep the numeric-export latch closed.

One baseline and one treatment outcome are now valid (**2/8**). Six frozen primary outcomes remain: patch-only seed 29, confidence-control seeds 17 and 29, unfiltered-v3 seeds 17 and 29, and FrameBridge seed 29. Complete the already frozen matrix only when an immediately runnable, disjoint fit queue and available accelerator are verified; do not change seeds, arms, comparisons, or gates. Since the treatment already fails the primary seed-17 requirement, do not start conditional replication. The next useful decision is whether any remaining frozen outcome can be completed within the verified deadline; the full gate cannot be declared from this partial result.

See [PROJECT_STATE](../PROJECT_STATE.md), the [FB25 protocol](../docs/65_fb25_fitter_ab_protocol_2026-09-26.md), the [fitter freeze](../protocols/FB25_fitter_ab_freeze.json), and the [prize packet draft](../submissions/2026-09_progress_prize/submission_statement.md).
