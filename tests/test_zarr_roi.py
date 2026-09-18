import unittest

from scroll_lab.zarr_meta import ZarrLevel
from scroll_lab.zarr_roi import plan_roi


class RoiTests(unittest.TestCase):
    def test_crossing_chunk_boundaries_changes_read_cost(self):
        level = ZarrLevel("3", (1024, 1024, 1024), (128, 128, 128), "|u1", (8, 8, 8), 1024**3)
        aligned = plan_roi(level, (0, 0, 0), (256, 256, 256))
        shifted = plan_roi(level, (1, 1, 1), (257, 257, 257))
        self.assertEqual(aligned.touched_chunks, 8)
        self.assertEqual(shifted.touched_chunks, 27)
        self.assertEqual(aligned.estimated_chunk_bytes_upper_bound, 8 * 128**3)

    def test_out_of_bounds_is_rejected(self):
        level = ZarrLevel("0", (10,), (4,), "|u1", (1,), 10)
        with self.assertRaises(ValueError):
            plan_roi(level, (0,), (11,))
