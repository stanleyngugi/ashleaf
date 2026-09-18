# TIFXYZ Preflight and Pixel Audit

The TIFXYZ auditor checks a surface directory against the official format contract. The default mode reads only `meta.json` and the TIFF headers; it does not load the image planes. Pixel mode additionally checks real valid vertices against the cached bounding box and samples adjacent-point spacing against `1/scale`.

## Quick start

```bash
python3 scripts/fetch_smoke_patches.py
uv pip install --python .venv/bin/python '.[pixels]'
.venv/bin/python scripts/audit_tifxyz.py --pixels \
  data/PHercParis4/verified_patches/0003_fill_sel_20260512_105100_10 \
  data/PHercParis4/verified_patches/same_wrap000882_growpatch
```

The second patch is a known stale-bbox example and should make the audit exit with status 1. Without `--pixels`, the tool checks only metadata and TIFF dimensions. Pixel mode requires the optional `numpy` and `tifffile` dependencies.

## Checks

- required `meta.json`, `x.tif`, `y.tif`, and `z.tif` files;
- `format=tifxyz`, positive two-component `scale`, valid bbox order;
- coordinate TIFF width/height equality and single-sample planes;
- compatible mask dimensions;
- valid vertices after `Z>0` and optional mask invalidation;
- true vertex bounds versus the recorded bbox;
- a conservative warning when observed neighbor spacing differs from `1/scale` by more than eightfold.

The spacing check is a heuristic because real meshes stretch locally. A warning asks for inspection; it does not prove metadata corruption. The bbox test is direct: it compares actual valid coordinate extrema against recorded bounds with a 1e-3 voxel tolerance.

## Memory and limits

Pixel mode loads coordinate arrays and can use substantial RAM. Its default limit is 20 million grid vertices per patch; larger patches receive a warning and skip the pixel pass. The header-only audit remains available for large assets. A tiled pixel scanner is a future implementation task.

## References

- [Official TIFXYZ format](https://github.com/ScrollPrize/villa/blob/main/lasagna/tifxyz_format.md)
- [Stale Paris 4 bbox issue](https://github.com/ScrollPrize/villa/issues/1272)
- [Scale/flattening issue](https://github.com/ScrollPrize/villa/issues/1379)
