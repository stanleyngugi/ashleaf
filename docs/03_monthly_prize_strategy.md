# Monthly Prize Strategy

## Operating model

Each month we should aim to submit one or more of the following:

1. a usable open-source tool;
2. a reproducible benchmark or validation result;
3. a real-data improvement;
4. a verified bug report and fix;
5. a GPU or memory optimization;
6. documentation that makes an existing method materially easier to use.

The strongest submissions combine at least two: for example, a tool plus a benchmark, or a bug fix plus a regression test.

## Recommended first release

**Winding Evidence Lab v0.1:** a CLI and report generator that checks official spiral-input assets, detects metadata inconsistencies, proposes candidate winding constraints, and exports confidence-ranked constraints with QC overlays.

Why this first:

- it directly targets an official open problem;
- it leverages our old spiral and pitch work without importing the old Kaggle assumptions;
- it can deliver value before a full scroll is automatically unwrapped;
- it naturally supports ablations and held-out evaluation;
- it creates a shared geometric substrate for Viterbi, MWS, graph, and neural branches.

## Submission checklist

- public permissive license and clean repository;
- installation instructions tested on a fresh environment;
- one-command demo on a small public sample or synthetic fixture;
- exact commit, seed, data version, and hardware recorded;
- before/after metrics and runtime/memory measurements;
- failure gallery and known limitations;
- no private data, credentials, or hidden manual steps;
- clear relationship to official formats and tools;
- upstream issue or pull request when appropriate.

## Monthly cadence

### Week 1: instrument

Reproduce the official baseline, validate data contracts, and build the cheapest end-to-end test.

### Week 2: branch

Run parallel experiments across at least three families: a classical/geometric baseline, a graph/topology branch, and a learned or GPU branch.

### Week 3: verify

Repeat winners on held-out evidence, test for leakage and shortcut behavior, and stress runtime/memory.

### Week 4: release

Freeze a small useful contribution, write the report, publish the code, and submit. Archive failures so the next month starts from evidence rather than memory.

