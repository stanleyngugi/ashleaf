# Current Official Ecosystem

Checked against the official website and `ScrollPrize/villa` on 2026-09-18.

## Competition shape

The current Scroll Prize combines machine learning, computer vision, geometry, and systems engineering. The monthly Progress Prizes are open-ended and reward public, useful work: real-data improvements, bug fixes, speedups, documentation, and actionable information. This strongly favors small, verifiable releases.

The long-horizon Grand Prize requires an automated, reproducible workflow that can produce a complete readable scroll under the published rules. It is strategically important, but it should not prevent monthly submissions.

## Official pipeline components

- **VC3D / Volume Cartographer:** surface extraction and tracing lineage used by the challenge team.
- **Lasagna:** PyTorch-based surface-mesh optimization, including stacked-sheet consistency and fiber tracing.
- **Spiral fitting:** globally coherent whole-scroll fit using patches, fibers, and winding annotations.
- **Ink detection:** surface-volume models and iterative pseudo-labeling workflows.
- **Data formats:** OME-Zarr for primary volumes, TIFF/TIFXYZ and OBJ for derived surfaces, JSON metadata, and official curated datasets.

## Current data contracts

The July 2026 curated datasets include:

- `spiral-input`: surface patches, lines, points, winding constraints, umbilicus, and related geometry;
- `surface-labels`: voxelized recto surface labels paired with volume data;
- `ink-labels`: binary ink masks plus supervision/validation masks.

The new repository should validate metadata and geometry before using them. Public issue reports have already identified examples where stale bounding boxes can silently drop valid patch vertices and where a `scale` value can cause flattening to request terabytes of memory. These are precisely the kind of high-value, low-glamour defects that can produce a monthly-prize submission.

## Relevant official links

- [Scroll Prize](https://scrollprize.org/)
- [Prizes and rules](https://scrollprize.org/prizes)
- [Data](https://scrollprize.org/data)
- [Curated datasets](https://scrollprize.org/data_datasets)
- [Spiral-fitting tutorial](https://scrollprize.org/tutorial_spiral)
- [Winding-annotation open problem](https://scrollprize.org/open_problems/winding_annotations)
- [Official `villa` repository](https://github.com/ScrollPrize/villa)

