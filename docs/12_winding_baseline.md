# Relative-Winding CPU Baseline

The first geometry algorithm is intentionally simple: deterministic graph propagation over constraints of the form

```text
winding[target] - winding[source] = delta
```

It assigns an arbitrary zero origin per connected component and records every edge that disagrees with an already assigned path. It never silently removes contradictions.

## Why build this before GPU work

- It gives every later solver a reference implementation.
- It produces synthetic truth cases without downloading scroll data.
- It tests sign conventions and disconnected components.
- It exposes contradiction counts and weighted satisfaction for benchmark reports.
- It gives us a stable adapter boundary for `winding-sync`, official `villa` inputs, and future GPU kernels.

## What it is not

This is not intended to beat the current robust synchronization projects. It is the transparent baseline against which confidence calibration, L1 synchronization, proposal filtering, and learned evidence can be measured.

## Next experiment

Add a public-data adapter and compare:

1. raw propagation;
2. confidence-ordered propagation;
3. robust integer synchronization;
4. rejection of low-confidence edges;
5. held-out spiral-fit quality using an external evaluator.

The baseline can already be run on the planted contradiction fixture:

```bash
PYTHONPATH=src python3 scripts/solve_winding.py \
  experiments/fixtures/winding_conflict.json --confidence-order
```

The command exits nonzero when contradictions are present. That behavior is deliberate: a benchmark or pipeline must not report a clean solve while discarding incompatible evidence.
