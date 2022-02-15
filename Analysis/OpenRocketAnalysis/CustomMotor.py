from RocketParts.motor import Motor
import javaInitialization

import orhelper
from orhelper import AbstractSimulationListener
from Analysis.OpenRocketAnalysis.openRocketHelpers import apogee

from openRocketHelpers import getSimulationByName, most_updated_sim, new_or_instance
from Helpers.data import interpolated_lookup

from net.sf.openrocket.simulation import SimulationStatus # type: ignore
# from net.sf.openrocket.masscalc import RigidBody
from net.sf.openrocket.database.motor import ThrustCurveMotorSetDatabase
from net.sf.openrocket.rocketcomponent import FlightConfiguration, MotorMount


class OverrideThrustLookup(AbstractSimulationListener):
    def __init__(self, motor: Motor):
        self.motor = motor
        super().__init__()
        
    
    def postSimpleThrustCalculation(self, simulationStatus: SimulationStatus, thrust: float) -> float:
        self.motor.environment.time = simulationStatus.getSimulationTime()
        # ! TODO: The CG is very important too. I need that data from the motor sim
        # Pass the altitude in here
        return self.motor.calculate_thrust(simulationStatus.getRocketPosition().z)
    
    # def postMassCalculation(self, status: SimulationStatus, mass_data: RigidBody):
    #     pass
    #     return

    # I could create a ThrustCurveMotorSet
    # Then use code very similar to the selectMotor method in the selection panel in the source
    # The getMotors method also looks promising so I can look at stuff I have already loaded in
    # I would have to declare it then
    # Maybe something from the database? findMotors looks good

    # Very odd that setMotorConfiguration is not included in the source code but is available from the debugger
    # Same thing with setConfiguration accepting a Configuration but asking for a FlightConfiguration in the source. Unfortunately, Flight Configuration is also an interface

    # Wonder if maybe it is jpype causing issues


    # Create with d = ThrustCurveMotorSetDatabase()
    # Then add with d.addMotor(ThrustCurveMotors)

    # this.fcid = simulationConditions.getFlightConfigurationID();
    # FlightConfiguration simulationConfig = simulationConditions.getRocket().getFlightConfiguration( this.fcid).clone();
    
    # def startSimulation(self, status):
    #     status.
    #     print(1)
    #     return super().startSimulation(status)


# TODO: Rewrite another option to work with .rse files
# I can probably get the RockSimMotorLoader to work https://github.com/openrocket/openrocket/blob/44e685610317dc4731d58d66891b5f7615a77534/core/src/net/sf/openrocket/file/motor/RockSimMotorLoader.java
# I just need to set the same thing it usually sets
# Try def: startSimulation

# Alright, I think that if I can load all of the motors on the OpenRocketGUI with specific names, then I should be able to set the motor configuration to be that one


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

