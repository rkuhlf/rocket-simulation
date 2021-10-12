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

import pandas as pd
import numpy as np


import sys
sys.path.append(".")

# Adds one because it is exclusive
max_file_num = 15


output = []


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
    while "Pinf/P" not in lines[0]:
        del lines[0]
    
    chamber_over_exit = float(lines[0].split()[3])
    exit_pressure = chamber_pressure / chamber_over_exit

    while "GAMMAs" not in lines[0]:
        del lines[0]

    gamma = float(lines[0].split()[2])

    while "SON VEL,M/SEC" not in lines[0]:
        del lines[0]

    speed_of_sound = float(lines[0].split()[4])

    while "MACH NUMBER" not in lines[0]:
        del lines[0]

    mach_number = float(lines[0].split()[4])

    exit_velocity = speed_of_sound * mach_number


    while "CF" not in lines[0]:
        del lines[0]

    CF = float(lines[0].split()[2])

    return [chamber_pressure, OF_ratio, exit_pressure, gamma, exit_velocity, CF]

    


for num in range(max_file_num):
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

dataframe = pd.DataFrame(output, columns=["Chamber Pressure [psia]", "O/F Ratio", "Exit Pressure [psia]", "gamma", "Exit Velocity [m/s]", "Thrust Coefficient"])
print(dataframe)

dataframe.to_csv("./Data/Input/CombustionLookup.csv")


