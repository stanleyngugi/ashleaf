import unittest

from scroll_lab.manifest import audit_manifest_tifxyz, validate_manifest


class ManifestTests(unittest.TestCase):
    def test_valid_manifest(self):
        manifest = {
            "schema_version": 1,
            "assets": [{
                "id": "patch-001",
                "kind": "tifxyz",
                "path": "patch-001",
                "shape": [128, 128, 3],
                "spacing": [0.05, 0.05, 0.08],
                "bbox": [[0, 0, 0], [127, 127, 2]],
            }],
        }
        self.assertEqual(validate_manifest(manifest), [])

    def test_duplicate_ids_and_invalid_shape_are_reported(self):
        manifest = {"assets": [
            {"id": "same", "kind": "tifxyz", "path": "a", "shape": [1, 0, 1]},
            {"id": "same", "kind": "tifxyz", "path": "b"},
        ]}
        codes = [issue.code for issue in validate_manifest(manifest)]
        self.assertEqual(codes, ["shape_nonpositive", "duplicate_asset_id"])

    def test_missing_assets_is_reported(self):
        self.assertEqual(validate_manifest({})[0].code, "assets_missing")

    def test_local_tifxyz_asset_is_audited(self):
        issues = audit_manifest_tifxyz(
            {"assets": [{"id": "missing-patch", "kind": "tifxyz", "path": "absent"}]},
            base_dir="/tmp",
        )
        self.assertEqual(issues[0].code, "not_directory")
