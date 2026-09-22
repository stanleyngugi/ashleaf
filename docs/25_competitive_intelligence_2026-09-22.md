# Competitive Intelligence — 2026-09-22

Status: internal working note; Discord observations are contextual and must be revalidated against durable public artifacts before being used in a release claim.

## Purpose

The project has an authenticated, read-only view of the Vesuvius Challenge Discord. It was checked to answer three narrow questions:

1. Is the 2.4 µm / 9.6 µm frame mismatch already known publicly?
2. Has anyone already published the corrected independent E1 mesh-arm measurement?
3. What level of evidence is currently competitive for a September progress submission?

No messages, reactions, uploads, or other representational actions were made.

## Search record

Date observed: 2026-09-22, Africa/Nairobi timezone.
Server: Vesuvius Challenge.
Read surfaces: `#rules`, `#robots`, and server-wide search results.
Focused searches: `E1` and `9.6`.

Discord content is mutable, search is not a complete archive, and some result context could not be loaded. Absence from search is therefore weak evidence.

## Findings

### 1. The coordinate problem is public

The `constraint-gauge` author publicly recorded the August correction that Paris 4 annotated coordinates live on the 9.6 µm grid of the 2.4 µm rescan, not the previously assumed 7.91 µm volume. The post explicitly describes this as the third frame error in that project.

This means we must not pitch FrameBridge as discovering that annotations are 9.6 µm. That credit belongs to the prior correction and its author/correspondent chain.

### 2. Clean cross-resolution mapping remains an acknowledged systems problem

A Villa team member wrote that VC3D actions essentially assume the loaded volume is native resolution while surfaces may live at 4× downsample, making clean mapping complicated. Other current discussions routinely state equivalent coordinates at 2.4 and L2 9.6 µm.

This supports the utility of an explicit frame contract, but it is not proof that our implementation is correct.

### 3. No completed corrected E1 mesh-arm score was found

The `E1` search surfaced the original `constraint-gauge` benchmark announcement and its plan to score E1. The durable repository still records mesh-arm coverage 0.000 under the old implicit frame handling. The focused searches did not surface a subsequent corrected independent-arm result.

This is only “not found,” not proof of nonexistence. Before public release we should repeat the search with the exact terms used in the result and inspect recent `constraint-gauge` changes.

### 4. The current competitive standard is high

Recent `#robots` and public forum work includes:

- held-out metrics with explicit controls and negative results;
- downloadable artifacts and exact evaluation harnesses;
- multi-seed comparisons and ablations;
- clear AI disclosure;
- careful separation of a metric improvement from actual visual/scientific utility;
- public pull requests that make results reusable by Villa.

FrameBridge must therefore ship as more than a bug observation. A credible submission needs a measured independent score, reproducible acquisition/evaluation code, negative controls, limitations, and ideally an upstream-compatible integration.

## Competitive implications

### What is not enough

- “Divide mesh coordinates by four.”
- Bounding-box overlap alone.
- A private notebook without fetch hashes and a CPU reproduction path.
- Re-fitting E1 constants on the independent meshes.
- Claiming novelty for the already-public 9.6 µm correction.

### What can still be distinctive

1. The first reproducible corrected E1 score on the independent verified-mesh arm.
2. A generic, strict coordinate-frame contract that prevents the broader class of native/pyramid/axis/order errors.
3. Sparse, byte-exact remote evaluation that avoids multi-gigabyte downloads.
4. A benchmark adapter that preserves frozen-estimator provenance.
5. An upstream patch and migration notes for existing consumers.

## Publication discipline

The server rules explicitly permit LLM-produced experiment reports in `#robots`, provided the model is named, context is useful, human commentary is separated, and claims are reproducible proposals rather than authority. The server also warns that shared work may be used by competitors.

Accordingly:

- remain read-only until the decisive pilot is complete;
- do not tease the hypothesis before we have measured evidence;
- when ready, disclose AI involvement accurately;
- publish enough for reproducibility in one coordinated release;
- credit the earlier frame correction precisely;
- avoid overstating Discord search as a novelty search.

## Decision

The Discord review does not displace E0011. It makes the bar clearer: our prize case is **execution and reusable validation**, not discovery of the scale factor. Continue to the actual-ray pilot immediately.
