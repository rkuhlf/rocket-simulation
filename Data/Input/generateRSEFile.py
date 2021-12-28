# CREATE RSE FILE
# Using thrust, a proportional decrease in mass, and a mass-center-of-gravity lookup
# TODO: move everything into a thrust curves folder, then refactor everything. I would really ike to have some global variables with folder destinations, and I really do not like the sys path . garbage. maybe somthing with project setup in python will do the trick

import pandas as pd

from Helpers.general import interpolate
from Helpers.data import interpolated_lookup
from Data.Input.ThrustProfile import riemann_sum


mass_CG_lookup = pd.read_csv("Data/Input/massCGLookup.csv")

mass_CG_lookup["mass"] *= 1000
max_mass = mass_CG_lookup["mass"][0]
min_mass = mass_CG_lookup["mass"][len(mass_CG_lookup["mass"]) - 1]

thrust_profile = pd.read_csv("Data/Input/finleyThrust.csv")
total_impulse = riemann_sum(thrust_profile["time"], thrust_profile["thrust"])


from xml.dom import minidom

root = minidom.Document()

database = root.createElement('engine-database')
root.appendChild(database)

engineList = root.createElement('engine-list')
database.appendChild(engineList)

motor = root.createElement("engine")
motor.setAttribute("Type", "hybrid")
motor.setAttribute("mfg", "Goddard")
motor.setAttribute("code", "finleyThrustCustomCG")
motor.setAttribute("auto-calc-cg", "0")
motor.setAttribute("auto-calc-mass", "0")
motor.setAttribute("len", "4241")
motor.setAttribute("dia", "171")
motor.setAttribute("initWt", str(max_mass))
motor.setAttribute("propWt", str(max_mass - min_mass))
engineList.appendChild(motor)

data = root.createElement("data")
motor.appendChild(data)

current_total = 0

prev_time = 0
prev_thrust = 0
for i, row in thrust_profile.iterrows():
    current_total += (row["time"] - prev_time) * (row["thrust"] + prev_thrust) / 2

    eng_data = root.createElement("eng-data")
    eng_data.setAttribute("t", str(row["time"]))
    eng_data.setAttribute("f", str(row["thrust"]))
    mass = interpolate(current_total, 0, total_impulse, max_mass, min_mass)
    eng_data.setAttribute("m", str(mass))
    # Convert to mm
    eng_data.setAttribute("cg", str(1000 * interpolated_lookup(mass_CG_lookup, "mass", mass, "CG", safe=True)))

    data.appendChild(eng_data)

    prev_thrust = row["thrust"]
    prev_time = row["time"]

xml_str = root.toprettyxml(indent ="\t")

save_path_file = "Data/Input/finleyThrust.rse"

with open(save_path_file, "w") as f:
	f.write(xml_str)




