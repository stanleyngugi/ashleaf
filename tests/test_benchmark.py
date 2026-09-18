import unittest

from scroll_lab.benchmark import run_winding_benchmark
from scroll_lab.winding import RelativeConstraint


class BenchmarkTests(unittest.TestCase):
    def test_report_contains_manifest_solver_score_and_provenance(self):
        report = run_winding_benchmark(
            {"assets": [{"id": "a", "kind": "synthetic", "path": "a"}]},
            [RelativeConstraint("a", "b", 1)],
        )
        self.assertEqual(report["benchmark"], "relative-winding-cpu-baseline")
        self.assertEqual(report["manifest"]["asset_count"], 1)
        self.assertIn("score", report)
        self.assertIn("provenance", report)

