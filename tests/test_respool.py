import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from scroll_lab.respool import (
    RespoolIndex,
    byte_ranges_for_rows,
    coalesce_byte_ranges,
    sampling_roi_from_closed_bounds,
    union_rois,
)


class RespoolTests(unittest.TestCase):
    def test_coalesce_ranges_trades_padding_for_fewer_requests(self):
        exact = byte_ranges_for_rows([1, 2, 5, 9], 8)
        merged = coalesce_byte_ranges(exact, 8, max_gap_rows=2)
        self.assertEqual([(item.row_start, item.row_end) for item in merged], [(1, 5), (9, 9)])
        self.assertEqual(sum(item.length for item in merged), 6 * 8)

    def _fixture(self, directory: Path):
        meta = {
            "format": "respool",
            "version": 2,
            "array_shape": [5, 6, 7],
            "brick_shape": [2, 2, 2],
            "grid_shape": [3, 3, 4],
            "rows": 4,
            "dtype": "u1",
        }
        coords = np.asarray([[-1, -1, -1], [0, 0, 0], [1, 1, 1], [2, 2, 3]], np.int32)
        table = np.zeros((3, 3, 4), np.int32)
        table[0, 0, 0] = 1
        table[1, 1, 1] = 2
        table[2, 2, 3] = 3
        meta_path = directory / "meta.json"
        coords_path = directory / "coords.npy"
        table_path = directory / "table.npy"
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        np.save(coords_path, coords)
        np.save(table_path, table)
        return meta_path, coords_path, table_path

    def test_validates_and_plans_exact_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = RespoolIndex.load(*self._fixture(Path(tmp)))
            plan = index.plan((0, 0, 0), (4, 4, 4))
        self.assertEqual(plan.logical_bricks, 8)
        self.assertEqual(plan.occupied_rows, (1, 2))
        self.assertEqual(plan.payload_bytes, 16)
        self.assertEqual(len(plan.ranges), 1)
        self.assertEqual(plan.ranges[0].to_dict()["http_range"], "bytes=8-23")
        self.assertEqual(plan.absent_zero_bricks, 6)

    def test_nonconsecutive_rows_become_separate_ranges(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = RespoolIndex.load(*self._fixture(Path(tmp)))
            plan = index.plan((0, 0, 0), (5, 6, 7))
        self.assertEqual(plan.occupied_rows, (1, 2, 3))
        self.assertEqual(len(plan.ranges), 1)
        self.assertEqual(plan.ranges[0].byte_start, 8)
        self.assertEqual(plan.ranges[0].byte_end, 31)

    def test_rejects_table_coordinate_disagreement(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._fixture(Path(tmp))
            table = np.load(paths[2])
            table[1, 1, 1] = 3
            table[2, 2, 3] = 2
            np.save(paths[2], table)
            with self.assertRaisesRegex(ValueError, "exact inverses"):
                RespoolIndex.load(*paths)

    def test_sampling_roi_adds_padding_and_halo(self):
        roi = sampling_roi_from_closed_bounds(
            (10.2, 20.0, 30.8),
            (12.0, 25.1, 34.0),
            array_shape=(100, 100, 100),
            padding_zyx=(0.0, 1.5, 1.5),
            interpolation_halo=1,
        )
        self.assertEqual(roi, ((9, 17, 28), (14, 28, 37)))

    def test_sampling_roi_clips_and_union(self):
        first = sampling_roi_from_closed_bounds(
            (0.2, 1.0, 2.0), (4.0, 5.0, 6.0), array_shape=(10, 10, 10)
        )
        second = ((3, 4, 5), (9, 10, 10))
        self.assertEqual(first[0], (0, 0, 1))
        self.assertEqual(union_rois([first, second]), ((0, 0, 1), (9, 10, 10)))


if __name__ == "__main__":
    unittest.main()
