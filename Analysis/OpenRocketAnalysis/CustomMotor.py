from RocketParts.motor import Motor
import javaInitialization

import orhelper
from orhelper import AbstractSimulationListener
from Analysis.OpenRocketAnalysis.openRocketHelpers import apogee
from openRocketHelpers import getSimulationByName, most_updated_sim, new_or_instance

from net.sf.openrocket.simulation import SimulationStatus # type: ignore
from Helpers.data import interpolated_lookup


class OverrideThrustLookup(AbstractSimulationListener):
    def __init__(self, motor: Motor):
        self.motor = motor
        super().__init__()
        
    
    def postSimpleThrustCalculation(self, simulationStatus: SimulationStatus, thrust: float) -> float:
        self.motor.environment.time = simulationStatus.getSimulationTime()
        # ! TODO: The CG is very important too. I need that data from the motor sim
        return self.motor.calculate_thrust()



# Sample implementation of a CustomMotor
if __name__ == "__main__":
    with new_or_instance() as instance:
        orh = orhelper.Helper(instance)

        # Load document, run simulation and get data and events
        sim = most_updated_sim(orh)

        # print(sim.getRocket().getID())
        # sim.getRocket().hasMotors()

        m = Motor()
        m.set_thrust_data_path("./Data/Input/ThrustCurves/finleyThrust.csv")
        custom_motor = OverrideThrustLookup(m)
        orh.run_simulation(sim, listeners=[custom_motor])
        # data = orh.get_timeseries(sim, [FlightDataType.TYPE_TIME, FlightDataType.TYPE_ALTITUDE, FlightDataType.TYPE_VELOCITY_Z])
        # events = orh.get_events(sim)

