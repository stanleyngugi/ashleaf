# Experiment Protocol

## Required run record

Every nontrivial run must record:

- hypothesis and baseline;
- code commit and configuration;
- data source, version, and split policy;
- random seeds and deterministic settings;
- hardware, software, CUDA, and GPU memory;
- wall time, peak memory, and storage;
- primary metric and secondary diagnostics;
- failure cases and visual artifacts;
- decision: promote, revise, archive, or stop.

## Evaluation hierarchy

Use the strongest available evidence and label it explicitly:

1. official evaluation or community-accepted benchmark;
2. held-out real data with no annotation or asset leakage;
3. held-out regions from known volumes;
4. synthetic fixtures with planted defects;
5. train-overlap or smoke tests.

Lower levels are useful for debugging but cannot justify a production claim.

## Anti-shortcut checks

For every model or learned postprocessor, report:

- foreground fraction by volume and by patch;
- prediction entropy and connected-component statistics;
- output similarity across different volumes of the same shape;
- calibration or confidence histograms;
- performance by thickness, curvature, scan resolution, and artifact severity;
- train/validation overlap and nearby-patch leakage.

## Promotion gates

An idea moves from exploration to a serious branch only if it passes all applicable gates:

- improves a held-out primary metric or a clearly valuable systems metric;
- does not regress a critical safety metric beyond a stated tolerance;
- has a reproducible run and a failure explanation;
- fits the monthly contribution scope or has an explicit Grand Prize rationale;
- has a bounded compute budget for the next experiment.

## Experiment families

We will deliberately maintain breadth:

- classical geometry and dynamic programming;
- graph optimization and LOGISMOS-like layered surfaces;
- affinity learning, connectomics, and MWS;
- implicit/level-set and neural surface representations;
- self-supervised 3D representations and domain adaptation;
- diffusion and generative restoration as proposal mechanisms;
- physics-inspired mesh refinement and optimal transport;
- GNNs, equivariant models, recurrent surface tracers, and active learning;
- GPU kernels, tiled I/O, mixed precision, and memory-aware inference.

Complexity is justified only by a measurable advantage.

