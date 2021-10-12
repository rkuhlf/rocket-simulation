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



import sys
sys.path.append(".")

# Adds one because it is exclusive
max_file_num = 1




def read_cea_lines(lines):
    chamber_pressure = float(lines[0].split()[2])
    print(chamber_pressure)

    while "O/F= " not in lines[0]:
        del lines[0]

    OF_ratio = float(lines[0].split()[1])
    print(OF_ratio)

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
    print("Mach number", mach_number)

    exit_velocity = speed_of_sound * mach_number

    print(exit_velocity)





    


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

        read_cea_lines(cea_run)




    f.close()