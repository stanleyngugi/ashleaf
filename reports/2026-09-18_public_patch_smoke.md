# Two Public Paris 4 Patch Smoke Tests

Date: 2026-09-18

Source: public `spiral-input` PHercParis4 `verified_patches` on the [official data server](https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/verified_patches/). `scripts/fetch_smoke_patches.py` pins the SHA-256 of every downloaded file. The data is ignored by Git.

## Results

| Patch | Grid | Valid vertices | Bbox check | Observed adjacent step |
|---|---:|---:|---|---|
| `0003_fill_sel_20260512_105100_10` | 39 × 63 | 2,456 | pass | u 20.05 vox, v 21.84 vox |
| `same_wrap000882_growpatch` | 14 × 55 | 510 | **fail: stale bbox** | u 20.00 vox, v 20.03 vox |

For the known failure, the actual maximum valid Z is 8743.897 vox. The public issue reports its recorded maximum Z as 8409.29 vox, a mismatch of approximately 334.6 slices. Our auditor detects the mismatch on the downloaded public patch.

The positive control matters: the same implementation accepts a small public patch with thousands of valid vertices, so this is not a blanket rejection of Paris 4 data.

## Commands

```bash
python3 scripts/fetch_smoke_patches.py
.venv/bin/python scripts/audit_tifxyz.py --pixels \
  data/PHercParis4/verified_patches/0003_fill_sel_20260512_105100_10
.venv/bin/python scripts/audit_tifxyz.py --pixels \
  data/PHercParis4/verified_patches/same_wrap000882_growpatch
```

The second audit intentionally returns exit code 1.

## Scope

This is a two-patch regression smoke test, not a corpus audit or a new discovery. The stale bbox and scale failure modes were already reported by community contributors. The value here is a small, repeatable preflight that can be placed before benchmarking or fitting.
