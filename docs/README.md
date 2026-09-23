# Documentation Map

Start here when returning to the project after time away.

## Current decision stack

Read these in order:

1. [Project Intelligence — 2026-09-22](21_project_intelligence_2026-09-22.md): what was inspected, what changed, competitive landscape, and why the project pivoted.
2. [September Execution Board](22_september_execution_board.md): active work packages, gates, calendar, experiment matrix, fallbacks, and definition of done.
3. [Experiment Protocol](04_experiment_protocol.md): rules for leakage, baselines, metrics, reproducibility, and promotion.
4. [External Winding Benchmark](18_external_winding_benchmark.md): how third-party winding tools and `constraint-gauge` are evaluated.
5. [Colab Compute Runbook](23_colab_compute_runbook.md): GPU/session discipline after CPU gates pass.
6. [FrameBridge Coordinate Contract](24_framebridge_contract.md): active coordinate schema, conventions, controls, and unresolved assumptions.
7. [Competitive Intelligence — 2026-09-22](25_competitive_intelligence_2026-09-22.md): read-only Discord scan, novelty boundary, and current evidence bar.
8. [E1 Applicability-Matched Mesh Protocol](26_e1_applicability_protocol.md): preregistered local-correspondence diagnostic after FB04.
9. [FrameBridge FB06 Decision](27_framebridge_fb06_decision_2026-09-22.md): mixed held-out replication, honest claim boundary, competitive assessment, and FB07 plan.
10. [Research Worklog — 2026-09-22](28_research_worklog_2026-09-22.md): material progress, failures, storage actions, verification state, and exact evidence boundaries.
11. [FB07 Confidence Protocol](29_fb07_confidence_protocol.md): preregistered leave-one-segment-out confidence-ranking diagnostic.
12. [September FrameBridge Release Runbook](30_september_release_runbook.md): official-criteria alignment, release gates, commands, public narrative, and submission checklist.
13. [Prepublication Claim Audit](31_prepublication_claim_audit_2026-09-23.md): system-level release thesis, constant-label baseline, evidence boundaries, and independent-review action log.
14. [FrameBridge Public-Data Demo](32_framebridge_public_demo.md): cloneable CPU-only metadata/index planning demo, expected output, storage costs, and Windows/Unix commands.
15. [Public Release Record — 2026-09-23](33_public_release_2026-09-23.md): published repository, audit and test evidence, claim boundary, and next prize gates.
16. [Community Introduction Draft — 2026-09-23](34_community_outreach_draft_2026-09-23.md): ready-to-post Discord framing and channel/feedback checklist; not yet posted.
17. [Ashleaf Name and Repository Rename](35_ashleaf_name_2026-09-23.md): project/tool naming hierarchy, public URL migration, and verification checklist.
18. [September Winning Sprint — 2026-09-23](36_september_winning_sprint_2026-09-23.md): current decision, evidence gates, owner-facing calendar, and submission path.

The root [README](../README.md) is the compact project entry point. The experiment queue lives in [`experiments/registry.csv`](../experiments/registry.csv).

## Status vocabulary

- **Active:** governs current work.
- **Reference:** still valid background or a reusable protocol/component.
- **Historical:** records how a decision was reached; do not treat its recommendation as current.
- **Exploratory:** a research lane, not a committed build.

## Documents by function

### Mission, strategy, and execution

| Document | Status | Purpose |
|---|---|---|
| [00 Project Charter](00_project_charter.md) | Reference | Mission, near-term objective, tracks, decision principles |
| [03 Monthly Prize Strategy](03_monthly_prize_strategy.md) | Reference | Prize-oriented release model and checklist |
| [08 Execution Plan](08_execution_plan.md) | Historical/reference | Initial phased execution plan |
| [14 Master Roadmap](14_master_roadmap.md) | Reference | Multi-horizon research roadmap |
| [20 September Release Plan](20_september_release_plan.md) | Historical | Original bbox-preflight candidate; explicitly superseded on 2026-09-22 |
| [21 Project Intelligence](21_project_intelligence_2026-09-22.md) | **Active** | Current evidence, ecosystem, pivot, ranked lanes, winning thesis |
| [22 September Execution Board](22_september_execution_board.md) | **Active** | Day-by-day gated plan for FrameBridge |

### Context and ecosystem

| Document | Status | Purpose |
|---|---|---|
| [01 Old Project Audit](01_old_project_audit.md) | Reference | What can and cannot be reused from the previous repository |
| [02 Official Ecosystem](02_official_ecosystem.md) | Reference | Official repositories, formats, data, and workflows |
| [07 Research Bibliography](07_research_bibliography.md) | Reference | Technical sources and relevance notes |
| [09 Old Code Porting Notes](09_old_code_porting_notes.md) | Reference | Guardrails for importing old components |
| [10 Competition Gap Analysis](10_competition_gap_analysis.md) | Historical/reference | Initial opportunity analysis; cross-check against document 21 before acting |

### Research methods and ideas

| Document | Status | Purpose |
|---|---|---|
| [04 Experiment Protocol](04_experiment_protocol.md) | **Active** | Reproducible experiment rules and promotion gates |
| [05 Research Map](05_research_map.md) | Exploratory | Geometry, topology, ML, and systems branches |
| [12 Winding Baseline](12_winding_baseline.md) | Reference | Local winding-evidence and synchronization baseline |
| [13 GPU Experiment Plan](13_gpu_experiment_plan.md) | Exploratory/reference | Earlier GPU ideas; use document 23 for actual session procedure |
| [18 External Winding Benchmark](18_external_winding_benchmark.md) | **Active** | Accuracy/coverage/provenance rules for outside tools |
| [23 Colab Compute Runbook](23_colab_compute_runbook.md) | **Active when GPU is used** | Reproducible Colab execution and storage contract |
| [24 FrameBridge Coordinate Contract](24_framebridge_contract.md) | **Active** | Explicit frame schema, transform mathematics, validation guarantees, and FB00 procedure |
| [25 Competitive Intelligence](25_competitive_intelligence_2026-09-22.md) | **Active/internal** | Current Discord context, duplication check, publication discipline, and competitive bar |
| [26 E1 Applicability Protocol](26_e1_applicability_protocol.md) | **Active** | Predeclared adjacent-wrap local pairing, orientation contract, metrics, and promotion gates |
| [27 FrameBridge FB06 Decision](27_framebridge_fb06_decision_2026-09-22.md) | **Active** | Mixed replication interpretation, current winning thesis, FB07 confidence plan, and stop rules |
| [28 Research Worklog — 2026-09-22](28_research_worklog_2026-09-22.md) | **Active log** | Chronological experiment, verification, failure, and storage record |
| [29 FB07 Confidence Protocol](29_fb07_confidence_protocol.md) | **Active** | Frozen LOSO ranking models, features, metrics, interpretation gates, and claim boundary |
| [30 September Release Runbook](30_september_release_runbook.md) | **Active** | Official-rule alignment, hygiene/publication/community/submission gates, quick verification, and disclosure text |
| [31 Prepublication Claim Audit](31_prepublication_claim_audit_2026-09-23.md) | **Active** | Release framing, constant `+1` baseline, evidence map, and audit resolution |
| [32 FrameBridge Public-Data Demo](32_framebridge_public_demo.md) | **Active** | Hash-pinned metadata fetch, sparse index proof, range-plan quickstart, and full-pipeline dependency boundary |
| [33 Public Release Record](33_public_release_2026-09-23.md) | **Active** | Public GitHub status, audited release checks, known limitations, and next actions |
| [34 Community Introduction Draft](34_community_outreach_draft_2026-09-23.md) | **Active** | Discord announcement draft, current browser blocker, and feedback-recording discipline |
| [35 Ashleaf Name and Repository Rename](35_ashleaf_name_2026-09-23.md) | **Active** | Brand decision, repository URL migration, and publication verification |
| [36 September Winning Sprint](36_september_winning_sprint_2026-09-23.md) | **Active** | Prize-oriented next experiments, integration proof, decision gates, and deadline |

### Data contracts and reliability components

| Document | Status | Purpose |
|---|---|---|
| [06 Security and Provenance](06_security_and_provenance.md) | **Active** | Supply-chain, data, secret, and provenance rules |
| [11 Manifest Schema](11_manifest_schema.md) | **Active** | Current experiment-manifest contract |
| [15 TIFXYZ Audit](15_tifxyz_audit.md) | Reference/component | Metadata and pixel-aware patch checks |
| [16 OME-Zarr Metadata](16_omezarr_metadata.md) | Reference/component | Multiscale metadata and memory planning |
| [17 PointCollection Audit](17_pointcollection_audit.md) | Reference/component | Annotation parsing and validation |
| [19 Fit Window Preflight](19_fit_window_preflight.md) | Reference/component | Integrated ROI check; useful but no longer the release headline |

## Reports and evidence

| Report | Evidence level | Contents |
|---|---|---|
| [Initial Research — 2026-09-18](../reports/2026-09-18_initial_research.md) | Historical research record | Initial official/source review and strategy |
| [Public Patch Smoke — 2026-09-18](../reports/2026-09-18_public_patch_smoke.md) | Verified here on pinned small data | Public-data fetch/audit smoke result |
| [Fit-Window False Negative — 2026-09-18](../reports/2026-09-18_fit_window_false_negative.md) | Verified here on two selected patches | Known stale-bbox reproduction and limitations |
| [Onboarding Audit — 2026-09-22](../reports/2026-09-22_onboarding_audit.md) | Verified review/reproduction ledger | Files/upstreams inspected, tests run, browser/compute state, and remaining uncertainties |
| [FrameBridge FB00 — 2026-09-22](../reports/2026-09-22_framebridge_fb00.md) | Verified here, z-support only | Wrong-frame control, corrected 95 mm overlap, evidence labels, and next gates |
| [FrameBridge FB01 — 2026-09-22](../reports/2026-09-22_framebridge_fb01.md) | Verified here, full allocation bounds | Nine meshes, annotations, umbilicus, and group-4 field overlap in physical xyz |
| [FrameBridge FB02 — 2026-09-22](../reports/2026-09-22_framebridge_fb02.md) | Verified here, sparse-index planning | `respool` integrity, exact byte-range contract, per-mesh costs, and pilot selection |
| [FrameBridge FB03 — 2026-09-22](../reports/2026-09-22_framebridge_fb03.md) | Verified here, exact pilot rays | Wrong-frame 0/19,999 control, corrected 19,999/19,999 seven-ray support, and 117.1 MiB acquisition plan |
| [FrameBridge FB04 — 2026-09-22](../reports/2026-09-22_framebridge_fb04.md) | Frozen negative accuracy result | Coverage 1.000, exact `dw=1` 0.000, MAE 69.844, and quantified pair-applicability mismatch |
| [FrameBridge FB05 — 2026-09-22](../reports/2026-09-22_framebridge_fb05.md) | Preregistered one-mesh diagnostic | 20,000 adjacent-wrap local pairs; 92.385% exact signed accuracy, 0.0794 MAE, full coverage |
| [FrameBridge FB06 — 2026-09-22](../reports/2026-09-22_framebridge_fb06.md) | Frozen held-out replication plus labeled exploration | Three eligible held-outs at 45.60%, 86.72%, and 92.07%; five ineligible; full reliability curve and failure analysis |
| [FrameBridge FB07 — 2026-09-22](../reports/2026-09-22_framebridge_fb07.md) | Internal LOSO cross-validation | Geometry ranking modestly beats distance at 30% coverage; native E1 confidence fails to transfer well; release decision |

Future empirical results belong under `reports/` with a date and corresponding manifests/artifacts. Strategy and enduring instructions belong under `docs/`.

## Source-of-truth hierarchy

When documents disagree, use this order:

1. Current official prize rules and current official source code.
2. Pinned raw data/metadata and reproducible local measurements.
3. The latest dated project intelligence/decision record.
4. Stable protocols and schemas.
5. Older plans, exploratory notes, and remembered assumptions.

Do not silently rewrite historical reports to match a new conclusion. Add a dated status notice or a new decision record so the reasoning remains auditable.

## Maintenance rules

- Update this map when adding a durable document.
- Put a date in time-sensitive research/decision filenames.
- Mark superseded recommendations at the top of the original file.
- Link claims to a command, manifest, result artifact, upstream commit, or primary URL.
- Separate verified fact, upstream fact, inference, hypothesis, and decision.
- Keep generated large artifacts out of Git; retain small summaries and hashes.
