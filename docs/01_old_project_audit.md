# Audit of the Former Vesuvius Repository

Source: `C:\Users\stanley\Documents\folder\Vesuvius` (read-only reference repository).

## Inventory

The repository contains 169 Markdown files, of which 121 have distinct content after excluding Git metadata, virtual environments, and duplicated copies. It combines:

- the 2025 Kaggle surface-detection attempt;
- Viterbi-style surface tracking and a legacy Mutex Watershed (MWS) path;
- spiral fitting and pitch-estimation research;
- topology, LOGISMOS, OCT, connectomics, and graph-method research;
- extensive implementation notes and GPU validation reports.

The documents are valuable as a record of hypotheses and failure modes, but their age and duplication make them unsafe as an unquestioned specification.

## What we should borrow

### 1. Empirical failure discipline

The most important evidence is not the claimed local score. A foreground-variation report found that model predictions were nearly identical for all same-sized volumes—about 99.88% foreground for the 320³ group and about 66% for the 256³ group. That is a classic shortcut/underfitting warning and should become a mandatory per-volume prediction sanity check.

The former project also found a checkpoint-selection bug where loss was negated before deciding whether a checkpoint was best. The fix is a permanent rule here: checkpoint selection, metric direction, and validation split must be unit-tested.

### 2. Reusable geometry ideas

The spiral work explored radial profiles, autocorrelation, surface tracks, winding pairs, variable pitch, and cylindrical/flattened representations. These ideas map naturally to the current official `spiral-input` datasets and winding-constraint open problem.

### 3. Topology ideas as experiments, not assumptions

Viterbi, LOGISMOS-like layered graph optimization, skeleton-guided MWS, affinity prediction, and topology-aware post-processing are all worth preserving behind explicit adapters. They are not yet a reason to commit the whole project to one segmentation representation.

## What failed or remains unproven

### Viterbi-as-mask

The GPU validation report from 2026-02-17 is decisive for the old Kaggle task: on a real three-volume core, the Viterbi variant reduced the local composite score by roughly 0.112 on average, with a worst-volume drop around 0.188. Mean runtime was about 637–646 seconds, exceeding the stated 300-second budget. The report attributes the loss to sparse masks hurting Dice/SurfaceDice/VOI, while topology improved in isolation.

Conclusion: keep Viterbi as a controlled research branch; do not use it as the default output representation.

### MWS/binary round-trip

The old notes indicate that converting instance structure through MWS and back to a binary mask erased much of the information MWS was supposed to preserve. This is an interface-design failure, not evidence that MWS itself is useless. Future MWS experiments must evaluate instance-aware outputs and must not collapse them to binary masks until the final interface.

### Metric confidence

Several old local evaluations approximated the official metric or overlapped training volumes. Reported numbers are therefore evidence about implementation behavior, not leaderboard predictions. New experiments must label every score as `train-overlap`, `held-out`, `synthetic`, or `official`.

## Porting policy

We will port concepts first, then small tested components. We will not copy the old repository wholesale because it contains stale paths, duplicate documents, historical speculative claims, dirty worktree state, and exposed credentials in historical files/remotes.

The official current integration point is `ScrollPrize/villa`; our repository should provide adapters, benchmarks, and contributions around it rather than fork the entire ecosystem.

