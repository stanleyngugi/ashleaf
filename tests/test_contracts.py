import unittest

from scroll_lab.contracts import validate_bbox, validate_shape, validate_spacing


class ContractTests(unittest.TestCase):
    def test_bbox_accepts_points_on_boundary(self):
        issues = validate_bbox(
            [(0, 0, 0), (1, 2, 3)],
            [[0, 0, 0], [1, 2, 3]],
        )
        self.assertEqual(issues, [])

    def test_bbox_reports_stale_extent(self):
        issues = validate_bbox(
            [(0, 0, 0), (1, 2, 9)],
            [[0, 0, 0], [1, 2, 3]],
        )
        self.assertEqual([issue.code for issue in issues], ["point_outside_bbox"])

    def test_bbox_reports_reversed_bounds(self):
        issues = validate_bbox([], [[1, 0, 0], [0, 2, 3]])
        self.assertEqual([issue.code for issue in issues], ["bbox_order"])

    def test_spacing_is_positive(self):
        issues = validate_spacing([0.05, 0.05, 0.08])
        self.assertEqual(issues, [])

    def test_spacing_rejects_zero(self):
        issues = validate_spacing([0.05, 0, 0.08])
        self.assertEqual([issue.code for issue in issues], ["spacing_nonpositive"])

    def test_shape_rejects_empty_and_nonpositive(self):
        self.assertEqual(validate_shape([])[0].code, "shape_empty")
        self.assertEqual(validate_shape([32, 0, 32])[0].code, "shape_nonpositive")


if __name__ == "__main__":
    unittest.main()

