# Old plan of overriding the CP and CG is temporarily put on hold
# To get it working correctly, I would have to recalculate the CAxial for every single component
# And I would have to recalculate local centers of pressure
# The only real way to get a global override working is to calculate one global torque myself. I do not even know if this is correct
# --- New Plan ---
# Will just graph the CP and override CG alongside the OpenRocket ones
# It would be better to figure out how to load a .rse engine


import pandas as pd
import numpy as np
from orhelper import AbstractSimulationListener
from helpers.data import interpolated_lookup
from net.sf.openrocket.document import Simulation # type: ignore

from net.sf.openrocket.simulation import SimulationStatus # type: ignore
from net.sf.openrocket.aerodynamics import AerodynamicForces, FlightConditions # type: ignore
from net.sf.openrocket.aerodynamics import BarrowmanCalculator # type: ignore

import java # type: ignore
import jpype

from net.sf.openrocket.util import Coordinate, PolyInterpolator # type: ignore


class OverrideAerodynamicsConstant(AbstractSimulationListener):
    def __init__(self, sim: Simulation, CD: float, CP: float, override_CD=True, override_CP=True):
        self.sim = sim
        self.CD = CD
        self.CP = CP

        self.CD_is_overriden = override_CD
        self.CP_is_overriden = override_CP

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
    
    def override_CD(self, forces: AerodynamicForces):
        # It has to be in https://github.com/openrocket/openrocket/blob/44e685610317dc4731d58d66891b5f7615a77534/core/src/net/sf/openrocket/aerodynamics/BarrowmanCalculator.java That is the only place where getCP is used
        # Uses CAxial, Cm, and Cyaw. Cm appears to be pitch
        # Might have to use conditions.getPitchCenter().x
        # Below the axial coefficient calculation, there is some stuff about CP: https://github.com/openrocket/openrocket/blob/44e685610317dc4731d58d66891b5f7615a77534/core/src/net/sf/openrocket/aerodynamics/BarrowmanCalculator.java#L186
        # I think we have to do some kind of override of https://github.com/openrocket/openrocket/blob/44e685610317dc4731d58d66891b5f7615a77534/core/src/net/sf/openrocket/aerodynamics/BarrowmanCalculator.java#L197
        # That is the only place that getCP is used
        if self.CP_is_overriden:
            # print(forces.getCP())
            # Basically overriding the Barrowman calculator methods of OpenRocket

            # There is also a weight option here that appears to be changing; probably important
            # CP_coord = forces.getCP()
            # CP_coord = CP_coord.setX(self.CP)
            # forces.setCP(CP_coord)
            # print(forces.getCP())
            
            # TODO: probably have to override CSide or something
            pass

        if self.CD_is_overriden:
            # This is not necessary to setCAxial, but it is good practice to keep everything correct
            forces.setCD(self.CD)

            forces.setCaxial(self.calculateAxialDrag(self.flight_conditions, self.CD))

        return forces

    def calculateAxialDrag(self, conditions: FlightConditions, cd: float): 
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
class OverrideAerodynamicsDataFrame(OverrideAerodynamicsConstant):
    def __init__(self, sim: Simulation, data_frame: pd.DataFrame, override_CD=True, override_CP=True):
        """Requires that the dataframe have Mach and CD/CP columns"""
        self.data_frame = data_frame

        super().__init__(sim, 0, 0, override_CD=override_CD, override_CP=override_CP)
    
    def postAerodynamicCalculation(self, status: SimulationStatus, forces: AerodynamicForces):
        try:
            mach = self.flight_conditions.getMach()
            # This line is throwing the error
            self.CD = interpolated_lookup(self.data_frame, "Mach", mach, "CD", safe=True)
            # self.CP = 15

            return super().postAerodynamicCalculation(status, forces)
        except IndexError as e:
            print("Error in aerodynamics listener")