import unittest

from Helpers.general import *
import numpy as np


# TODO: Expand on and implement more unit tests


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

        print(vector_from_angle([0, 0]))
        print(vector_from_angle([np.pi * 3 / 4, np.pi / 4]))
        print(vector_from_angle([0, np.pi / 2]))
        print(vector_from_angle([np.pi / 2, np.pi / 2]))
        print(vector_from_angle([0, np.pi]))

    def test_projection(self):
        print(project(np.array([10., 2., 0]), np.array([1., 0., 0])))

    def test_angle_from_vector(self):
        self.assertTrue(np.alltrue(
            np.isclose(
                angle_from_vector_2d((1, 0)),
                0)))

        self.assertTrue(np.alltrue(
            np.isclose(
                angle_from_vector_2d((0, 1)),
                np.pi / 2)))

        self.assertTrue(np.alltrue(
            np.isclose(
                np.abs(angle_from_vector_2d((-10, 0)) / (np.pi)),
                1)))

        print(180 / np.pi * angles_from_vector_3d((10, 0, 20)))
        print(180 / np.pi * angles_from_vector_3d((10, 1, 20)))
        print(180 / np.pi * angles_from_vector_3d((0, 10, -5)))
        print(180 / np.pi * angles_from_vector_3d((-1, 10, -5)))
        print(180 / np.pi * angles_from_vector_3d((-10, 10, 0)))
        print(180 / np.pi * angles_from_vector_3d((-10, 0, -5)))  # broken
        print(180 / np.pi * angles_from_vector_3d((-10, -10, 0)))
        print(180 / np.pi * angles_from_vector_3d((0, -10, 0)))  # broken
        print(180 / np.pi * angles_from_vector_3d((3, -4, 0)))
        print(180 / np.pi * angles_from_vector_3d((100, -4, 0)))


        # self.assertTrue(np.alltrue(
        #     np.isclose(
        #         np.abs(angles_from_vector_3d((-10, -10, 0))),
        #         (np))))
