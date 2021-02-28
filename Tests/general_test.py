import unittest

from Helpers.general import *
import numpy as np



class Testing(unittest.TestCase):
    def test_interpolate(self):
        self.assertEqual(interpolate(-1, -2, 0, 0, 100), 50)

    def test_numpy_from_string(self):
        self.assertTrue(np.alltrue(numpy_from_string("[  0.    0. ]") ==
                                   np.array([0, 0])))

    def test_euler_to_vector(self):
        # pi / 2 should go to x: 0, y: 1
        self.assertTrue(np.alltrue(
            np.isclose(
                euler_to_vector_2d(np.pi / 2),
                np.array([0, 1]))))

        self.assertTrue(np.alltrue(
            np.isclose(
                euler_to_vector_2d(np.pi / 4),
                np.array([2 ** 0.5 / 2, 2 ** 0.5 / 2]))))

        self.assertTrue(np.alltrue(
            np.isclose(
                euler_to_vector_2d(np.pi),
                np.array([-1, 0]))))

        self.assertTrue(np.alltrue(
            np.isclose(
                euler_to_vector_2d(-np.pi / 2),
                np.array([0, -1]))))
