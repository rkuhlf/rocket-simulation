import numpy as np
from random import choice

import orhelper
from Analysis.OpenRocketAnalysis.CustomMotor import OverrideThrustLookup
from Analysis.OpenRocketAnalysis.openRockethelpers import apogee
from Analysis.OpenRocketAnalysis.overrideAerodynamicsListener import OverrideAerodynamicsDataFrame
from Analysis.monteCarlo import MonteCarlo
from Analysis.monteCarloFlight import MonteCarloFlight
from helpers.data import interpolated_lookup
from net.sf.openrocket.simulation import FlightDataType, SimulationStatus # type: ignore
from net.sf.openrocket.simulation.listeners import SimulationListener # type: ignore
from openRockethelpers import get_randomized_sim
from orhelper import Helper
from net.sf.openrocket import document # type: ignore
from rocketparts.motor import Motor
import pandas as pd
from net.sf.openrocket.simulation.exception import MotorIgnitionException # type: ignore


class MonteCarloFlightOR(MonteCarloFlight):
    def __init__(self, orhelper: Helper, sims=[], drag_dataframe=None):
        """If the drag_dataframe is None, it will use OpenRocket's prediction"""
        self.orhelper = orhelper
        self.drag_dataframe = drag_dataframe
        self.drag_dataframe = self.drag_dataframe[self.drag_dataframe["Alpha"] == 0]
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


    def store_data(self, sim):
        data = {
            "time": sim.getSimulatedData().getBranch(0).get(FlightDataType.TYPE_TIME),
            "altitude": sim.getSimulatedData().getBranch(0).get(FlightDataType.TYPE_ALTITUDE),
            "velocity": sim.getSimulatedData().getBranch(0).get(FlightDataType.TYPE_VELOCITY_TOTAL),
            "mach": sim.getSimulatedData().getBranch(0).get(FlightDataType.TYPE_MACH_NUMBER),
            "acceleration": sim.getSimulatedData().getBranch(0).get(FlightDataType.TYPE_ACCELERATION_TOTAL),
            "drag": sim.getSimulatedData().getBranch(0).get(FlightDataType.TYPE_DRAG_FORCE),
            "thrust": sim.getSimulatedData().getBranch(0).get(FlightDataType.TYPE_THRUST_FORCE),
            "CP": sim.getSimulatedData().getBranch(0).get(FlightDataType.TYPE_CP_LOCATION),
            "CG": sim.getSimulatedData().getBranch(0).get(FlightDataType.TYPE_CG_LOCATION)
        }

        return data


    def save_simulation(self, sim: document.Simulation):
        MonteCarlo.save_simulation(self, sim)

        self.characteristic_figures.append({
            "Apogee": apogee(sim),
            "Lateral Velocity": sim.getSimulatedData().getDeploymentVelocity(),
            "Total Impulse": self.get_total_impulse(sim),
            "Max Mach": sim.getSimulatedData().getMaxMachNumber(),
            "Max Velocity": sim.getSimulatedData().getMaxVelocity(),
            "Landing Velocity": sim.getSimulatedData().getGroundHitVelocity(),
            "Landing Distance": sim.getSimulatedData().getBranch(0).getLast(FlightDataType.TYPE_POSITION_XY),
            "Mean Wind Speed": sim.getOptions().getWindSpeedAverage(),
            "Wind Speed Deviation": sim.getOptions().getWindSpeedDeviation()
        })

        data = self.store_data(sim)
        
        if self.drag_dataframe is not None:
            CPs = self.lookup_CP_custom_data(data["mach"])
            data["RASAero CP"] = CPs

        data = pd.DataFrame(data)
        data.set_index("time")

        self.important_data.append(data)
    
    def lookup_CP_custom_data(self, mach_numbers):
        CPs = []

        for mach in mach_numbers:
            # Convert inches to meters
            CPs.append(interpolated_lookup(self.drag_dataframe, "Mach", mach, "CP", safe=True) * 0.0254)
        
        return CPs

    def finish_simulating(self):
        # TODO: create count of tumbling rockets
        super().finish_simulating()
    
    def handle_failed_sim(self, sim, e):
        super().handle_failed_sim(sim, e)

        if isinstance(e, MotorIgnitionException):
            # You may want to try restarting OpenRocket to make sure that your motors are actually defined.
            # The debugger will also tell you which motors were loaded
            print("It appears that the OpenRocket simulation does not have a motor. I think anything that ignites at t=0 should work with the rest of the code. Simply add a motor to the default configuration in the file.")
        



class MonteCarloFlightRandomMotorOR(MonteCarloFlightOR):
    def __init__(self, orh, motors: 'list[Motor]', sims=[], drag_dataframe=None, dry_mass=None, dry_CG=None, ox_tank_front=None):
        super().__init__(orh, sims=sims, drag_dataframe=drag_dataframe)

        self.ox_tank_front = ox_tank_front
        self.dry_mass = dry_mass
        self.dry_CG = dry_CG

        self.motors = motors
        self.selected_motor = motors[0].copy()

    def run_simulation(self, sim):
        # This is a horrible way to do this; motor should be reached through the sim.
        # This means that nothing can be multithreaded
        self.selected_motor = choice(self.motors).copy()
        self.selected_motor.adjust_for_atmospheric = True
        self.selected_motor.nozzle_area = np.pi * 0.0516382 ** 2 # m^2
        
        listeners = [OverrideThrustLookup(self.selected_motor)]
        listeners.append(OverrideAerodynamicsDataFrame(sim, self.drag_dataframe))
        self.orhelper.run_simulation(sim, listeners=listeners)
    
    def get_total_impulse(self, sim: document.Simulation):
        return self.selected_motor.total_impulse
    
    def store_data(self, sim):
        data = super().store_data(sim)

        
        data["custom CG"] = self.lookup_CG_custom_data(data["time"])

        return data
    
    def lookup_CG_custom_data(self, times):
        CGs = []

        for time in times:
            propellant_CG = interpolated_lookup(self.selected_motor.thrust_data, "time", time, "propellant_CG", safe=True) + self.ox_tank_front
            propellant_mass = interpolated_lookup(self.selected_motor.thrust_data, "time", time, "propellant_mass", safe=True)

            CGs.append((self.dry_mass * self.dry_CG + propellant_mass * propellant_CG) / (self.dry_mass + propellant_mass))
        
        return CGs