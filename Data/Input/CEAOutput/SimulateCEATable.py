# GENERATE A TABLE OF CEA DATA WITH ROCKET CEA
# Because it is slightly bad to do web-scraping and this should give me more control, I have written a locally operated data gatherer for chemical equilibrium
# However, it still requires installing Fortran, and it is probably a little bit slow to run, so I will still be outputting to a table in the same format

import numpy as np
import pandas as pd
from rocketcea.cea_obj import CEA_Obj, add_new_fuel, add_new_oxidizer, add_new_propellant
import sys
sys.path.append(".")

from Helpers.data import inputs_path


# by default, it has the HTPB and N2O at 76-ish F. This is probably fine for the HTPB, we will see what effect it has to change it
paraffin_nitrous = CEA_Obj(oxName="N2O", fuelName="HTPB")

expansion_ratio = 5.7
pressure_range = np.linspace(14, 1000, 100)
OF_range = np.linspace(0.1, 30, 100)

data = []
for OF in OF_range:
    for chamber_pressure in pressure_range:
        cstar = paraffin_nitrous.get_Cstar(chamber_pressure, OF) * 0.3048 # convert ft to m
        Isp = paraffin_nitrous.estimate_Ambient_Isp(chamber_pressure, OF, expansion_ratio)[0]
        temperature = paraffin_nitrous.get_Temperatures(chamber_pressure, OF, expansion_ratio)[0]
        # I don't think this one needs the expansion ratio
        density = paraffin_nitrous.get_Chamber_Density(chamber_pressure, OF, expansion_ratio)
        molar_mass = paraffin_nitrous.get_Chamber_MolWt_gamma(chamber_pressure, OF, expansion_ratio)[0]
        throat_velocity = paraffin_nitrous.get_SonicVelocities(chamber_pressure, OF, expansion_ratio)[1] * 0.3048 # convert ft to m
        exit_pressure = chamber_pressure / paraffin_nitrous.get_PcOvPe(chamber_pressure, OF, expansion_ratio)
        # Using the gamma average in the nozzle, which isn't perfect but should be closer
        gamma = paraffin_nitrous.get_Throat_MolWt_gamma(chamber_pressure, OF, expansion_ratio)[1]
        gamma += paraffin_nitrous.get_exit_MolWt_gamma(chamber_pressure, OF, expansion_ratio)[1]
        gamma /= 2
        exit_mach = paraffin_nitrous.get_MachNumber(chamber_pressure, OF, expansion_ratio)
        exit_velocity = exit_mach * paraffin_nitrous.get_SonicVelocities(chamber_pressure, OF, expansion_ratio)[2] * 0.3048 # convert ft to m
        coefficient = paraffin_nitrous.get_PambCf(Pc=chamber_pressure, MR=OF, eps=expansion_ratio)[0]

        row = [chamber_pressure, OF, cstar, Isp, temperature, density, molar_mass, throat_velocity, exit_pressure, gamma, exit_velocity, coefficient]
        data.append(row)


data = np.asarray(data)

dataframe = pd.DataFrame(data, columns=["Chamber Pressure [psia]", "O/F Ratio", "C-star [m/s]", "Specific Impulse [s]", "Chamber Temperature [K]", "Chamber Density [kg/m^3]", "Molar Mass [kg/mol]", "Throat Velocity [m/s]", "Exit Pressure [psia]", "gamma", "Exit Velocity [m/s]", "Thrust Coefficient"])

dataframe.to_csv(inputs_path + "/CombustionLookupHTPB.csv")
