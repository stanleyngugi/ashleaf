# VC3D Winding Point Collections

The spiral fitter consumes VC3D point-collection JSON. The current public Paris 4 `spiral-input` bundle contains `same_windings.json`, `relative_windings.json`, and `abs_winding.json`.

## Reproduce the schema audit

```bash
python3 scripts/fetch_spiral_annotations.py
python3 scripts/audit_pointcollections.py \
  data/PHercParis4/same_windings.json \
  data/PHercParis4/relative_windings.json \
  data/PHercParis4/abs_winding.json
```

The fetcher pins SHA-256 hashes; files remain under ignored `data/`.

## Observed public files, 2026-09-18

| File | Collections | Nonempty collections | Points | Audit |
|---|---:|---:|---:|---|
| same | 154 | 125 | 5,413 | pass |
| relative | 300 | 254 | 2,173 | pass |
| absolute | 6 | 5 | 59 | pass |

The public same-winding file serializes `wind_a: null` on its points. The adapter treats null as unannotated, matching the meaning of a same-winding collection. Relative and absolute files use numeric `wind_a` values. Empty collections are counted but are not considered a failure.

The auditor checks version, collection and point structure, finite `[x, y, z]` coordinates, homogeneous presence of numeric winding values, and optional bounds against a declared full-resolution `zyx` volume shape. It does not infer that a relative collection's `wind_a` values are globally absolute; their gauge is local to the annotation context.

## Evaluation rule

Internal agreement among a generator's own constraints is not external accuracy. The independent [`constraint-gauge` benchmark](https://github.com/pscamillo/constraint-gauge) demonstrates how large that gap can be on a public Paris 4 slice and adds coverage, density, confidence calibration, and provenance gates. Our CPU BFS score is an engineering diagnostic only. Any research claim about winding quality must use human annotations or held-out geometry, and should compare under the established benchmark where possible.
