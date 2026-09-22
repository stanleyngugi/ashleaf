import json
import tempfile
import unittest
from pathlib import Path

from scroll_lab.frame_probe import run_frame_probe


class FrameProbeTests(unittest.TestCase):
    def test_measures_pointcollections_and_checks_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            points = {
                "collections": {
                    "a": {"points": {
                        "0": {"p": [1, 2, 10]},
                        "1": {"p": [4, 8, 20]},
                    }}
                }
            }
            (root / "points.json").write_text(json.dumps(points), encoding="utf-8")
            frame = {
                "name": "coarse", "axis_order": ["x", "y", "z"],
                "voxel_size_um": [4, 4, 4],
            }
            raw = {
                "schema_version": 1,
                "frames": {"f": frame},
                "artifacts": [
                    {"id": "points", "frame": "f", "pointcollections": ["points.json"]},
                    {"id": "band", "frame": "f", "axis_intervals": {"z": [21, 30]}},
                ],
                "comparisons": [
                    {"id": "no", "a": "points", "b": "band", "axis": "z", "expected_overlap": False}
                ],
            }
            result = run_frame_probe(raw, manifest_dir=root)
            self.assertTrue(result["all_expectations_met"])
            self.assertEqual(result["artifacts"][0]["point_count"], 2)
            self.assertEqual(result["artifacts"][0]["axis_intervals_native"]["z"], [10.0, 20.0])
            self.assertEqual(len(result["artifacts"][0]["sources"][0]["sha256"]), 64)

    def test_rejects_path_escape(self):
        raw = {
            "schema_version": 1,
            "frames": {"f": {"name": "f", "axis_order": ["x", "y", "z"], "voxel_size_um": [1, 1, 1]}},
            "artifacts": [{"id": "p", "frame": "f", "pointcollections": ["../outside.json"]}],
            "comparisons": [{"id": "x", "a": "p", "b": "p", "axis": "z"}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "escapes base_dir"):
                run_frame_probe(raw, manifest_dir=tmp)

    def test_reads_umbilicus_tifxyz_and_array_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "umb.json").write_text(json.dumps({
                "control_points": [
                    {"x": 2, "y": 3, "z": 4}, {"x": 8, "y": 9, "z": 10}
                ]
            }), encoding="utf-8")
            (root / "mesh.json").write_text(json.dumps({
                "bbox": [[1, 2, 3], [12, 13, 14]]
            }), encoding="utf-8")
            (root / "array.json").write_text(json.dumps({
                "format": "respool", "array_shape": [20, 30, 40]
            }), encoding="utf-8")
            raw = {
                "schema_version": 1,
                "frames": {
                    "xyz": {"name": "xyz", "axis_order": ["x", "y", "z"], "voxel_size_um": [1, 1, 1]},
                    "zyx": {"name": "zyx", "axis_order": ["z", "y", "x"], "voxel_size_um": [1, 1, 1]},
                },
                "artifacts": [
                    {"id": "umb", "frame": "xyz", "umbilicus_json": "umb.json"},
                    {"id": "mesh", "frame": "xyz", "tifxyz_metadata": ["mesh.json"]},
                    {"id": "array", "frame": "zyx", "array_metadata": "array.json"},
                ],
                "comparisons": [
                    {"id": "mesh-array", "a": "mesh", "b": "array", "mode": "bounds3d", "expected_overlap": True}
                ],
            }
            result = run_frame_probe(raw, manifest_dir=root)
            by_id = {item["id"]: item for item in result["artifacts"]}
            self.assertEqual(by_id["umb"]["axis_intervals_native"]["z"], [4.0, 10.0])
            self.assertEqual(by_id["mesh"]["axis_intervals_native"]["x"], [1.0, 12.0])
            self.assertEqual(by_id["array"]["axis_intervals_native"]["z"], [0.0, 19.0])
            self.assertTrue(result["comparisons"][0]["overlap"])


if __name__ == "__main__":
    unittest.main()
