# Initial Research and Execution Decision

Date: 2026-09-18

## Decision

We will pursue monthly Progress Prize contributions first, with the first release centered on winding evidence, geometry QC, and integration around the official `villa` ecosystem. The old Kaggle surface detector becomes a reference benchmark and a source of controlled algorithm branches, not the main product.

## Why this matches the current competition

The official Progress Prize page explicitly favors early releases, real-data improvements, bug fixes, actionable analysis, and strong documentation. Multiple submissions can be evaluated in a month, and the next listed deadline is September 30, 2026. This means a reliable validator, benchmark, or upstream bug report can be a better first move than a large model that is not yet reproducible.

The official winding-constraint problem asks for constraints that are accurate, confidence-aware, fast, easy to verify, and general. Our proposed Winding Evidence Lab matches every one of those requirements.

## Old project versus current project

| Former project | Current project |
|---|---|
| Kaggle binary 3D surface mask | Full virtual unwrapping plus ink detection |
| Local composite metric dominated decisions | Real scroll geometry, usable meshes, fibers, and readable ink |
| Viterbi/MWS postprocessing around a binary mask | Evidence and constraints feeding global spiral/mesh methods |
| Hard runtime pressure in a notebook | Open-source community integration and reproducibility |
| Long architecture-first effort | Short release loops plus parallel research tracks |

The old work still contributes: pitch and spiral features, topology engineering, GPU benchmarks, metric caution, and failure-analysis habits. The major change is the evaluation target and delivery strategy.

## Immediate technical sequence

1. Finish the contract layer and add official-format adapters.
2. Create synthetic winding fixtures with known integer winding differences and planted contradictions.
3. Read a small public `spiral-input` sample and produce a QC report without fitting a whole scroll.
4. Implement a baseline candidate generator from local tangents/normals/pitch cues.
5. Compare unweighted BFS with confidence-weighted and robust integer synchronization.
6. Benchmark against verified annotations and visual fit quality.
7. Publish the strongest narrow contribution before expanding into expensive GPU training.

## Parallel research sequence after the baseline

- Viterbi as proposal/confidence, not binary mask.
- MWS with instance labels preserved to the interface.
- LOGISMOS-like constrained graph surfaces.
- Self-supervised 3D feature probes for cross-scroll geometry.
- GPU tiled I/O and memory-safe rendering.
- Implicit and physics-inspired surface refinement only after a planted-defect benchmark exists.

## Risks to control immediately

### Data-contract risk

The current public ecosystem has reported stale patch bounding boxes and malformed spacing metadata that can silently drop evidence or request impossible flattening allocations. These become regression fixtures in E0001.

### Leakage risk

The official Grand Prize rules prohibit overlap between training and prediction regions and require public experiment tracking for stochastic trained models. Split generation and provenance must be implemented before serious modeling.

### Shortcut risk

The old model produced nearly identical foreground fractions for all volumes of the same shape. Every new learned experiment will include shape-stratified output statistics and cross-volume similarity tests.

### Integration risk

A mathematically strong method is not useful if it cannot export official formats, flatten, render, or be inspected. Every branch must be tested at its interface boundary.

## Source set

- [Official prizes and Progress Prize criteria](https://scrollprize.org/prizes)
- [Official winding-constraint problem](https://scrollprize.org/open_problems/winding_annotations)
- [Official curated datasets](https://scrollprize.org/data_datasets)
- [Official `villa` monorepo](https://github.com/ScrollPrize/villa)
- [Current community projects](https://github.com/ScrollPrize/villa/blob/main/scrollprize.org/docs/20_community_projects.md)
- [Paris 4 metadata bounding-box issue](https://github.com/ScrollPrize/villa/issues/1272)
- [Paris 4 spacing/flattening issue](https://github.com/ScrollPrize/villa/issues/1379)
- [Held-out spiral-fit evaluation](https://github.com/Nicodol/spiralcheck)
- [Integer winding synchronization](https://github.com/abundantjoe/winding-sync)

