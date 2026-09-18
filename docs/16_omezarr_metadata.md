# OME-Zarr Metadata Preflight

The current public CT volumes use OME-Zarr for chunked, multiresolution access. A local copy of the metadata is enough to plan an experiment without downloading the volume.

## Public smoke test

```bash
python3 scripts/fetch_smoke_zarr_metadata.py
python3 scripts/audit_zarr_metadata.py \
  data/PHerc0125/volumes/20250821151825-9.362um-1.2m-113keV-masked.zarr
```

The downloader fetches only `.zgroup`, `.zattrs`, and six `.zarray` files. Their SHA-256 values are pinned in the script. It fetches no CT chunks.

On 2026-09-18, the metadata audit found six valid levels, `zyx` axes, `uint8` values, and 128³ chunks. The highest-resolution shape was 20,840 × 8,387 × 8,387 voxels, about 1.466 TB uncompressed. The coarsest level was 652 × 263 × 263 voxels, about 45 MB uncompressed. These estimates are uncompressed array sizes, not network transfer costs or actual storage sizes.

The metadata's coordinate transforms are relative pyramid scales (1, 2, 4, 8, 16, 32). They do not by themselves establish the physical voxel size; the scan catalog and artifact metadata must be consulted for that.

Plan a bounded read before allocating memory or starting a GPU job:

```bash
python3 scripts/plan_zarr_roi.py \
  data/PHerc0125/volumes/20250821151825-9.362um-1.2m-113keV-masked.zarr \
  --level 3 --start 0 0 0 --stop 256 256 256
```

The ROI is half-open in the metadata's axis order (`zyx` here). The planner reports touched chunks and a conservative uncompressed byte bound. A one-voxel shift can increase a 256³ ROI from 8 to 27 touched 128³ chunks, so chunk alignment matters for throughput and memory. This bound does not include decoder buffers or model tensors.

## Current checks

- Zarr v2 group marker and OME multiscales metadata;
- named unique axes;
- each referenced level exists and has positive shape/chunk values;
- dtype and relative scale are parseable;
- dimensions agree across shape, chunks, axes, and transforms;
- a warning when level shapes disagree strongly with scale factors.

The current adapter reads local metadata only. Remote metadata fetch is a separate, pinned step to keep provenance explicit. It does not verify chunk contents or multiscale value correctness; dedicated community tools already do that.

## References

- [Official data formats](https://scrollprize.org/data)
- [Official open data repository](https://github.com/ScrollPrize/open-data)
