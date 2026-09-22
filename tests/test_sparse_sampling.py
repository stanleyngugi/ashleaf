import unittest

import numpy as np

from scroll_lab.sparse_sampling import SparseRespoolSampler


class _Index:
    array_shape = (5, 6, 7)
    brick_shape = (2, 2, 2)
    grid_shape = (3, 3, 4)
    brick_voxels = 8
    rows = 37

    def __init__(self):
        self.table = np.arange(36, dtype=np.int32).reshape(self.grid_shape) + 1


class SparseSamplingTests(unittest.TestCase):
    def _sampler(self):
        index = _Index()
        dense = np.arange(np.prod(index.array_shape), dtype=np.uint8).reshape(index.array_shape)
        pool = np.zeros((index.rows, index.brick_voxels), dtype=np.uint8)
        for bz in range(index.grid_shape[0]):
            for by in range(index.grid_shape[1]):
                for bx in range(index.grid_shape[2]):
                    block = np.zeros(index.brick_shape, dtype=np.uint8)
                    z0, y0, x0 = bz * 2, by * 2, bx * 2
                    source = dense[z0 : z0 + 2, y0 : y0 + 2, x0 : x0 + 2]
                    block[: source.shape[0], : source.shape[1], : source.shape[2]] = source
                    pool[index.table[bz, by, bx]] = block.ravel()
        remap = np.arange(index.rows, dtype=np.int32)
        return dense, SparseRespoolSampler(index, pool, remap)

    def test_integer_and_trilinear_samples_match_dense_formula(self):
        dense, sampler = self._sampler()
        points = np.asarray([[0, 0, 0], [4, 5, 6], [1.25, 2.5, 3.75]], dtype=float)
        got = sampler.sample(points)
        expected_last = 0.0
        p = points[-1]
        lo = np.floor(p).astype(int)
        frac = p - lo
        for dz in (0, 1):
            for dy in (0, 1):
                for dx in (0, 1):
                    idx = np.minimum(lo + [dz, dy, dx], np.asarray(dense.shape) - 1)
                    weights = np.where([dz, dy, dx], frac, 1 - frac)
                    expected_last += dense[tuple(idx)] * np.prod(weights)
        np.testing.assert_allclose(got, [dense[0, 0, 0], dense[4, 5, 6], expected_last])

    def test_missing_occupied_row_fails_loudly(self):
        _, sampler = self._sampler()
        sampler.row_remap[sampler.index.table[0, 0, 0]] = 0
        with self.assertRaisesRegex(RuntimeError, "absent from the acquisition"):
            sampler.sample(np.asarray([[0.0, 0.0, 0.0]]))

    def test_out_of_bounds_rejected(self):
        _, sampler = self._sampler()
        with self.assertRaises(IndexError):
            sampler.sample(np.asarray([[-0.1, 0.0, 0.0]]))

    def test_matches_scipy_map_coordinates_order_one(self):
        try:
            from scipy.ndimage import map_coordinates
        except ImportError:
            self.skipTest("SciPy is optional; manual trilinear parity is tested above")

        dense, sampler = self._sampler()
        rng = np.random.default_rng(7)
        points = rng.random((200, 3)) * (np.asarray(dense.shape) - 1)
        expected = map_coordinates(dense, points.T, order=1, mode="nearest")
        np.testing.assert_array_equal(sampler.sample(points, quantize_uint8=True), expected)


if __name__ == "__main__":
    unittest.main()
