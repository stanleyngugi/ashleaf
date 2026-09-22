import unittest

from scroll_lab.frames import (
    Bounds3D,
    FrameSpec,
    FrameTransform,
    bounds_from_points,
    physical_axis_interval,
    physical_axis_overlap,
    physical_overlap,
)


class FrameSpecTests(unittest.TestCase):
    def test_identity_and_roundtrip(self):
        frame = FrameSpec("same", ("x", "y", "z"), (2.4, 2.4, 2.4))
        transform = FrameTransform.between(frame, frame)
        point = (11.25, 20.5, -2.0)
        self.assertEqual(transform.apply_point(point), point)
        self.assertLessEqual(transform.max_roundtrip_error([point]), 1e-12)

    def test_paris4_mesh_to_annotation_is_quarter_scale(self):
        mesh = FrameSpec("mesh-2.4um", ("x", "y", "z"), (2.4, 2.4, 2.4))
        annotation = FrameSpec("annotation-l2-9.6um", ("x", "y", "z"), (9.6, 9.6, 9.6))
        transform = FrameTransform.between(mesh, annotation)
        self.assertEqual(transform.apply_point((400.0, 800.0, 1200.0)), (100.0, 200.0, 300.0))
        self.assertLessEqual(transform.max_roundtrip_error([(400.0, 800.0, 1200.0)]), 1e-12)

    def test_axis_permutation_and_anisotropy(self):
        array = FrameSpec("array", ("z", "y", "x"), (4.0, 3.0, 2.0), (10.0, 20.0, 30.0))
        physical = FrameSpec("physical", ("x", "y", "z"), (1.0, 1.0, 1.0))
        transform = FrameTransform.between(array, physical)
        self.assertEqual(transform.apply_point((5.0, 7.0, 11.0)), (32.0, 41.0, 50.0))

    def test_general_affine_translation(self):
        source = FrameSpec(
            "affine", ("x", "y", "z"), (1.0, 1.0, 1.0),
            affine_voxel_to_um_xyz=(
                (2.0, 0.0, 0.0, 5.0),
                (0.0, 3.0, 0.0, 7.0),
                (0.0, 0.0, 4.0, 11.0),
                (0.0, 0.0, 0.0, 1.0),
            ),
        )
        physical = FrameSpec("physical", ("x", "y", "z"), (1.0, 1.0, 1.0))
        self.assertEqual(FrameTransform.between(source, physical).apply_point((1, 2, 3)), (7.0, 13.0, 23.0))

    def test_center_corner_mismatch_fails_loudly(self):
        centers = FrameSpec("centers", ("x", "y", "z"), (1, 1, 1), sample_semantics="voxel_center")
        corners = FrameSpec("corners", ("x", "y", "z"), (1, 1, 1), sample_semantics="voxel_corner")
        with self.assertRaisesRegex(ValueError, "sample semantics differ"):
            FrameTransform.between(centers, corners)

    def test_schema_is_strict_and_roundtrips(self):
        frame = FrameSpec("a", ("x", "z", "y"), (2, 4, 3), source="fixture")
        self.assertEqual(FrameSpec.from_dict(frame.to_dict()), frame)
        with self.assertRaisesRegex(ValueError, "unknown frame fields"):
            FrameSpec.from_dict({**frame.to_dict(), "lasagna_scale": 4})


class BoundsTests(unittest.TestCase):
    def test_bounds_transform_checks_all_corners(self):
        source = FrameSpec(
            "sheared", ("x", "y", "z"), (1, 1, 1),
            affine_voxel_to_um_xyz=(
                (1.0, 1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0, 0.0),
                (0.0, 0.0, 1.0, 0.0),
                (0.0, 0.0, 0.0, 1.0),
            ),
        )
        physical = FrameSpec("physical", ("x", "y", "z"), (1, 1, 1))
        result = FrameTransform.between(source, physical).apply_bounds(Bounds3D((0, 0, 0), (2, 3, 4)))
        self.assertEqual(result, Bounds3D((0, 0, 0), (5, 3, 4)))

    def test_bounds_from_points_and_overlap(self):
        bounds = bounds_from_points([(5, 4, 3), (1, 8, 2), (4, 0, 9)])
        self.assertEqual(bounds, Bounds3D((1, 0, 2), (5, 8, 9)))
        fine = FrameSpec("fine", ("x", "y", "z"), (2.4, 2.4, 2.4))
        coarse = FrameSpec("coarse", ("x", "y", "z"), (9.6, 9.6, 9.6))
        report = physical_overlap(
            fine, Bounds3D((0, 0, 100), (100, 100, 500)),
            coarse, Bounds3D((0, 0, 50), (50, 50, 200)),
        )
        self.assertTrue(report["overlap"])
        self.assertEqual(report["overlap_bounds_um_xyz"]["lower"][2], 480.0)

    def test_wrong_frame_reproduces_false_no_overlap(self):
        mesh = Bounds3D((0, 0, 29420), (1, 1, 73889))
        field = Bounds3D((0, 0, 6527), (1, 1, 17253))
        wrongly_same = FrameSpec("wrongly-same", ("x", "y", "z"), (9.6, 9.6, 9.6))
        annotation = FrameSpec("annotation", ("x", "y", "z"), (9.6, 9.6, 9.6))
        wrong = physical_overlap(wrongly_same, mesh, annotation, field)
        self.assertFalse(wrong["overlap"])

        mesh_2p4 = FrameSpec("mesh-2.4", ("x", "y", "z"), (2.4, 2.4, 2.4))
        corrected = physical_overlap(mesh_2p4, mesh, annotation, field)
        self.assertTrue(corrected["overlap"])
        self.assertEqual(corrected["overlap_bounds_um_xyz"]["lower"][2], 70608.0)
        self.assertEqual(corrected["overlap_bounds_um_xyz"]["upper"][2], 165628.8)

    def test_z_only_overlap_does_not_invent_xy_bounds(self):
        mesh = FrameSpec("mesh", ("x", "y", "z"), (2.4, 2.4, 2.4))
        annotation = FrameSpec("annotation", ("x", "y", "z"), (9.6, 9.6, 9.6))
        result = physical_axis_overlap(
            mesh, (29420, 73889), annotation, (6527, 17253), canonical_axis="z"
        )
        self.assertTrue(result["overlap"])
        self.assertEqual(result["overlap_interval_um"], [70608.0, 165628.8])
        self.assertAlmostEqual(result["overlap_extent_um"], 95020.8)

    def test_axis_interval_rejects_coupled_affine(self):
        sheared = FrameSpec(
            "sheared", ("x", "y", "z"), (1, 1, 1),
            affine_voxel_to_um_xyz=(
                (1.0, 0.0, 0.0, 0.0),
                (0.0, 1.0, 0.0, 0.0),
                (1.0, 0.0, 1.0, 0.0),
                (0.0, 0.0, 0.0, 1.0),
            ),
        )
        with self.assertRaisesRegex(ValueError, "full bounds are required"):
            physical_axis_interval(sheared, "z", (0, 10))


if __name__ == "__main__":
    unittest.main()
