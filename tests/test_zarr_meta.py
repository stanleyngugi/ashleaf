import json
import tempfile
import unittest
from pathlib import Path

from scroll_lab.zarr_meta import audit_omezarr_v2


class ZarrMetadataTests(unittest.TestCase):
    def test_valid_two_level_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".zgroup").write_text(json.dumps({"zarr_format": 2}))
            (root / ".zattrs").write_text(json.dumps({"multiscales": [{
                "axes": [{"name": "z"}, {"name": "y"}, {"name": "x"}],
                "datasets": [
                    {"path": "0", "coordinateTransformations": [{"type": "scale", "scale": [1, 1, 1]}]},
                    {"path": "1", "coordinateTransformations": [{"type": "scale", "scale": [2, 2, 2]}]},
                ],
            }]}))
            for name, shape in (("0", [8, 10, 12]), ("1", [4, 5, 6])):
                (root / name).mkdir()
                (root / name / ".zarray").write_text(json.dumps({
                    "shape": shape, "chunks": [4, 4, 4], "dtype": "|u1", "zarr_format": 2,
                }))
            audit = audit_omezarr_v2(root)
            self.assertTrue(audit.ok)
            self.assertEqual(audit.axes, ("z", "y", "x"))
            self.assertEqual(audit.levels[0].estimated_uncompressed_bytes, 960)

    def test_missing_level_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".zgroup").write_text(json.dumps({"zarr_format": 2}))
            (root / ".zattrs").write_text(json.dumps({"multiscales": [{
                "axes": [{"name": "z"}],
                "datasets": [{"path": "0", "coordinateTransformations": [{"type": "scale", "scale": [1]}]}],
            }]}))
            self.assertIn("invalid_level", [issue.code for issue in audit_omezarr_v2(root).issues])
