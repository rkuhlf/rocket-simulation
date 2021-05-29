import unittest

import numpy as np
from environment import Environment


class Testing(unittest.TestCase):
    def test_density(self):
        e = Environment()
        # At all levels, the air density should be within about 0.1 for both models
        for i in np.arange(0, 13, 0.1):
            self.assertAlmostEqual(
                e.get_air_density_from_lookup(i),
                e.get_air_density_from_model(i),
                1)
