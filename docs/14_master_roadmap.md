# Master Roadmap

This is the execution plan for the research lab. It is designed to keep monthly contributions moving while preserving room for major technical experiments.

## Track A — monthly-prize contribution engine

### A1. Contract and provenance layer — active

- JSON manifest schema;
- geometry metadata checks;
- stable asset identifiers;
- run fingerprints;
- malformed-data regression fixtures.

### A2. Cross-tool benchmark — next

- adapters for official OME-Zarr, TIFXYZ, meshes, annotations, and prediction outputs;
- normalized coordinate/spacing conventions;
- external-tool version and provenance capture;
- common held-out manifests;
- metrics for quality, coverage, contradictions, runtime, memory, and human effort.

### A3. Winding evidence — next

- ingest existing community synchronization and annotation outputs;
- compare raw propagation, robust synchronization, and rejection policies;
- evaluate candidate constraints with `spiralcheck` or an equivalent held-out protocol;
- publish failure galleries and actionable upstream issues.

### A4. Release and feedback loop

- release a small tool early;
- obtain real users and issue reports;
- fix usability/integration defects;
- submit monthly evidence;
- fold feedback into the next benchmark.

## Track B — geometry and surface research

- Viterbi as proposal/confidence field;
- LOGISMOS-like ordered surface graphs;
- instance-preserving affinity/MWS experiments;
- physics-inspired mesh refinement;
- implicit and level-set probes;
- surface self-intersection and flattening diagnostics.

Every branch must use the same manifest, split, and report format.

## Track C — ink and representation learning

- reproduce official ink baselines;
- cross-scroll and cross-resolution split audits;
- self-supervised 3D feature probes;
- uncertainty and active-learning selection;
- false-positive and hallucination checks;
- only then large domain-generalization experiments.

## Track D — GPU systems

- GPU environment fingerprint;
- CPU/GPU parity tests;
- tiled OME-Zarr access;
- pinned transfers and mixed precision;
- GPU winding cues and cost volumes;
- Viterbi, affinity, rendering, projection, and meshing kernels;
- scaling reports across tile sizes and VRAM limits.

## Promotion gates

An idea earns more compute only when it has:

1. a reproducible baseline;
2. a held-out or planted-defect test;
3. a measurable advantage;
4. a failure analysis;
5. an integration path into official/community formats.

## Immediate build queue

1. Finish official-format adapters.
2. Run the baseline on a tiny public sample.
3. Add the first cross-tool manifest.
4. Compare existing winding tools rather than duplicating them.
5. Release the reliability harness.
6. Begin GPU parity and scaling experiments when hardware is available.

