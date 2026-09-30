# FrameBridge FB09 — frozen-gate transfer to official traced fibers

Date: 2026-09-24. Status: **completed CPU transfer check on constructed intra-fiber zero relations**, not human pairwise winding ground truth or official fitter evidence. The selection and comparison were specified before FB09 normal/E1 outcomes in [the protocol](../docs/39_fb09_fiber_transfer_protocol.md); exact acquisition and scoring commands are in [the runbook](../docs/45_fb09_cpu_transfer_runbook.md).

## Result

A SHA-256-ranked scan of the public Paris 4 [`eval_fibers` directory](https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/eval_fibers/) selected the first 40 traces carrying explicit `PHercParis4/20260411134726@L0`, level-0, unit-scale, 2.4 µm coordinate tags and qualifying intratrace pairs. Ten arclength-separated pairs per trace yielded 400 candidate pairs. The source index, selected filenames and raw content hashes, screened skips, and candidate coordinates are recorded in the ignored manifest `artifacts/framebridge/FB09_eval_fiber_pairs.json` (SHA-256 `d30baba84dfd49341d035ae2f36c7652d9d880ab2690877c38cff05a24b471ca`). A strict replay after tightening the scale-factor check reproduced that manifest byte for byte, before any field scoring.

The unchanged FB08 gate withheld every nonzero winding proposal: **0/400 emitted**, including **0/64** in the predeclared `|Δz|<1`, chord-length 10–50 working-voxel window. By contrast, frozen E1 alone answered all 400 and proposed nonzero on **399/400**; confidence ≥0.75 still proposed nonzero on **84/400**. In the matched window, those counts were **63/64** and **14/64**. The two endpoint normals were valid for 398 pairs, and none had the frozen minimum chord–normal alignment of 0.75. The all-pair median minimum absolute dot was 0.064, 90th percentile 0.193. The matched-window median was 0.061 among 63 valid-normal pairs.

This is an independent **candidate-source transfer** of the normal-applicability rejection pattern. It is stronger than repeating the original same-winding annotation source, and it shows why E1 confidence alone is not an applicability detector on along-fiber chords. Its limit is equally important: `dw=0` is **constructed from continuity along a traced fiber**, not a human-verified pairwise winding label. Tracing mistakes, shared scan/model priors, and source selection can matter. Zero observed gate emits here must not be described as zero future risk, better positive-relation accuracy, or a production spiral-fitter gain.

A labeled **post-hoc** geometry control applied the existing radial-fraction ≥0.75 cutoff to the same E1 proposals: it would emit nonzero on **134/400** fiber pairs (18/64 matched), or **31/400** (4/64 matched) with E1 confidence ≥0.75. This control did not set the FB09 gate and was not part of its primary protocol. It shows the normal-alignment rejection is not merely reproduced by that simple radial shortcut on this constructed-negative sample.

## Provenance and cost

The two normal channels used 40,599,552 bytes each in 300 exact coalesced HTTP ranges; grad-magnitude used 51,019,776 bytes in 334 ranges. The downloader required HTTP 206/`Content-Range`, checked lengths and SHA-256, then post-write re-hashed every file. Every candidate had seven in-bounds E1 rays. The scorer verified the FB08 frozen gate source SHA and candidate, normal-feature, ray-plan, and download-manifest hashes. Raw public fiber/field bytes and row-level results remain ignored. The scored artifact is `artifacts/framebridge/FB09_fiber_transfer.json` with SHA-256-linked provenance.

## Decision

Add FB09 to the public evidence for FrameBridge as a **trust layer that rejects inapplicable high-confidence E1 relations across two different zero-cue sources**. Do not elevate it to a winding-assignment or fitter claim. The positive magnitude bottleneck and the negative FB10–FB12 graph integration results remain. Next competitive work should seek fresh signed-positive relations or a controlled official-fitter before/after outcome, while retaining the detailed FB08–FB12 failure analysis as an actionable community tool.
