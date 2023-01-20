# CALCULATE THE CG OF THE PROPULSION OVER THE BURN
# The ox tank is already calculated in a separate file, and I am just going to run the fuel grain as decreasing in mass perfectly proportional to ox
# In the thrust curve, this mass loss will be made proportional to thrust



from Visualization.OxTankCG import run_simulation
from rocketparts.massObject import MassObject
from helpers.general import interpolate



masses, mass_vap, ullages, centers, temperatures, pressures = run_simulation()

ox_tank_offset = 1.6891 # m
ox_tank_initial_mass = masses[0]

ox_tank_mass_object = MassObject(mass=masses[0], center_of_gravity=centers[0] + ox_tank_offset)

fuel_grain_initial_mass = 12 # kg
fuel_grain_final_mass = 4 # kg
# 214.5 in
fuel_grain = MassObject(mass=fuel_grain_initial_mass, center_of_gravity=5.4483)

# Assuming no mass change of the ablative
# Use the distance from the center to the top of the nose cone
# 194.75 inches from start
precombustion_ablative = MassObject(mass=0.609, center_of_gravity=4.94665)
# 236 inches from start
precombustion_ablative = MassObject(mass=1.218, center_of_gravity=5.9944)


propulsion_mass_object = MassObject(mass_objects=[ox_tank_mass_object, precombustion_ablative, fuel_grain, precombustion_ablative])

used_masses = []
total_centers = []

for i, mass in enumerate(masses):
    if mass <= 0:
        break
    

    ox_tank_mass_object.mass = mass
    ox_tank_mass_object.center_of_gravity = centers[i] + ox_tank_offset

    fuel_grain.mass = interpolate(mass, ox_tank_initial_mass, 0, fuel_grain_initial_mass, fuel_grain_final_mass)

    # I actually need the motor center of gravity relative to itself because that is how rse files work
    total_centers.append(propulsion_mass_object.total_CG - ox_tank_offset)
    used_masses.append(propulsion_mass_object.total_mass)


# import matplotlib.pyplot as plt

# plt.plot(used_masses, total_centers)
# plt.gca().invert_xaxis()
# plt.gca().invert_yaxis()

# plt.show()


import numpy as np
import pandas as pd

# It is easiest to implement into the .rse file if I can just look up the CG from the mass. I can calculate the mass from the thrust.
df = pd.DataFrame(data=np.asarray([used_masses, total_centers]).transpose())

df.to_csv("Data/Input/massCGLookup.csv")