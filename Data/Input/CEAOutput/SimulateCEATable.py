# GENERATE A TABLE OF CEA DATA WITH ROCKET CEA
# Because it is slightly bad to do web-scraping and this should give me more control, I have written a locally operated data gatherer for chemical equilibrium
# However, it still requires installing Fortran, and it is probably a little bit slow to run, so I will still be outputting to a table in the same format
# If this throws a "ImportError: DLL load failed: %1 is not a valid Win32 application." I can fix it by going into my path and deleting the references to cygwin and MinGW

import numpy as np
from numpy.core import overrides
import pandas as pd
from rocketcea.cea_obj import CEA_Obj, add_new_fuel, add_new_oxidizer, add_new_propellant

import sys
sys.path.append(".")

from Helpers.data import inputs_path
from Data.Input.CEAPropellants import define_ABS_nitrous, define_HTPB_nitrous


# by default, it has the HTPB and N2O at 76-ish F. This is probably fine for the HTPB, we will see what effect it has to change it
# combo_to_sim = CEA_Obj(oxName="N2O", fuelName="HTPB")
# combo_to_sim = define_ABS_nitrous(overrides_units=True)
combo_to_sim = define_HTPB_nitrous(overrides_units=True)


# expansion ratio is from 25 bar to 90,000 Pa based on OpenRocket with correct external atmosphere
expansion_ratio = 4.78
# The input is also taken in bar now
pressure_range = np.linspace(1, 60, 100)
OF_range = np.linspace(0.1, 30, 100)

data = []
for OF in OF_range:

    for chamber_pressure in pressure_range:
        cstar = combo_to_sim.get_Cstar(chamber_pressure, OF)
        Isp = combo_to_sim.estimate_Ambient_Isp(chamber_pressure, OF, expansion_ratio)[0]
        temperature = combo_to_sim.get_Temperatures(chamber_pressure, OF, expansion_ratio)[0]
        # I don't think this one needs the expansion ratio
        density = combo_to_sim.get_Chamber_Density(chamber_pressure, OF, expansion_ratio)
        molar_mass = combo_to_sim.get_Chamber_MolWt_gamma(chamber_pressure, OF, expansion_ratio)[0]
        throat_velocity = combo_to_sim.get_SonicVelocities(chamber_pressure, OF, expansion_ratio)[1]
        exit_pressure = chamber_pressure / combo_to_sim.get_PcOvPe(chamber_pressure, OF, expansion_ratio)
        # Using the gamma average in the nozzle, which isn't perfect but should be closer
        gamma = combo_to_sim.get_Throat_MolWt_gamma(chamber_pressure, OF, expansion_ratio)[1]
        gamma += combo_to_sim.get_exit_MolWt_gamma(chamber_pressure, OF, expansion_ratio)[1]
        gamma /= 2
        exit_mach = combo_to_sim.get_MachNumber(chamber_pressure, OF, expansion_ratio)
        exit_velocity = exit_mach * combo_to_sim.get_SonicVelocities(chamber_pressure, OF, expansion_ratio)[2]
        coefficient = combo_to_sim.get_PambCf(Pc=chamber_pressure, MR=OF, eps=expansion_ratio)[0]

        
        expansion = combo_to_sim.get_PambCf(Pc=chamber_pressure, MR=OF, eps=expansion_ratio)[2]
        separated = expansion.startswith("Separated")
        if separated:
            to_find = "epsSep="
            index = expansion.index(to_find) + len(to_find)
            epsilon_of_separation = float(expansion[index:-1])
            
            exit_velocity = combo_to_sim.get_MachNumber(chamber_pressure, OF, epsilon_of_separation) * combo_to_sim.get_SonicVelocities(chamber_pressure, OF, epsilon_of_separation)[2]


        row = [chamber_pressure, OF, cstar, Isp, temperature, density, molar_mass, throat_velocity, exit_pressure, gamma, exit_velocity, coefficient]
        data.append(row)

    print(f"Simulated O/F of {OF}")

dataframe = pd.DataFrame(data, columns=["Chamber Pressure [bar]", "O/F Ratio", "C-star [m/s]", "Specific Impulse [s]", "Chamber Temperature [K]", "Chamber Density [kg/m^3]", "Molar Mass [g/mol]", "Throat Velocity [m/s]", "Exit Pressure [bar]", "gamma", "Exit Velocity [m/s]", "Thrust Coefficient"])
print(dataframe)
dataframe.to_csv(inputs_path + "/CombustionLookup.csv")
