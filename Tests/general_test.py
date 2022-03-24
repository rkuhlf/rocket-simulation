# TESTS FOR THE GENERAL HELPERS
# You don't really need to run these over and over again, this is just the file where I was making sure that all of the math I copied down and worked out is correct


import unittest

from Helpers.general import *
import numpy as np


# TODO: Expand on and implement more unit tests

# TODO: Write tests for all of the major files to make sure everything runs before I commit anything


class TestGeneralHelpers(unittest.TestCase):
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
        self.assertTrue(np.all(
            project(np.array([10., 2., 0]), np.array([1., 0., 0])) == \
                np.array([10, 0, 0])))

        # Hopefully, this corresponds to theta_around = 4.7 and theta_down = 0.2
        print(project(np.array([0, 0.1, 1]), np.array([0., 0., -1])))
        # Hopefully, this corresponds to theta_around = 1.5 and theta_down = 0.2
        print(project(np.array([0, -0.1, 1]), np.array([0., 0., -1])))

        # Then we do the first one minus the result to get the direction of lift
        # So I think the projection part is correct, since I am getting the correct signs depending on inclinations
        
    def test_vector_from_angle(self):
        # This is 1.5 around and 0.2 down -> should be a positive y and a positive z
        print(vector_from_angle([np.pi/2, 0.2]))

        # This is 1.5 around and 2.8 down
        print(vector_from_angle([np.pi/2, 2.8]))

        # This is 4.7 around and 2.8 down
        print(vector_from_angle([3*np.pi/2, 2.8]))

        # This is 4.7 around and 2.8 down
        print(vector_from_angle([3*np.pi/2, 0.2]))

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

    def test_helix_length(self):
        self.assertAlmostEqual(47.504, helical_length(6, 3, 2.5), 2)

    def test_helix_area(self):
        # Do not really need too much accuracy for these regression things
        self.assertAlmostEqual(148.648, helical_area(6, 3, 2.5, 0.5), -1)