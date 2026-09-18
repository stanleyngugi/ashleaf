# New Vesuvius Research Lab

An experiment-first repository for the current Vesuvius Challenge / Scroll Prize.

The immediate objective is to make useful, reproducible open-source contributions that can compete for the monthly Progress Prizes. The longer-term objective is to contribute to a fully automated virtual-unwrapping and ink-reading system for the 2027 Grand Prize.

## Working thesis

Deep experimentation and fast feedback are our competitive advantage. We will maintain several technical tracks in parallel—geometry, winding constraints, surface extraction, ink detection, topology, graph methods, self-supervision, and GPU systems—and promote ideas only when controlled experiments show a real gain.

The first target is a cross-tool geometry reliability and quality-control toolkit, beginning with winding constraints. It supports the official open problem without duplicating existing community annotators and synchronizers, reuses the strongest geometry work from the previous repository, can produce a useful monthly submission before a full end-to-end system exists, and gives us measurable interfaces for later Viterbi, MWS, graph, and neural experiments.

## Repository map

- `docs/` — project charter, old-repository audit, official competition facts, research map, and experiment protocol.
- `experiments/` — hypotheses, run records, ablations, and experiment templates.
- `src/` — reusable tooling. Keep competition-specific adapters separate from general algorithms.
- `scripts/` — reproducible data checks, benchmark runners, and report generation.
- `reports/` — short decision reports; large generated artifacts stay out of Git.

## Rules of execution

1. Establish a cheap baseline before adding complexity.
2. Change one major factor at a time whenever possible.
3. Record failures, negative results, runtime, memory, and data leakage checks.
4. Never call a result “better” without a held-out evaluation and a reproducible command.
5. Treat official `villa` formats and interfaces as contracts; isolate adapters around them.
6. Prefer a small useful release over an opaque private mega-pipeline.

## Current upstreams

- Official website: <https://scrollprize.org/>
- Official monorepo: <https://github.com/ScrollPrize/villa>
- Official data index: <https://scrollprize.org/data>
- Curated datasets: <https://scrollprize.org/data_datasets>
- Winding-annotation open problem: <https://scrollprize.org/open_problems/winding_annotations>
- Spiral-fitting tutorial: <https://scrollprize.org/tutorial_spiral>

## First milestone

Build a deterministic audit and benchmark for winding evidence:

1. Read official spiral-input data without silently trusting stale metadata.
2. Generate candidate same/relative/absolute winding constraints.
3. Assign confidence and reject geometrically ambiguous candidates.
4. Export official-compatible files plus human-readable QC images/reports.
5. Measure precision, coverage, fit quality, manual time saved, runtime, and memory.
6. Publish a small release with a reproducible demo and a clear failure gallery.

This repository is intentionally not a copy of the former Kaggle project. The old code and documents are reference material; only validated components will be ported.

The current monthly-prize deadline listed by the official site is September 30, 2026. See [`reports/2026-09-18_initial_research.md`](reports/2026-09-18_initial_research.md) for the decision record and [`experiments/registry.csv`](experiments/registry.csv) for the active research queue.

Run the current CPU-only end-to-end fixture with:

```bash
PYTHONPATH=src python3 scripts/run_baseline_benchmark.py \
  experiments/manifests/example.json \
  experiments/fixtures/winding_conflict.json \
  --confidence-order
```

Real-data preflight examples are documented in [`docs/15_tifxyz_audit.md`](docs/15_tifxyz_audit.md) and [`docs/16_omezarr_metadata.md`](docs/16_omezarr_metadata.md). These download only tiny public surface patches or metadata, not full CT volumes.

The [fit-window preflight](docs/19_fit_window_preflight.md) combines patch geometry and winding annotations and has a [real Paris 4 false-negative reproduction](reports/2026-09-18_fit_window_false_negative.md).

Set up a fresh Python environment and reproduce the public-data smoke checks with:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[pixels]'
.venv/bin/python scripts/run_public_smoke.py
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -q
```

The smoke command downloads only pinned small patches, annotations, and OME-Zarr metadata; it writes a JSON report under the ignored `artifacts/` directory. Use `--no-fetch` to rerun offline. The [September release plan](docs/20_september_release_plan.md) separates completed smoke tests from evidence still needed for a strong monthly submission.
