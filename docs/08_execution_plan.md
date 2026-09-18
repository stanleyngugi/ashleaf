# Execution Plan

## Phase 0 — repository and evidence foundation

Completed in the initial commit:

- old-repository audit and failure ledger;
- official ecosystem and prize requirements;
- research map and bibliography;
- experiment protocol and registry;
- security/provenance rules.

## Phase 1 — cheap, CPU-safe correctness layer

First implementation work:

1. metadata, bounding-box, spacing, and shape validators;
2. synthetic fixtures with malformed metadata and planted geometry defects;
3. deterministic report format;
4. tests that run without a GPU or large data download.

This phase is deliberately unglamorous. It protects every later GPU experiment from silent data errors.

## Phase 2 — winding-evidence baseline

Implement progressively:

1. local tangent/normal and pitch cues;
2. pair proposal generation;
3. confidence calibration and contradiction reports;
4. baseline BFS/integer synchronization;
5. held-out evaluation against verified Paris 4 annotations.

## Phase 3 — parallel research branches

Run bounded probes for weighted synchronization, graph optimization, Viterbi-as-proposal, instance-aware MWS, implicit surfaces, and self-supervised geometry. No branch receives a large training run before it passes a cheap synthetic/public-data gate.

## Phase 4 — monthly release loop

Package the strongest result as a standalone tool, publish a report and demo, open upstream issues/PRs where appropriate, and submit before the monthly deadline. Continue experiments after release rather than freezing the whole project around one result.

## Compute policy

The local environment is currently CPU-only and lacks the Python scientific stack. GPU runs will be performed in a separately fingerprinted environment. The repository must remain useful for review, testing, and report generation without requiring the full GPU environment.

