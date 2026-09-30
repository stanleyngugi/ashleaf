# Reviewer quickstart

Start with [the concise statement](submission_statement.md), [claim ledger](claim_ledger.md), and repository [README](../../README.md). The [HTML demo result](demo_result.html) is an inspectable visual of sparse-index occupancy, not papyrus geometry.

Run the CPU metadata demo from the repository root using the commands in [README](../../README.md). It fetches and verifies small public metadata/index inputs and plans ranges; it does not fetch the planned CT payload or run a fitter. The clean-extraction replay and compact checker results are documented in [demo receipt](demo_receipt.md).

Compact evidence checks:

    python scripts/check_framebridge_release.py --fb06 experiments/results/framebridge_fb06_summary.json --fb07 experiments/results/framebridge_fb07_loso.json
    python scripts/check_fb15_summary.py
    python scripts/check_fb16_summary.py

These checks validate compact tracked summaries and pinned rules, not full raw-data replays. Public challenge raw annotations and field bytes are not bundled; see the [FB08](../../docs/40_fb08_cpu_reproduction.md), [FB14](../../docs/48_fb14_cpu_reproduction.md), [FB15](../../docs/50_fb15_cpu_reproduction.md), and [FB16](../../docs/53_fb16_cpu_reproduction.md) runbooks for complete inputs and commands.

Human annotations, constructed +1 labels, continuity-derived zero cues, and model-field evidence remain distinct. No improved geometry or fitter result is claimed.
