import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from scroll_lab.fit_window import preflight_fit_window


class FitWindowTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("tifffile") and importlib.util.find_spec("numpy"), "pixel extras missing")
    def test_real_vertices_can_be_inside_when_cached_bbox_says_outside(self):
        import numpy as np
        import tifffile

        with tempfile.TemporaryDirectory() as tmp:
            patch = Path(tmp) / "patch"
            patch.mkdir()
            (patch / "meta.json").write_text(json.dumps({
                "format": "tifxyz", "scale": [1, 1], "bbox": [[0, 0, 1], [1, 1, 3]],
            }))
            for axis in "xy":
                tifffile.imwrite(patch / f"{axis}.tif", np.ones((2, 2), dtype="float32"))
            tifffile.imwrite(patch / "z.tif", np.array([[1, 2], [3, 9]], dtype="float32"))
            result = preflight_fit_window([patch], z0=8, z1=10, scan_pixels=True)
            self.assertEqual(result.metadata_candidate_patches, 0)
            self.assertEqual(result.actual_active_patches, 1)
            self.assertEqual(result.false_negative_metadata_patches, 1)

    def test_invalid_window_is_rejected(self):
        with self.assertRaises(ValueError):
            preflight_fit_window([], z0=10, z1=10)

    @unittest.skipUnless(importlib.util.find_spec("tifffile") and importlib.util.find_spec("numpy"), "pixel extras missing")
    def test_empty_patch_is_known_inactive(self):
        import numpy as np
        import tifffile

        with tempfile.TemporaryDirectory() as tmp:
            patch = Path(tmp) / "patch"
            patch.mkdir()
            (patch / "meta.json").write_text(json.dumps({
                "format": "tifxyz", "scale": [1, 1], "bbox": [[0, 0, 1], [1, 1, 3]],
            }))
            for axis in "xy":
                tifffile.imwrite(patch / f"{axis}.tif", np.ones((2, 2), dtype="float32"))
            tifffile.imwrite(patch / "z.tif", np.zeros((2, 2), dtype="float32"))
            result = preflight_fit_window([patch], z0=8, z1=10, scan_pixels=True)
            self.assertEqual(result.actual_active_patches, 0)
            self.assertEqual(result.unknown_patches, 0)
            self.assertEqual(result.patches[0].actual_vertices_inside, 0)
