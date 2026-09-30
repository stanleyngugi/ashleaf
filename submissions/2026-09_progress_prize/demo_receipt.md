# CPU demo receipt

Run date: 2026-10-01 (Africa/Nairobi; local working tree). Environment: existing Windows .venv-win; Python 3.14.0 and NumPy 2.5.3. Execution was CPU-only. No install or network fetch was needed in this replay because the pinned public metadata and mesh meta files were already present locally.

Command: scripts/plan_framebridge_ranges.py with public group-4 gradient metadata, coordinate index, table, public mesh metadata, and public channel URL, writing artifacts/framebridge/public_demo_plan.json.

Observed output:

    meshes: 1
    occupied_bricks: 10683
    logical_bricks: 11520
    payload_bytes: 350060544
    range_count: 717

The planner verified the sparse index/table inverse and emitted a plan. This run does not fetch the 350 MB planned field payload, inspect the mesh TIFF, establish physical registration, evaluate E1, or produce unwrapped geometry.

## Extracted reviewer ZIP replay

The candidate ZIP was extracted into a temporary clean directory on Windows. A new Python 3.14 virtual environment installed NumPy 2.5.3 and the package with editable install. The documented metadata fetch then downloaded and hash-verified the pinned public metadata/index files (not raw CT/field payload); the planner reproduced the same 10,683 occupied bricks, 11,520 logical bricks, 350,060,544 planned bytes, and 717 ranges. The FB06/FB07 release check, FB15 summary check, and FB16 freeze/source check all passed from the extracted archive. Sixteen required quickstart/evidence paths were checked for presence. This verifies the packaged demo and compact checks, not every full scientific reproduction.

## Final extracted ZIP tests

The final extracted reviewer ZIP also passed seven selected bundled test files covering gate decisions, frame contracts/probes, sparse sampling, release integrity, FB15 truth-blind review, and FB16 graph policy: **31 passed**. These are targeted package checks, not the whole repository test suite.

Compact checks on the same worktree:

- FrameBridge release integrity check: PASS; recomputed 32,878 / 46,318 FB06 held-out agreements (70.9832%) and confirmed the 100% constant-+1 baseline. FB06 is constructed-positive diagnostic evidence, not a winding accuracy claim.
- FB15 frozen-rule summary check: PASS.
- FB16 freeze/source summary check: PASS.
- FB25 local 26-check source/index/checkout verification and unchanged protocol hash: documented in the current state and score audit. No FB25 fit was run in this demo session.
