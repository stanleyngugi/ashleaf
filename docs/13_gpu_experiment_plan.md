# GPU Experiment Plan

GPU access is intentionally deferred until the CPU contracts and benchmark manifests are stable. When access arrives, the first runs should validate the infrastructure rather than launch a large training job.

## GPU readiness ladder

### G0 — environment fingerprint

Record GPU model, VRAM, driver, CUDA, PyTorch, Zarr, compiler versions, power/clock settings, and repository commit.

### G1 — numerical and hash parity

Run CPU and GPU implementations on the same synthetic fixtures. Compare labels, constraint residuals, mesh/volume hashes where exact parity is expected, and bounded floating-point tolerances where it is not.

### G2 — scaling benchmark

Measure throughput, peak allocated/reserved memory, host-to-device transfer time, and cost per processed voxel across tile sizes and batch sizes.

### G3 — real-data smoke test

Run one small public asset with complete logs and visual output. Inspect for axis swaps, missing slices, stale metadata, and silent fallback.

### G4 — controlled research ablation

Only after G0–G3 pass, compare Viterbi proposals, affinity/MWS variants, graph synchronization, self-supervised features, or learned geometry on a held-out split.

## GPU research families

- tiled OME-Zarr reads and pinned-memory staging;
- GPU local tangent, normal, and structure-tensor extraction;
- batched winding-edge proposal generation;
- differentiable or parallel integer-synchronization proposals;
- affinity prediction with instance-preserving MWS;
- Viterbi cost-volume construction and batched dynamic programming;
- mixed precision and kernel fusion for surface/ink inference;
- GPU mesh projection, welding, and flattening benchmarks.

## Non-negotiable checks

- no benchmark without a CPU reference;
- no speedup claim without output-equivalence checks;
- no large run without a memory estimate and kill threshold;
- no learned result without shortcut and leakage diagnostics;
- every crash becomes a regression fixture where practical.

