**Latest correction, 10:12 UTC:** account 3 (`ulemseewako@gmail.com`) connected a fresh CPU Colab runtime and `drive.mount('/content/drive', force_remount=True, timeout_ms=180000)` completed. The notebook read `MyDrive/Ashleaf/FB25/gpu_runtime_transfer_20260930.json`: `verified_and_persisted`; input archive 2,082,447,360 bytes, SHA-256 `ef5c644388d2730bc284e5d9877caf6b652029757c8b9de3629a298325a23d9b`; code archive 5,475,203 bytes, SHA-256 `9a533f7607ac87b364cef12e61971c2a78f5480c9a908a8424090c276693894c`; all 4,922 patch hashes verified. Account 3's Drive browser search also finds the 6.59 GB pinned-environment archive and its JSON manifest. This reverses the earlier “no current mounted access” status for account 3. The runtime has not yet verified archive bytes from the mounted path, inspected environment manifest contents/disk space, restored inputs, or scored. It is CPU-only; no GPU is allocated. The exact next step is bounded folder/manifest and process-state inspection, then CPU restore only if size/hash/space checks pass.

# FB25 environment recovery and exact scoring qualification

**Latest correction, 10:02 UTC:** Account 2 is signed into the in-built Drive UI as `sngugi.research@gmail.com`; a scoped search opened and read `gpu_runtime_transfer_20260930.json`, which confirms the verified 2,082,447,360-byte input archive, 5,475,203-byte code archive and 4,922 hash-verified patches. This confirms browser Drive access, but not a mounted Colab filesystem. A fresh account-2 CPU runtime accepted the Drive permission prompt and then timed out after five minutes with `ValueError: mount failed`; the CPU runtime was released. Earlier T4 notebook output did show a successful mount and FB25 root listing, but its assumed nested split-manifest path was absent; that output is historical.

The owner CPU host `de61d06ec3e3` was reconnected and checked read-only. `/content/fb25_restore_20260930_v1/restore.json`, `/content/fb25_work/primary`, and the v4 attempt/launcher/operation are absent, and no `fb25_operate_score.py` or fitter process is running. `nvidia-smi` is unavailable on that CPU backend. Owner `google.auth.default()` fell through to a GCE metadata credential endpoint returning 404; a fresh `auth.authenticate_user()` displayed the already-authorized credential prompt, was accepted, then waited for a Colab callback and was interrupted. The owner CPU runtime was released. No baseline score launch, current v4 attempt, or valid held-out report is verified; **no GPU is retained**.

The exact next decision is to recover the already-persisted FB25 archives through a scoped route that works without the failed DriveFS mount or stalled Colab callback. Then restore to local runtime storage, inspect current process/attempt/output evidence, and run the qualified baseline score only if no writer or valid report exists. Do not rerun qualification, reacquire inputs, or change the frozen experiment.

**Latest correction, 09:36 UTC:** no account currently has verified mounted
transfer read/write. On account 2 (`sngugi.research@gmail.com`), the runtime
type selector confirmed CPU. A fresh mount permission was approved and a
force-remount attempt ended with `ValueError: mount failed`; its runtime was
disconnected. On account 3 (`ulemseewako@gmail.com`), the CPU runtime's
`auth.authenticate_user()` waited over a minute for a Colab authorization reply
with no visible prompt or progress; it was interrupted and the runtime released.
The earlier saved account 3 mount success was T4-era historical output, not a
current pass. No GPU is retained.

**Correction, 08:28 UTC:** the compact owner recovery notebook executed
on a temporary CPU runtime, but `drive.mount('/content/drive')` failed with
`ValueError: mount failed`. It therefore did not inspect the v4 attempt or
process table. No score launch is verified, and this is a concrete mounted
Drive access blocker. The runtime is disconnected now; no GPU is retained.
The compact notebook is saved at
`https://colab.research.google.com/drive/1y7DA9zUXAjVuiDTTMSbIekhUZOEdeRoh`.
The next action is to re-establish CPU Drive access (including the already
tested second account if needed), verify the existing attempt before launch,
and only then run the qualified baseline scorer.

**Correction, 08:03–08:04 UTC:** bounded fresh CPU status recovered the
Linux qualification: **passed, exit 0, 1.389 seconds**, on host
`ed329769278b`, pinned Python 3.14.7, NumPy **2.5.1**, SciPy 1.18.0.
The Windows test used NumPy 2.5.2; that earlier version does not describe the
actual qualified scorer. Qualification SHA-256 is
`c6245adcb6f70d19165b94b29dda04a4c84d0aedbb288408e56e2a57280a9dbe`;
adapter `bac559cd53e44916b28240694ee7f95892210138f9850a4ad78b749028e4f1c3`,
fixture `03be032ca3b36f450ac5e8e77e69d0cbf98fcba76ec967abb80712f0ac8bc6a5`,
log `968f1ae8132d51bb66e3f51438921e04dd6e730b2418f519e40259da435f0729`.
The receipt/log/launcher record were copied and verified under
`MyDrive/Ashleaf/FB25/primary/reports/scorer_exact_memory_qualification_20260930_v1`.
Earlier pending-result paragraphs below preserve the recovery chronology.
The bounded status helper is now deployed and executed successfully on CPU.
Browser inventory IDs changed during control resets; recovering the same
in-app browser restored control. Output errors require focused iframe reads.
The original durable staging directory exists, but its `staging_manifest.json`
is **missing**; do not assume external resume provenance is complete.
Baseline v4 is prepared in a new notebook cell and has **not launched yet**.

**08:17 UTC and subsequent browser correction:** owner host `ed329769278b`
freshly reported Drive already mounted, project present and restore receipt
surviving. A `Reconnect T4` action, despite one surviving CPU entry in session
manager, allocated a T4. It was immediately disconnected/deleted, and owner
accelerator preference explicitly changed to CPU. CPU reconnection then
returned the original host and restored files. Release proof is
`artifacts/project_audit_2026-09-30/owner_cpu_preference_and_gpu_released.jpg`.
The original page subsequently crashed before the prepared baseline cell's
launch could be verified. Its candidate local attempt is
`/content/fb25_work/primary/score_recovery_20260930_v4`; inspect this path and
command identity before any relaunch. No valid scientific report was observed.
A compact owner recovery notebook was created at
`https://colab.research.google.com/drive/1y7DA9zUXAjVuiDTTMSbIekhUZOEdeRoh`;
setup ran at 08:28 UTC but failed on Drive mount before checking local state.
No GPU is retained for browser/setup work.

At 09:30 UTC, account 2 was reconnected only after its Change runtime type
dialog showed CPU selected. A focused `force_remount=True` access test triggered
the expected Colab Drive permission prompt, which was approved under the user's
standing instruction. After about two minutes it still raised
`ValueError: mount failed` before reading the transfer manifest or writing the
access probe. The CPU runtime was disconnected. Account 3's current runtime
dialog also showed CPU selected. Its existing credential-refresh cell waited
inside `google.colab.auth.authenticate_user()` for an input reply that never
arrived; the visible output remained at `ACCOUNT3_AUTH_REFRESH`. I interrupted
that cell and disconnected the CPU runtime. Thus neither retry established
usable account access, and no data transfer or score launch took place.

Evidence recorded 2026-09-30, through 07:43 UTC (10:43 Nairobi). This report
supersedes the environment-publication and surviving-local-files statements in
the earlier execution recovery report. It does not establish a scientific win.

## Verified environment and CPU recovery

The environment archive v2 completed at **2026-09-29 22:52:38.171806 UTC**.
Its durable manifest reports `verified_and_persisted`. The archive is
`MyDrive/Ashleaf/FB25/gpu_pinned_environment_20260930.tar.gz`, **6,589,451,779
bytes**, SHA-256
`6fa35f7077cb3382aaa8238cdbc50e8abb0967e17be862b07c9252d99ab51fe8`.
It preserves all three pinned vendor checkouts, their environments, and the
canonical managed Linux Python 3.14.7 runtime. Versionless interpreter aliases
were normalized to equivalent relative canonical targets before packing.

The earlier owner CPU runtime expired. Its local scoring attempts and temporary
files must not be assumed to survive. Durable archives and original runs remain.
A new owner CPU host, `ed329769278b`, mounted the project and restored all three
archives. Restore completed at **07:22:08.394 UTC**, freshly confirmed at 07:32.
The restoration log records 47,445 environment members, 213 code members and
30,839 input members. Fitter imports and all **26 freeze checks passed**.
`/content/fb25_restore_20260930_v1/restore.json` records
`restored_for_preflight`. Restoration is implemented in the separate
`scripts/fb25_restore_runtime.py`; archive boundary tests cover allowed Python
links and rejection of escaping links, special files and duplicate members.

The restored 4,004 fit / 918 heldout patches, original source metadata and four
arms live under `/content/fb25_work/primary/restored_inputs_20260930`.
The unchanged staging script regenerated local dataset roots under
`/content/fb25_work/primary/stage_primary_20260929`. This establishes usable CPU
restoration, not CUDA compatibility or completed fitting. The old code archive
predates later operational fixes; apply the current operational overlay after
restoration and recheck the freeze before running.

The input archive remains 2,082,447,360 bytes, SHA-256
`ef5c644388d2730bc284e5d9877caf6b652029757c8b9de3629a298325a23d9b`.
The code archive remains 5,475,203 bytes, SHA-256
`9a533f7607ac87b364cef12e61971c2a78f5480c9a908a8424090c276693894c`.

## Exact scoring accommodation

Native baseline scoring v3 previously exited -9 without a report. The kill
source is unconfirmed. The new allocation adapter retains the complete input
union, native arithmetic, float64 geometry, int64 faces, native tree and face
order, ties, sample support, metrics and annotation computations. It uses local
disk backing and batches point queries at 128. It changes no frozen vendor file.
The pre-outcome contract is
`protocols/FB25_exact_memory_scoring_amendment_2026-09-30.md`.

The exact parity fixture **passed on Windows** against the pinned Spiralcheck
source with NumPy 2.5.2 and SciPy 1.18.0, in 4.413 seconds. Its checks include
byte-exact geometry arrays, nearest-face choices, winding coordinates, normals,
per-patch and pooled metrics, leakage/unseen calculations and annotation results.
Local evidence is
`artifacts/project_audit_2026-09-30/exact_memory_windows_parity.log`.
The Windows Python version is 3.14.0; this is supplementary evidence, not the
required pinned Linux qualification.

The Linux qualification was launched under the restored pinned Spiralcheck
Python 3.14.7 as PID 9883. Its fresh attempt is
`/content/fb25_work/primary/scorer_exact_memory_qualification_20260930_v1`.
Read `qualification.json` and `parity.log`, and verify their hashes before use.
**Its result has not yet been recovered in this report.** A notebook check was
executed, but browser output retrieval became unresponsive; neither a launch nor
an unread result counts as a pass. The scoring wrapper refuses a missing,
failed or mismatched qualification, test, adapter, log, source pin or runtime.
No valid primary score has been observed.

## Interrupted treatment and accounts

The original FrameBridge seed-17 checkpoint was inspected: schema 2,
**18,000 embedded completed iterations**, SHA-256
`4939532cb1141918e261389b2123a0c858c57160fd6bdd0ae90bd25a54feb110`.
Optimiser, scheduler and RNG recovery fields are present, but the native
headless checkpoint contains **`input_manifest={}`**. The current recovery
wrapper requires its dataset root and will therefore reject this checkpoint.
Do not bypass that check implicitly. The original parent command, recipe,
staging manifest and PCL can be audited for a separate pre-outcome external
provenance accommodation; otherwise rerun the same frozen seed from
initialization. It is still an interrupted fit with no final mesh set.

Account 2 has verified notebook/GPU and editor access, but mounted project
read/write readiness remains unproven. Account 3's fresh current CPU runtime
failed Drive authentication. Its stale CPU session was terminated; a July 2026
CPU runtime was selected and a fresh mount test started at 07:43:18 UTC on
`8fc4005d8a18`. That compatibility test has no recovered outcome yet. Do not
describe editor access or an allocated GPU as end-to-end readiness.

**No GPU is allocated.** The two prior idle T4 sessions were released. Prepare
CPU access, staging, persistence, bounded snapshot storage and a specific fit
queue before allocation. Release any GPU immediately after its assigned work
finishes or blocks. Fifteen-GB secondary-account quotas require a bounded
snapshot plan; do not start several queues with unbounded 1-GB snapshots.

## Next unresolved decision

Recover the baseline's durable inputs on a mounted CPU Colab runtime and inspect
the actual v4 attempt/process before acting; then score the completed 30,000-step
patch-only seed-17 baseline with the qualified adapter. Restore its
local checkpoint and meshes from the surviving durable run, and construct the
4,003-entry score union from the restored full fit split with only the existing
degenerate-patch exclusion. Keep all 918 heldout patches. Use a fresh v4
attempt; old local preflight paths disappeared with the expired runtime.

Complete the seven unfinished primary outcomes with exact frozen recipes,
then obtain all eight provenance-bound reports and apply the original gate.
Replication is conditional. `numeric_export_permitted=false` remains in force.
The verified September deadline is October 1, 2026, **09:59 Nairobi**; the
remaining work must advance this decision rather than reopen closed mechanisms.

## Browser recovery limitation after the observations above

The large owner notebook's status cell returned a visible error, but its output
could not be recovered. Colab separately displayed an output JavaScript loader
error citing expired login access or third-party cookies as possible causes;
these are the page's hypotheses, not a confirmed diagnosis. The host reported
roughly 400 MB free RAM. Browser control then failed even on the smaller account
notebook, reporting failure to load its request-header policy. Reloading and
closing/reopening the large page did not restore reliable control. The original
owner notebook is now reopened as browser tab 6; its backend was not deliberately
terminated. No scientific job was stopped, and no GPU was allocated.

The separate read-only `scripts/fb25_recovery_status.py` prepares a bounded
receipt/log check for recovery. It is implemented locally, **not yet deployed or
executed in Colab**. Qualification result, baseline v4 launch, account mounted
readiness and current CPU process state therefore remain unverified. Recover
browser control and inspect existing evidence before relaunching anything.
