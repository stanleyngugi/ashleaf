# Research Bibliography and Transfer Ideas

This is a living bibliography. Each item has a proposed transfer test rather than being treated as a promise of improvement.

## Official ecosystem

- [Open Prizes](https://scrollprize.org/prizes) — authoritative requirements and monthly prize criteria.
- [Winding Constraints](https://scrollprize.org/open_problems/winding_annotations) — authoritative definition of same-, relative-, and absolute-winding evidence.
- [`villa`](https://github.com/ScrollPrize/villa) — current official integration point for VC3D, Lasagna, spiral fitting, and ink workflows.
- [Curated datasets](https://scrollprize.org/data_datasets) — current `spiral-input`, `surface-labels`, and `ink-labels` bundles.
- [Community projects](https://github.com/ScrollPrize/villa/blob/main/scrollprize.org/docs/20_community_projects.md) — existing efforts we should benchmark against instead of unknowingly duplicating.

## Graphs, topology, and layered surfaces

- [The Mutex Watershed and its Objective](https://arxiv.org/abs/1904.12654) — deterministic graph partitioning from attractive and repulsive affinities. Transfer test: retain instance labels and evaluate agglomeration quality before any binary surface conversion.
- [LOGISMOS-B](https://pmc.ncbi.nlm.nih.gov/articles/PMC4324764/) — constrained multi-surface graph segmentation with topology and separation constraints. Transfer test: construct a small scroll-coordinate graph with ordered radial layers and compare global optimality/runtime to Viterbi.
- [Automatic segmentation of retinal layers with graph theory and dynamic programming](https://pmc.ncbi.nlm.nih.gov/articles/PMC3408910/) — close analogy for ordered, thin, layered structures. Transfer test: use learned boundary costs plus hard ordering and smoothness constraints.
- [CNN plus graph search for retinal layers](https://doi.org/10.1364/BOE.8.002732) — useful hybrid pattern: neural evidence supplies costs, graph search supplies structural constraints. Transfer test: apply the same separation of roles to scroll surfaces.

## Representation learning

- [DINO](https://arxiv.org/abs/2104.14294) — self-distillation can produce useful dense semantic structure without labels. Transfer test: patch-level nearest-neighbor consistency across nearby scroll slices and across scans, before attempting full segmentation.
- [Swin UNETR self-supervised 3D pretraining](https://arxiv.org/abs/2111.14791) — a direct 3D medical-imaging precedent. Transfer test: masked-volume and rotation/proxy tasks on unlabeled CT, evaluated with frozen-feature probes.

## Current community signals worth monitoring

- [spiralcheck](https://github.com/Nicodol/spiralcheck) — producer-agnostic held-out evaluation for spiral fits; useful model for our own geometry test harness.
- [winding-sync](https://github.com/abundantjoe/winding-sync) — robust integer synchronization of relative winding constraints; a strong comparison point for our graph branch.
- [Herculaneum Scroll Tools](https://github.com/axiosdevs/herculaneum-scroll-tools) — winding annotation, CT-consistency QA, and dual-energy ink candidates.
- [Community project list](https://github.com/ScrollPrize/villa/blob/main/scrollprize.org/docs/20_community_projects.md) — includes GPU meshing, scroll-specific augmentations, low-memory rendering, and TIFXYZ QA.

## Research caution

Several methods are mathematically attractive but may be mismatched to the official deliverable. For example, a topologically elegant surface can still be spatially wrong, and a segmentation improvement can be irrelevant if its output cannot be flattened, inspected, or integrated into the official formats. Every paper-inspired idea must therefore pass an interface test and a real-data test.

