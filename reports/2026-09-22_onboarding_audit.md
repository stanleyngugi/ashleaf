# Repository and Ecosystem Onboarding Audit — 2026-09-22

## Scope

This report records what was actually inspected and reproduced before the 2026-09-22 strategy update. It separates onboarding evidence from the recommendations in [`docs/21_project_intelligence_2026-09-22.md`](../docs/21_project_intelligence_2026-09-22.md).

## Local repository review

Reviewed:

- root README, package metadata, ignore rules, and Git history/status;
- all project documents `docs/00` through `docs/20` as they existed at the start of the audit;
- all reports and experiment manifests/fixtures/registry entries;
- every module under `src/`;
- every script under `scripts/`;
- every test under `tests/`;
- tracked small artifacts and public-data provenance records;
- ignored data layout sufficiently to identify pinned small data and external checkouts.

Repository state at the start of review: clean `main` tracking `origin/main`, head `c08db9f`.

The local `.venv` is Linux/WSL-oriented. Running it directly from PowerShell is not the supported path; invoke it from WSL or create a separate Windows environment.

## Local verification

Command:

```bash
cd /mnt/c/Users/stanley/Desktop/new_vesuvius
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -q
```

Result on 2026-09-22:

```text
Ran 33 tests in 12.902s
OK
```

The previously committed public smoke evidence was also read and checked against the current implementation. Its bounded claim remains: on two selected Paris 4 patches, one known-bad cached bbox excludes a z window that contains 50 usable vertices; the control patch contains none there. No full-corpus prevalence claim was reproduced locally in this audit.

## `constraint-gauge` review

Checkout:

- repository: <https://github.com/pscamillo/constraint-gauge>
- local/remote head checked: `a72c4235862be12ae975402e7ec239713fd2b216`

Reviewed its README, complete GATE0 criteria/addenda, data provenance registry, gauge modules, runners, tools/tests, committed summaries, and representative pair results.

Self-contained scripts executed successfully:

- synthetic gauge;
- ground-truth tau;
- local tau;
- planar case;
- density gate;
- mesh spacing;
- mesh ground truth;
- pitch/arbitration checks.

The project’s own data-dependent tests were not represented as newly reproduced when their external data was unavailable. Committed result artifacts were treated as upstream evidence, with provenance labels preserved.

Critical recorded open probe: GATE0 A25 states that Paris 4 annotation coordinates are on a 9.6 µm L2 grid, not the previously assumed 7.91 µm volume; after 4× conversion to the 2.4 µm grid, their z support overlaps the verified meshes. It explicitly says the prior E1 zero mesh coverage is likely a frame artifact and leaves confirmation pending.

## Current official `villa` review

Checkout:

- repository: <https://github.com/ScrollPrize/villa>
- sparse shallow snapshot: `c4902849470a2e4005c8492120007280f087d636`
- local location: ignored `data/external/villa/`

Sparse paths reviewed:

- current official website docs;
- `lasagna/tifxyz_format.md`;
- current `spiral-fitting/` README, configuration/session/service code, fitter entry points, helper modules, tests, and autoresearch notes;
- current spiral-input documentation available in the snapshot.

Important consequence: current fitter code already contains substantially more source enablement, input/checkpoint preflight, structural-loss diagnostics, and run snapshotting than early local plans assumed. Any new fitter preflight must demonstrate a current missing invariant rather than target an older code path.

## Current web research

Primary sources checked on 2026-09-22:

- official prize rules and deadline: <https://scrollprize.org/prizes>;
- official winding-constraints problem statement: <https://scrollprize.org/open_problems/winding_annotations>;
- official/community-awarded project catalog: <https://scrollprize.org/community_projects>;
- current public repositories for `tifxyz-repair`, `winding-sync`, `winding-ruler`, `spiralcheck`, consumer-GPU fitting, `constraint-gauge`, and current official `villa`;
- current relevant official `villa` issues/PR context for stale bboxes, scale semantics, outer-shell sizing, and dense-input behavior.

The official prize page showed:

- $20,000 guaranteed for Best Submission of the Month;
- next deadline 2026-09-30 at 11:59 p.m. Pacific;
- preference for early release, actual use, real-data improvement, live bug fixes with evidence, actionable analysis, and strong documentation;
- core requirements for a specific problem/solution, significant advantage over existing solutions, examples/docs, standard formats, consistent outputs, and modular integration.

The community catalog and `tifxyz-repair` repository establish that the stale-bbox problem is already covered at a scope much larger than this repository’s initial two-patch smoke test. That evidence caused the candidate pivot; it was not inferred from popularity or stars.

## Browser and compute state

The built-in browser contained an authenticated Colab notebook (`Untitled2.ipynb`). It was not connected to a runtime, no cells were run, and no GPU work occurred during this audit. Gmail was present in another tab and was deliberately not inspected because it was outside scope.

The Colab notebook is a future compute surface, not a durable project record. Session requirements are documented in [`docs/23_colab_compute_runbook.md`](../docs/23_colab_compute_runbook.md).

## Changes produced by the audit

- Added an organized documentation map.
- Added the dated project intelligence and competitive-strategy brief.
- Added a gated September execution board.
- Added a Colab compute runbook.
- Marked the original bbox-preflight release plan as superseded while retaining it as history.
- Reclassified experiment E0010 as a component rather than the headline.
- Registered E0011, FrameBridge, as the active experiment.
- Ignored `.firecrawl/`, a local research-tool cache/work directory.

No model was trained, no CT volume was downloaded in full, no external repository was modified, no issue/PR was posted, no public release was made, and no prize submission was sent.

## Remaining uncertainties

- FrameBridge novelty must be rechecked immediately before implementation/public release; the ecosystem moves quickly.
- The required gradient-field and mesh data access/size must be measured before download.
- The exact frame transform may require origin/affine details beyond a simple 4× scale.
- A corrected transform may restore support but still yield poor E1 accuracy; that is an acceptable scientific outcome, not a promised win.
- The project needs an explicit permissive-license decision before public release.
- External review/community use cannot be manufactured internally and remains a release risk with eight days left.
