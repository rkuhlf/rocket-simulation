import Analysis.OpenRocketAnalysis.javaInitialization


from random import choice

import orhelper
from Analysis.OpenRocketAnalysis.CustomMotor import OverrideThrustLookup
from Analysis.OpenRocketAnalysis.openRocketHelpers import apogee
from Analysis.monteCarlo import MonteCarlo
from Analysis.monteCarloFlight import MonteCarloFlight
from net.sf.openrocket.simulation import FlightDataType, SimulationStatus # type: ignore
from net.sf.openrocket.simulation.listeners import SimulationListener # type: ignore
from openRocketHelpers import get_randomized_sim
from orhelper import Helper
from net.sf.openrocket import document # type: ignore
from RocketParts.motor import Motor
import pandas as pd

class MonteCarloFlightOR(MonteCarloFlight):
    def __init__(self, orhelper: Helper, sims=[]):
        self.orhelper = orhelper
        super().__init__(sims=sims)

    def initialize_simulation(self):
        sim = get_randomized_sim(self.orhelper)
        return sim

    def run_simulation(self, sim):
        self.orhelper.run_simulation(sim)

        return sim
    
    def get_total_impulse(self, sim):
        c = sim.getConfiguration()
        m = [m for m in c.motorIterator()][0]
        fcid = c.getFlightConfigurationID()
        m = m.getMotor(fcid)
        return m.getTotalImpulseEstimate()

    def save_simulation(self, sim: document.Simulation):
        MonteCarlo.save_simulation(self, sim)

        self.characteristic_figures.append({
            "Apogee": apogee(sim),
            "Lateral Velocity": sim.getSimulatedData().getDeploymentVelocity(),
            "Total Impulse": self.get_total_impulse(sim),
            "Max Mach": sim.getSimulatedData().getMaxMachNumber(),
            "Max Velocity": sim.getSimulatedData().getMaxVelocity(),
            "Landing Velocity": sim.getSimulatedData().getGroundHitVelocity(),
            "Landing Distance": sim.getSimulatedData().getBranch(0).getLast(FlightDataType.TYPE_POSITION_XY)
        })


        data = {
            "time": sim.getSimulatedData().getBranch(0).get(FlightDataType.TYPE_TIME),
            "altitude": sim.getSimulatedData().getBranch(0).get(FlightDataType.TYPE_ALTITUDE)
        }

        data = pd.DataFrame(data)
        data.set_index("time")

        self.important_data.append(data)

    def finish_simulating(self):
        super().finish_simulating()
        # TODO: create count of tumbling rockets



class MonteCarloFlightRandomMotorOR(MonteCarloFlightOR):
    def __init__(self, orh, motors: 'list[Motor]', sims=[]):
        super().__init__(orh, sims=sims)

        self.motors = motors
        self.selected_motor = motors[0].copy()

    def run_simulation(self, sim):
        # This is a horrible way to do this; motor should be reached through the sim.
        # This means that nothing can be multithreaded
        self.selected_motor = choice(self.motors).copy()
        

        self.orhelper.run_simulation(sim, listeners=[OverrideThrustLookup(self.selected_motor)])
    
    def get_total_impulse(self, sim: document.Simulation):
        return self.selected_motor.total_impulse