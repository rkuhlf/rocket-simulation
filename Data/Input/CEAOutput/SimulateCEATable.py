# GENERATE A TABLE OF CEA DATA WITH ROCKET CEA
# Because it is slightly bad to do web-scraping and this should give me more control, I have written a locally operated data gatherer for chemical equilibrium
# However, it still requires installing Fortran, and it is probably a little bit slow to run, so I will still be outputting to a table in the same format

import numpy as np
from rocketcea.cea_obj import CEA_Obj, add_new_fuel, add_new_oxidizer, add_new_propellant

# by default, it has the HTPB and N2O at 76-ish F. This is probably fine for the HTPB, we will see what effecti it has to change it
paraffin_nitrous = CEA_Obj(oxName="N2O", fuelName="HTPB")


# I am assuming 25 bar = 360 psi. I wish I could do something better, but I don't have any information on how the chamber pressure changes over time
pressure_range = np.linspace(360, 360, 1)

for chamber_pressure in pressure_range:


print(paraffin_nitrous.())



# I need to calculate:
# O/F Ratio,C-star,Specific Impulse [s],Chamber Temperature [K],Chamber Density [kg/m^3],Molar Mass [kg/mol],Throat Velocity [m/s],Exit Pressure [psia],gamma,Exit Velocity [m/s],Thrust Coefficient