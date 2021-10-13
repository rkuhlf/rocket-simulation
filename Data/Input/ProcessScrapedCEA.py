# Out of all of this data, there are a few things that I need
# Given an input chamber pressure and an input O/F ratio (and an input nozzle; just the expansion ratio)

# I need to find the *exit pressure*
# In addition, I would like to output the *ratio of specific heats* (gamma)
# By the way, Gammas are going to be totally weird. I guess the gamma changes as a function of heat, which means that it changes as it expands, which means that it is different at the throat and the exit.
# I am just going to use the original one for now, at the throat
# That should be all that I need

# However, I would also like to output the *exit velocity*, if only because I would like to compare the CEA values to the values I have been getting
# It should be pretty simple to do with a rearrangement of the thrust equation
# And I would like to output the *CF*; I believe CEA assumes atmospheric conditions

# Turns out I also need the molecular weight (MW) for the ideal gas law in CC. Actually, I just need the density of the chamber. and the *c-star* value, since that is in fact the main point of the calculation
# Also I need the velocity at the throat

import pandas as pd
import numpy as np


import sys
sys.path.append(".")

# Adds one because it is exclusive
max_file_num = 15


output = []

def process_CEA_float(string):
    # account for the minus sign making it scientific notation
    if "-" in string:
        split = string.split("-")
        base = float(split[0])
        exponent = float(split[1])
        return base * 10 ** exponent
    
    return float(string)

def read_cea_lines(lines):
    chamber_pressure = float(lines[0].split()[2])

    while "O/F= " not in lines[0]:
        del lines[0]

    OF_ratio = float(lines[0].split()[1])

    # If we don't get to exit conditions, we can't do anything
    while len(lines) > 0 and "EXIT" not in lines[0]:
        del lines[0]

    if len(lines) == 0:
        return

    # We go through all of the things we need and return them
    # Bruh they literally did this for me and I ignored it
    while "Pinf/P" not in lines[0]:
        del lines[0]
    
    chamber_over_exit = process_CEA_float(lines[0].split()[3])
    exit_pressure = chamber_pressure / chamber_over_exit

    # while "T, K" not in lines[0]:
    #     del lines[0]

    # throat_temperature = process_CEA_float(lines[0].split()[3])

    while "RHO" not in lines[0]:
        del lines[0]

    density = process_CEA_float(lines[0].split()[3])

    while "GAMMAs" not in lines[0]:
        del lines[0]

    gamma = process_CEA_float(lines[0].split()[2])

    while "SON VEL,M/SEC" not in lines[0]:
        del lines[0]

    throat_velocity = process_CEA_float(lines[0].split()[3])
    speed_of_sound = process_CEA_float(lines[0].split()[4])

    while "MACH NUMBER" not in lines[0]:
        del lines[0]

    mach_number = process_CEA_float(lines[0].split()[4])

    exit_velocity = speed_of_sound * mach_number

    while "CSTAR" not in lines[0]:
        del lines[0]

    cstar = process_CEA_float(lines[0].split()[2])

    while "CF" not in lines[0]:
        del lines[0]

    CF = process_CEA_float(lines[0].split()[2])

    while "Isp" not in lines[0]:
        del lines[0]

    specific_impulse = process_CEA_float(lines[0].split()[3]) / 9.81

    return [chamber_pressure, OF_ratio, cstar, specific_impulse, density, throat_velocity, exit_pressure, gamma, exit_velocity, CF]

    


for num in range(max_file_num):
    print("EXTRACTING FROM FILE", num)
    f = open("Data/Input/CEAOutput/" + str(num))
    lines = f.readlines()

    while "supar" not in lines[0]:
        del lines[0]

    expansion_ratio = float(lines[0].split()[1])

    while "Pin = " not in lines[0]:
        del lines[0]
    

    while len(lines) > 0:
        cea_run = [lines[0]]
        del lines[0]
        while len(lines) > 0 and "Pin = " not in lines[0]:
            cea_run.append(lines[0])
            del lines[0]

        data = read_cea_lines(cea_run)
        if data is not None:
            output.append(data)




    f.close()


output = np.asarray(output)

print(output)

dataframe = pd.DataFrame(output, columns=["Chamber Pressure [psia]", "O/F Ratio", "C-star", "Specific Impulse [s]", "Chamber Density [kg/m^3]", "Throat Velocity [m/s]", "Exit Pressure [psia]", "gamma", "Exit Velocity [m/s]", "Thrust Coefficient"])

dataframe = dataframe.sort_values(["O/F Ratio", "Chamber Pressure [psia]"])

print(dataframe)


dataframe.to_csv("./Data/Input/CombustionLookup.csv")


