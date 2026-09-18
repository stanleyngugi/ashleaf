import json
import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

from scroll_lab.tifxyz import audit_tifxyz, read_tiff_header


def write_small_tiff(path: Path, width: int, height: int, samples: int = 1) -> None:
    """Write only the classic TIFF IFD needed for header-only audit tests."""
    tags = [(256, width), (257, height), (277, samples)]
    header = b"II" + struct.pack("<HIH", 42, 8, len(tags))
    entries = b"".join(struct.pack("<HHII", tag, 4, 1, value) for tag, value in tags)
    path.write_bytes(header + entries + struct.pack("<I", 0))


class TifxyzTests(unittest.TestCase):
    def test_header_reader(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.tif"
            write_small_tiff(path, 12, 17)
            header = read_tiff_header(path)
            self.assertEqual((header.width, header.height, header.samples_per_pixel), (12, 17, 1))

    def test_audit_detects_mismatched_coordinate_grid(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "meta.json").write_text(json.dumps({"format": "tifxyz", "scale": [0.05, 0.05]}))
            write_small_tiff(folder / "x.tif", 12, 17)
            write_small_tiff(folder / "y.tif", 12, 17)
            write_small_tiff(folder / "z.tif", 12, 18)
            codes = [item.code for item in audit_tifxyz(folder).issues]
            self.assertIn("coordinate_shape_mismatch", codes)

    def test_audit_accepts_consistent_header_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "meta.json").write_text(json.dumps({"format": "tifxyz", "scale": [0.05, 0.05]}))
            for axis in "xyz":
                write_small_tiff(folder / f"{axis}.tif", 12, 17)
            self.assertTrue(audit_tifxyz(folder).ok)

    def test_empty_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "meta.json").write_text("{}")
            for axis in "xyz":
                write_small_tiff(folder / f"{axis}.tif", 12, 17)
            codes = {issue.code for issue in audit_tifxyz(folder).issues}
            self.assertIn("invalid_format", codes)
            self.assertIn("missing_scale", codes)

    @unittest.skipUnless(importlib.util.find_spec("tifffile") and importlib.util.find_spec("numpy"), "pixel extras missing")
    def test_pixel_scan_finds_stale_bbox_and_respects_mask(self):
        import numpy as np
        import tifffile

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "meta.json").write_text(json.dumps({
                "format": "tifxyz", "scale": [0.05, 0.05],
                "bbox": [[0, 0, 1], [2, 2, 3]],
            }))
            tifffile.imwrite(folder / "x.tif", np.array([[0, 1], [2, 100]], dtype="float32"))
            tifffile.imwrite(folder / "y.tif", np.array([[0, 1], [2, 100]], dtype="float32"))
            tifffile.imwrite(folder / "z.tif", np.array([[1, 2], [3, 4]], dtype="float32"))
            tifffile.imwrite(folder / "mask.tif", np.array([[255, 255], [255, 0]], dtype="uint8"))
            audit = audit_tifxyz(folder, scan_pixels=True)
            self.assertTrue(audit.ok)
            self.assertEqual(audit.stats["valid_vertices"], 3)
            (folder / "mask.tif").unlink()
            audit = audit_tifxyz(folder, scan_pixels=True)
            self.assertIn("stale_bbox", [issue.code for issue in audit.issues])

    @unittest.skipUnless(importlib.util.find_spec("tifffile") and importlib.util.find_spec("numpy"), "pixel extras missing")
    def test_pixel_scan_warns_on_reciprocal_scale_error(self):
        import numpy as np
        import tifffile

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "meta.json").write_text(json.dumps({"format": "tifxyz", "scale": [20, 20]}))
            x, y = np.meshgrid(np.arange(4, dtype="float32") * 20, np.arange(4, dtype="float32") * 20)
            tifffile.imwrite(folder / "x.tif", x)
            tifffile.imwrite(folder / "y.tif", y)
            tifffile.imwrite(folder / "z.tif", np.ones((4, 4), dtype="float32"))
            issues = audit_tifxyz(folder, scan_pixels=True).issues
            self.assertIn("scale_spacing_mismatch", [issue.code for issue in issues])
