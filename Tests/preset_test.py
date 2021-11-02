
import unittest
import sys
sys.path.append(".")

from simulation import Simulation
from logger import Logger


class TestingPreset(unittest.TestCase):
    def test_setter_overrides(self):
        logger = Logger({})

        sim = Simulation(logger=logger)

        self.assertEqual(sim.logger, logger)

