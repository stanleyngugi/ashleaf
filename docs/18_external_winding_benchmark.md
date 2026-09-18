# External Winding Benchmark Integration

`constraint-gauge` is the current community benchmark for winding generators against human annotations and verified meshes. It evaluates per-location accuracy, coverage, density, confidence calibration, and provenance. We use its JSON adapter contract instead of inventing a parallel score.

Our export command turns any solved node graph with full-resolution `[x, y, z]` coordinates into that contract:

```bash
python3 scripts/export_gauge_adapter.py \
  experiments/fixtures/winding_conflict.json \
  --confidence-order --output artifacts/synthetic_gauge_adapter.json
```

The fixture is synthetic and only checks the interface. It is not a scientific benchmark result. For real evaluation, feed a generator's independently produced node graph into this exporter, then run [`constraint-gauge`](https://github.com/pscamillo/constraint-gauge) on a held-out annotation or mesh arm. Declare the subject's provenance relative to each ground-truth arm before reporting a number.

The published benchmark has shown a severe gap between a generator's internal constraint agreement and external accuracy on one Paris 4 slice. It also found that sparse nodes can produce an apparently high score on the few pairs that remain matchable, which is why coverage and density gates are essential. These results are scoped to the tested configuration and slice, but the methodological lesson applies to every future branch here.

The old Kaggle project suffered from the same broad pattern: a locally encouraging metric can conceal a fundamentally wrong output. External evidence is now a promotion gate, not an optional final check.
