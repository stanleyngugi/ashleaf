# New Vesuvius Research Lab

An experiment-first repository for the current Vesuvius Challenge / Scroll Prize.

Licensed under the [MIT License](LICENSE).

The immediate objective is to make useful, reproducible open-source contributions that can compete for the monthly Progress Prizes. The longer-term objective is to contribute to a fully automated virtual-unwrapping and ink-reading system for the 2027 Grand Prize.

## Working thesis

Deep experimentation and fast feedback are our competitive advantage. We will maintain several technical tracks in parallel—geometry, winding constraints, surface extraction, ink detection, topology, graph methods, self-supervision, and GPU systems—and promote ideas only when controlled experiments show a real gain.

The first target is a cross-tool geometry reliability and quality-control toolkit, beginning with winding constraints. It supports the official open problem without duplicating existing community annotators and synchronizers, reuses the strongest geometry work from the previous repository, can produce a useful monthly submission before a full end-to-end system exists, and gives us measurable interfaces for later Viterbi, MWS, graph, and neural experiments.

**2026-09-22 strategy update:** the original two-patch stale-bbox preflight remains a useful regression and integration component, but it is no longer the release headline: the community's `tifxyz-repair` project has already completed and repaired a full-corpus audit. The active September target is now **FrameBridge**, an explicit 2.4 µm ↔ 9.6 µm coordinate contract and an independent verified-mesh test of pairwise winding evidence. See the [project intelligence brief](docs/21_project_intelligence_2026-09-22.md) and [execution board](docs/22_september_execution_board.md).

FrameBridge has now advanced through FB06. FB00 reproduced the frame failure and recovered **~95.0 mm z overlap**; FB01 proved full xyz allocation overlap across all nine meshes; FB02 validated the public sparse indexes; and FB03 found **0/19,999 wrong-frame pairs but 19,999/19,999 corrected pairs with all seven rays in bounds**. See the [coordinate contract](docs/24_framebridge_contract.md), [FB01 report](reports/2026-09-22_framebridge_fb01.md), [FB02 report](reports/2026-09-22_framebridge_fb02.md), and [FB03 report](reports/2026-09-22_framebridge_fb03.md).

FB04 preserved the corrected generic-pair negative result: arbitrary whole-mesh chords produced 0.000 exact `dw=1` accuracy. FB05's development pilot then achieved **92.385% exact signed accuracy** on 20,000 applicability-matched local pairs. Frozen FB06 replication was heterogeneous: the three eligible held-out meshes scored **45.60%, 86.72%, and 92.07%**, while five meshes were outside the predeclared trimming domain. Pooled held-out accuracy was **70.98% at full eligible coverage**. A clearly post-hoc reliability curve reached **96.06% at 21.47% coverage** for gaps ≤16 voxels. The active claim is therefore reliability/applicability, not universal 92% accuracy. See the [FB04 negative report](reports/2026-09-22_framebridge_fb04.md), [local-pair protocol](docs/26_e1_applicability_protocol.md), [FB05 pilot](reports/2026-09-22_framebridge_fb05.md), [FB06 replication](reports/2026-09-22_framebridge_fb06.md), and [current decision](docs/27_framebridge_fb06_decision_2026-09-22.md).

FB07 then tested confidence transfer with four leave-one-segment-out rotations. At 30% coverage, a small geometry model reached **91.28% macro accuracy and 82.85% worst-segment accuracy**, compared with **90.91% and 79.00%** for distance alone. Native E1 rounding confidence performed substantially worse. Because all segment outcomes were already known, this is internal cross-validation—not new held-out evidence. See the [FB07 protocol](docs/29_fb07_confidence_protocol.md) and [FB07 report](reports/2026-09-22_framebridge_fb07.md).

## Repository map

- [`docs/`](docs/README.md) — organized project charter, competition intelligence, research methods, data contracts, active execution board, and compute runbooks.
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

Build an independently valid audit and benchmark for winding evidence:

1. Represent coordinate order, physical resolution, pyramid level, origin, and provenance explicitly.
2. Reproduce the previous zero-coverage cross-arm result with a known-wrong transform, then test the corrected transform.
3. Score frozen pairwise winding evidence against independently verified meshes without tuning on the evaluation arm.
4. Measure accuracy and coverage together, including uncertainty, calibration, and reason-coded failures.
5. If the independent baseline is viable, improve confidence and export only high-confidence official-compatible constraints.
6. Publish a small release or upstream contribution with a one-command demo, result artifacts, and a clear failure gallery.

This repository is intentionally not a copy of the former Kaggle project. The old code and documents are reference material; only validated components will be ported.

The current monthly-prize deadline listed by the official site is September 30, 2026. See [`reports/2026-09-18_initial_research.md`](reports/2026-09-18_initial_research.md) for the decision record and [`experiments/registry.csv`](experiments/registry.csv) for the active research queue.

Run the current CPU-only end-to-end fixture with:

```bash
PYTHONPATH=src python3 scripts/run_baseline_benchmark.py \
  experiments/manifests/example.json \
  experiments/fixtures/winding_conflict.json \
  --confidence-order
```

Verify the compact FrameBridge release evidence without downloading CT data:

```bash
PYTHONPATH=src .venv/bin/python scripts/check_framebridge_release.py \
  --fb06 experiments/results/framebridge_fb06_summary.json \
  --fb07 experiments/results/framebridge_fb07_loso.json
```

The check preserves the critical claim boundary: FB06 is frozen held-out replication; FB07 is internal leave-one-segment-out analysis on already observed segments.

Real-data preflight examples are documented in [`docs/15_tifxyz_audit.md`](docs/15_tifxyz_audit.md) and [`docs/16_omezarr_metadata.md`](docs/16_omezarr_metadata.md). These download only tiny public surface patches or metadata, not full CT volumes.

The [fit-window preflight](docs/19_fit_window_preflight.md) combines patch geometry and winding annotations and has a [real Paris 4 false-negative reproduction](reports/2026-09-18_fit_window_false_negative.md). It is retained as tested infrastructure, not presented as the current novel submission.

Set up a fresh Python environment and reproduce the public-data smoke checks with:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[benchmark]'
.venv/bin/python scripts/run_public_smoke.py
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -q
```

The smoke command downloads only pinned small patches, annotations, and OME-Zarr metadata; it writes a JSON report under the ignored `artifacts/` directory. Use `--no-fetch` to rerun offline. The original [September preflight plan](docs/20_september_release_plan.md) is preserved as a superseded decision record. Current work is governed by the [September execution board](docs/22_september_execution_board.md); GPU runs will follow the [Colab runbook](docs/23_colab_compute_runbook.md).
