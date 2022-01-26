import numpy as np
from orhelper import AbstractSimulationListener
from torch import double
from net.sf.openrocket.document import Simulation

from net.sf.openrocket.simulation import SimulationStatus # type: ignore
from net.sf.openrocket.aerodynamics import AerodynamicForces, FlightConditions # type: ignore
from net.sf.openrocket.aerodynamics import BarrowmanCalculator

import java # type: ignore
import jpype


class OverrideCDConstant(AbstractSimulationListener):
    def __init__(self, sim: Simulation, value):
        self.sim = sim
        self.value = value
        super().__init__()

    def  postAerodynamicCalculation(self, status: SimulationStatus, forces: AerodynamicForces):
        forces.setCD(self.value)
        conditions = status.getSimulationConditions()
        calc = conditions.getAerodynamicCalculator()

        # Make the method public
        target_type = jpype.JArray(java.lang.Class)
        # Cast a list to that type
        parameters = target_type([FlightConditions, jpype.JDouble])
        # Look up the method using the created signature
        method = calc.getClass().getDeclaredMethod("calculateAxialDrag", parameters)

        method.setAccessible(True)
        
        # The flight conditions can be accessed from the stepper, so I just need to find the stepper

        # It needs flight conditions, not the simulation conditions
        axial = method.invoke(calc, [, self.value])

        forces.setCaxial(axial)
        return super().postAerodynamicCalculation(status, forces)
    

    # def calculateAxialDrag(conditions: FlightConditions, cd: double):   
    #     aoa = MathUtil.clamp(conditions.getAOA(), 0.0, np.pi)

    #     if (aoa > 1.5707963267948966):
    #         aoa = Math.PI - aoa
    #     if (aoa < 0.29670597283903605):
    #         mul = PolyInterpolator.eval(aoa, axialDragPoly1)
    #     else:
    #         mul = PolyInterpolator.eval(aoa, axialDragPoly2)
        
    #     if conditions.getAOA() < 1.5707963267948966:
    #         return mul * cd
        
    #     return -mul * cd
  

    