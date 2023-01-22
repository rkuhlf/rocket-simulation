# Do the same monte carlo type randomization of the flight, but also pick a random motor

from Analysis.monteCarloFlight import MonteCarloFlight
from random import choice

from src.rocketparts.motor import Motor

class MonteCarloFlightPickMotor(MonteCarloFlight):
    def __init__(self, motors: 'list[Motor]', sims=[]):
        super().__init__(sims=sims)

        self.motors = motors

    def initialize_simulation(self):
        sim = super().initialize_simulation()
        sim.rocket.motor = choice(self.motors).copy()

        return sim

