import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_fb15_review_queue.py"
SPEC = importlib.util.spec_from_file_location("export_fb15_review_queue", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


class FB15ReviewQueueTests(unittest.TestCase):
    def test_truth_blind_whitelist_and_reason_codes(self):
        rows = [
            {"id": "wrong", "collection_id": "1", "e1_predicted_dw": 2,
             "e1_confidence": 0.9, "sdt_crest_magnitude": 3,
             "sdt_ray_counts": [3] * 7, "truth_dw": 3,
             "e1_signed_exact": False, "sdt_magnitude_exact": True},
            {"id": "agree", "collection_id": "1", "e1_predicted_dw": 1,
             "e1_confidence": 0.8, "sdt_crest_magnitude": 1,
             "sdt_ray_counts": [1] * 7, "truth_dw": 1},
        ]
        queue = module.build_queue(rows)
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["reason"], "SDT_MAGNITUDE_DISAGREEMENT")
        self.assertEqual(queue[0]["review_priority_rank"], 1)
        self.assertFalse(queue[0]["numeric_export_permitted"])
        self.assertFalse(any("truth" in key or "exact" in key for key in queue[0]))

    def test_rank_uses_confidence_not_known_truth(self):
        def row(identifier, confidence):
            return {"id": identifier, "collection_id": "1", "e1_predicted_dw": 2,
                    "e1_confidence": confidence, "sdt_crest_magnitude": 1,
                    "sdt_ray_counts": [1] * 7, "truth_dw": 99}
        queue = module.build_queue([row("low", 0.8), row("high", 0.95)])
        self.assertEqual([item["id"] for item in queue], ["high", "low"])


if __name__ == "__main__":
    unittest.main()
