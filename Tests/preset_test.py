
import unittest


from simulation import Simulation
from Logging.logger import Logger


class TestingPreset(unittest.TestCase):
    def test_setter_overrides(self):
        logger = Logger({})

        sim = Simulation(logger=logger)

        self.assertEqual(sim.logger, logger)

