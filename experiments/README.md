# Experiments

Experiments are short-lived probes with explicit hypotheses and stop conditions. The registry is the index; detailed run reports belong in `reports/` or an external artifact store with a stable link.

## Naming

Use `E####-short-name`, for example `E0001-data-contract-audit`.

## Minimum experiment lifecycle

1. Add a hypothesis and baseline to `registry.csv`.
2. Run the cheapest reproducible test.
3. Record metrics and artifacts.
4. Decide whether to promote, revise, or archive.
5. Update the registry and write a short report.

The first manifest fixture is `experiments/manifests/example.json`. Validate it with:

```bash
python3 scripts/validate_manifest.py experiments/manifests/example.json
```
