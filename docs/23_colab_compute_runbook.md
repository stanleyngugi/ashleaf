# Colab Compute Runbook

Colab is the project’s GPU execution environment. As of 2026-09-22, an authenticated notebook is open in the built-in browser, but it is not connected to a runtime and no GPU job has been started. The current FrameBridge investigation should remain CPU-first until its coordinate and parity gates pass.

## What belongs on Colab

- bounded GPU parity checks;
- small ROI spiral-fit experiments;
- GPU-only current-`villa` tests;
- learned winding-evidence probes after CPU baselines exist;
- short profiler runs and memory scaling measurements.

Do not use a transient notebook as the only location for code, results, or decisions. Do not begin with a full-scroll volume or the official multi-GPU autoresearch schedule.

## Reproducible session contract

Every GPU run records:

- notebook URL/id and a committed export or script entry point;
- repository URL and exact commit;
- upstream `villa`/external-project commits;
- Python, CUDA, driver, PyTorch, GPU model, VRAM, RAM, and disk;
- data URLs, logical array/group, levels, hashes/ETags where available;
- coordinate-frame contract;
- random seeds and deterministic flags;
- command/config, start/end time, peak allocated/reserved VRAM, host RAM, and disk use;
- stdout/stderr log plus result manifest uploaded before runtime disconnect.

Secrets must be entered through Colab/Drive secret storage or an interactive prompt, never committed or printed.

## Session bootstrap

Use a fresh checkout rather than copying untracked notebook cells into the project:

```bash
!nvidia-smi
!git clone https://github.com/stanleyngugi/ashleaf.git /content/ashleaf
%cd /content/ashleaf
!git checkout <EXACT_COMMIT>
!python -m pip install -e '.[pixels]'
!PYTHONPATH=src python -m unittest discover -s tests -q
```

The Ashleaf repository is public, so no credential is required for the clone. Prefer a plain immutable commit checkout. For any separate private data or repository, use an authorized credential flow that does not expose a token in notebook output.

## Storage policy

```text
/content/                 ephemeral code, caches, bounded downloaded ROIs
/content/drive/.../runs/  manifests, logs, summaries, plots, checkpoints worth keeping
Git repository            source, tests, small fixtures, documentation—not CT volumes
```

Before a long run, calculate expected download, decompressed working set, checkpoint size, and output size. Keep at least 20% VRAM and 20% local disk headroom. Use chunked Zarr reads and a bounded ROI; never mount or download terabytes “just in case.”

## GPU gate ladder

1. `nvidia-smi` and a one-tensor CUDA allocation.
2. Repository unit tests on the Colab Python environment.
3. CPU/GPU parity on a synthetic fixture.
4. CPU/GPU parity on a tiny public ROI.
5. A 10–100 step smoke run with memory telemetry.
6. Checkpoint-save/reload/resume test.
7. Only then a bounded research run.

If any gate fails, save logs and stop. Repeatedly extending runtime is not a substitute for understanding the failure.

## FrameBridge-specific use

The baseline frame transform, overlap report, and E1 mesh score should run on CPU. Colab becomes relevant only if the required gradient-field slabs are inconvenient locally or if we progress to a bounded fitter integration. Even then:

- run the bounds-only probe before downloading array chunks;
- compute the exact required z slabs from transformed pair endpoints plus margin;
- log bytes requested/read and array group;
- cache only those slabs;
- copy summary JSON/CSV and manifests to durable storage immediately.

## Spiral fitting caution

Current official code warns that `normal_zarr_group` and `lasagna_scale` can be silently mismatched, and the official autoresearch notes assume considerably more parallel compute than a normal Colab instance. Before any fit:

- snapshot the effective inputs and config;
- verify every Zarr multiscale transform;
- record which input sources and losses are structurally active;
- estimate point/patch-linking and dense-field memory;
- start with a small z window;
- use an existing 12 GB-compatible path where appropriate rather than rediscovering it;
- reserve an untouched evaluation region.

## End-of-session checklist

- Stop the run cleanly and flush logs.
- Copy manifests, metrics, stderr/stdout, plots, and checkpoints to durable storage.
- Verify file sizes and hashes after the copy.
- Update the local experiment registry with outcome and artifact location.
- Disconnect the runtime when finished.
- Convert notebook-only reasoning into repository documentation or scripts.

The notebook is compute, not memory. This repository remains the source of truth.
