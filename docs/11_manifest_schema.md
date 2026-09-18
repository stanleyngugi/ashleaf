# Benchmark Manifest Schema v1

The manifest is deliberately smaller than any one upstream tool. It is the contract between adapters and benchmark runners.

```json
{
  "schema_version": 1,
  "source": "official-or-community-source",
  "assets": [
    {
      "id": "stable-unique-id",
      "kind": "tifxyz|ome-zarr|mesh|prediction|annotation",
      "path": "local-or-resolved-path",
      "shape": [128, 128, 3],
      "spacing": [0.05, 0.05, 0.08],
      "bbox": [[0, 0, 0], [127, 127, 2]]
    }
  ]
}
```

## Design rules

- `id` is stable and unique within a manifest.
- `kind` describes the asset at the interface, not the tool that produced it.
- `path` is provenance, not proof that the asset exists; adapters may add existence checks.
- `shape`, `spacing`, and `bbox` are optional because not every asset exposes all three, but when present they are validated.
- Coordinate order must be declared by a future adapter. The core validator does not guess whether an upstream tool uses `zyx`, `xyz`, or `uv`.
- The schema never stores credentials or signed URLs.

## Why this exists

The current ecosystem contains many specialized tools. A common manifest makes their outputs comparable while preserving tool-specific metadata in sidecar files. It also lets us validate cheap invariants before expensive fitting or GPU inference.

