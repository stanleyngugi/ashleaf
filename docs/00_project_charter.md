# Project Charter

## Mission

Help read carbonized Herculaneum scrolls by contributing open, reproducible improvements to virtual unwrapping, surface geometry, and ink detection.

## Near-term objective: monthly prizes

The current competition rewards open-source contributions, real-data improvements, bug fixes, speedups, documentation, and actionable information—not only a final full-scroll reading system. Therefore our first deliverables should be independently useful and easy for the community to run or verify.

The first project is the **Winding Evidence Lab**:

- consume official surface predictions and CT-aligned geometry;
- harvest candidate winding constraints from fibers, normals, surface patches, and flattened evidence;
- score confidence and detect contradictions;
- provide deterministic exports compatible with the official spiral fitter;
- include held-out evaluation and a visual QC report.

## Research tracks

| Track | Near-term output | Longer-term role |
|---|---|---|
| Winding/QC | Constraint harvester, verifier, defect reports | More globally coherent spiral fits |
| Surface geometry | Surface prediction/refinement baselines | Dense scroll-wide surfaces |
| Topology/separation | Viterbi, LOGISMOS-like graphs, MWS variants | Sheet identity and layer separation |
| Ink detection | Data and domain-shift baselines | Generalization to unseen scrolls/scans |
| Representation learning | 3D SSL/DINO-style probes | Reduce annotation dependence |
| GPU systems | Tiled I/O, kernels, inference benchmarks | Larger volumes and faster iteration |
| Exploratory methods | Implicit surfaces, diffusion, GNNs, physics, RL | Breakthrough candidates, only promoted by evidence |

## Decision principles

We will not spend months perfecting a single architecture without checkpoints. Every track has a cheap test, a go/no-go criterion, and a maximum initial compute budget. A negative result is a successful experiment when it closes a plausible path and is documented well enough not to repeat accidentally.

## Definition of a useful result

A result is useful when it improves at least one of:

- held-out geometric or ink quality;
- quality at fixed human effort;
- runtime, memory, or storage;
- robustness to scan, scroll, or resolution shift;
- reproducibility and debugging;
- community usability and documentation.

