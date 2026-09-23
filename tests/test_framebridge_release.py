"""Guard against treating stored FrameBridge summaries as self-verifying scores."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_framebridge_release.py"
spec = importlib.util.spec_from_file_location("check_framebridge_release", SCRIPT)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class FrameBridgeReleaseCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fb06 = json.loads((ROOT / "experiments/results/framebridge_fb06_summary.json").read_text())
        cls.fb07 = json.loads((ROOT / "experiments/results/framebridge_fb07_loso.json").read_text())

    def test_recomputes_tracked_counts_and_aggregates(self) -> None:
        summary = checker.verify_fb06(self.fb06)
        self.assertEqual(summary["exact_hits"], 32878)
        self.assertEqual(summary["pairs"], 46318)
        self.assertEqual(summary["constant_plus_one_baseline_accuracy"], 1.0)
        loso = checker.verify_fb07(self.fb07)
        self.assertEqual(loso["geometry_logistic"]["selected_pairs"], 19897)

    def test_corrupted_prediction_histogram_fails(self) -> None:
        changed = copy.deepcopy(self.fb06)
        changed["meshes"]["20231016151002"]["prediction_histogram"]["1"] += 1
        with self.assertRaisesRegex(ValueError, "histogram"):
            checker.verify_fb06(changed)

    def test_corrupted_fold_aggregate_fails(self) -> None:
        changed = copy.deepcopy(self.fb07)
        changed["aggregate"]["geometry_logistic"]["0.30"]["macro_mean_accuracy"] += 0.01
        with self.assertRaisesRegex(ValueError, "macro_mean_accuracy"):
            checker.verify_fb07(changed)


if __name__ == "__main__":
    unittest.main()
