import unittest

import numpy as np

from scroll_lab.ray_support import conservative_line_bricks, e1_multiray_bricks, rows_for_bricks


class RaySupportTests(unittest.TestCase):
    def test_line_crossing_multiple_axes_cannot_skip_corner_brick(self):
        bricks = conservative_line_bricks(
            (31.5, 31.5, 4.0),
            (33.0, 33.0, 4.0),
            brick_shape_zyx=(32, 32, 32),
            grid_shape_zyx=(3, 3, 3),
            interpolation_halo_voxels=0,
            max_step_voxels=8,
        )
        self.assertTrue({(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0)}.issubset(bricks))

    def test_interpolation_halo_reaches_neighbor(self):
        bricks = conservative_line_bricks(
            (10.0, 31.5, 10.0),
            (11.0, 31.5, 10.0),
            brick_shape_zyx=(32, 32, 32),
            grid_shape_zyx=(2, 2, 2),
        )
        self.assertIn((0, 0, 0), bricks)
        self.assertIn((0, 1, 0), bricks)

    def test_multiray_reports_partial_boundary_support(self):
        bricks, valid = e1_multiray_bricks(
            (1.0, 1.0, 1.0),
            (8.0, 1.0, 1.0),
            array_shape_zyx=(16, 16, 16),
            brick_shape_zyx=(4, 4, 4),
            grid_shape_zyx=(4, 4, 4),
            lasagna_scale=1.0,
            max_offset_working_voxels=2.0,
            m_rays=3,
        )
        self.assertEqual(valid, 2)
        self.assertTrue(bricks)

    def test_rows_omit_zero_and_deduplicate(self):
        table = np.zeros((2, 2, 2), dtype=np.int32)
        table[0, 0, 0] = 4
        table[1, 1, 1] = 9
        rows = rows_for_bricks(table, [(0, 0, 0), (0, 0, 1), (1, 1, 1), (1, 1, 1)])
        self.assertEqual(rows, (4, 9))


if __name__ == "__main__":
    unittest.main()
