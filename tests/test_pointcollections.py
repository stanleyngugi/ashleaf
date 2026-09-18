import unittest

from scroll_lab.pointcollections import audit_pointcollections


class PointCollectionTests(unittest.TestCase):
    def test_mixed_wind_a_is_rejected(self):
        value = {
            "vc_pointcollections_json_version": "1",
            "collections": {"1": {"points": {
                "0": {"p": [1, 2, 3], "wind_a": 0},
                "1": {"p": [2, 3, 4]},
            }}},
        }
        audit = audit_pointcollections(value)
        self.assertIn("mixed_winding_annotation", [issue.code for issue in audit.issues])

    def test_xyz_coordinates_are_checked_against_zyx_shape(self):
        value = {
            "vc_pointcollections_json_version": "1",
            "collections": {"1": {"points": {"0": {"p": [12, 2, 3]}}}},
        }
        audit = audit_pointcollections(value, volume_shape_zyx=(10, 10, 10))
        self.assertIn("position_out_of_bounds", [issue.code for issue in audit.issues])

    def test_null_wind_a_represents_same_winding(self):
        value = {
            "vc_pointcollections_json_version": "1",
            "collections": {"1": {"points": {
                "0": {"p": [1, 2, 3], "wind_a": None},
                "1": {"p": [2, 3, 4], "wind_a": None},
            }}},
        }
        audit = audit_pointcollections(value)
        self.assertTrue(audit.ok)
        self.assertEqual(audit.unannotated_collections, 1)
