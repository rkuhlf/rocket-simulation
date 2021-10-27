# ANALYZE THE EFFECTS OF DIFFERENT BODY DIAMETERS
# Assuming a constant speed profile, we can calculate the importance of coefficient of drag at each mach number.



# To be honest, this is too much of an oversimplification.
# If I would try to calculate using approximations like a constant wall thickness and the volume remaining the same, I don't see why it wouldn't be the minimum possible
# I can't really account for bending moments, which would probably be the main limiter
'''
import numpy as np

from Helpers.general import cylindrical_length


# We will assume that the rocket is a hollow cylinder with flat heads in order to calculate the length
# Based on a rocket diameter of 8 inches and a total length of 252 inches -> 12666.9016 in^3


# The lower limit for diameter is 6 inches for the parachutes
# We need to see if the lower limit for the buckling forces is higher than six inches
possible_diameters = np.array([7, 8, 9])
lengths = []

total_volume = 12667

for d in possible_diameters:
    lengths.append(cylindrical_length(total_volume, d / 2))

print(lengths)

'''



# Realistically, the only way to do this is to create a function to optimize a rocket (Monte Carlo sims in a different file)
# Then supply the diameter of the rocket as a constant and have everything else be optimized.
# This is still insanely hard, I would have to have a very good method for determining the required length.

# For this kind of thing, I am going to start by saying we can look at 6 inch, 7 inch, and 8 inch. We can look in between those later, but I should narrow it down to two first.


# Try to set better physical limitations
# Limit the ox tank to under 10 feet: hopefully that will provide a solid lower boundary
# The fuel grain should have some limitations as well. If we have a maximum flux of 500 kg/m^2-s, what does that give us