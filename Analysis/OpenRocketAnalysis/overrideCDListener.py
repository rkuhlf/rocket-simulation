import pandas as pd
import numpy as np
from orhelper import AbstractSimulationListener
from torch import double
from Helpers.data import interpolated_lookup
from net.sf.openrocket.document import Simulation

from net.sf.openrocket.simulation import SimulationStatus # type: ignore
from net.sf.openrocket.aerodynamics import AerodynamicForces, FlightConditions # type: ignore
from net.sf.openrocket.aerodynamics import BarrowmanCalculator

import java # type: ignore
import jpype

from net.sf.openrocket.util import PolyInterpolator


class OverrideCDConstant(AbstractSimulationListener):
    def __init__(self, sim: Simulation, value: double):
        self.sim = sim
        self.value = value

        # Looks like it is some kind of interpolation with the aoa to increase the drag coefficient smoothly
        # Inputs
        interpolator = PolyInterpolator([[0.0, 0.29670597283903605], [0.0, 0.29670597283903605]])
        # Output multiplier
        self.axialDragPoly1 = interpolator.interpolator([1.0, 1.3, 0.0, 0.0])

        # Inputs
        interpolator = PolyInterpolator([[0.29670597283903605, 1.5707963267948966], [0.29670597283903605, 1.5707963267948966], [1.5707963267948966]])
        # Output multiplier
        self.axialDragPoly2 = interpolator.interpolator([1.3, 0.0, 0.0, 0.0, 0.0])



        super().__init__()
    
    def postFlightConditions(self, status: SimulationStatus, flight_conditions: FlightConditions):
        self.flight_conditions = flight_conditions


    def postAerodynamicCalculation(self, status: SimulationStatus, forces: AerodynamicForces):
        forces = self.override_CD(forces)
        return forces
    
    def override_CD(self, forces):
        forces.setCD(self.value)

        forces.setCaxial(self.calculateAxialDrag(self.flight_conditions, self.value))

        return forces

    def calculateAxialDrag(self, conditions: FlightConditions, cd: double): 
        aoa = min(max(conditions.getAOA(), 0.0), np.pi)

        if (aoa > 1.5707963267948966):
            aoa = np.pi - aoa
        if (aoa < 0.29670597283903605):
            mul = PolyInterpolator.eval(aoa, self.axialDragPoly1)
        else:
            mul = PolyInterpolator.eval(aoa, self.axialDragPoly2)
        
        if conditions.getAOA() < 1.5707963267948966:
            return mul * cd
        
        return -mul * cd
  

# Refactor so that I can pass a function into the base class which will determine the coefficient of drag
# Create a couple of separate constructor functions that make it easier to just pass the function as the argument to the constructor without having to construct, then overwrite the function
class OverrideCDDataFrame(OverrideCDConstant):
    def __init__(self, sim: Simulation, data_frame: pd.DataFrame):
        """Requires that the dataframe have Mach and CD columns"""
        self.data_frame = data_frame

        super().__init__(sim, 0)
    
    def postAerodynamicCalculation(self, status: SimulationStatus, forces: AerodynamicForces):
        mach = self.flight_conditions.getMach()
        self.value = interpolated_lookup(self.data_frame, "Mach", mach, "CD")

        return super().postAerodynamicCalculation(status, forces)