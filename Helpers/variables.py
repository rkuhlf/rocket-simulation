# These are basically the globabl variables that all files need access to


import numpy as np
import pandas as pd

# INITIAL
position = np.array([0, 0], dtype="float64")
velocity = np.array([0, 0], dtype="float64")

# the acceleration isn't even necessary, but I do have to declare the previous value, so I'll just leave it here for clarity
acceleration = np.array([0, 0], dtype="float64")

# indicates whether the rocket has begun to fall
turned = False


mass = 5.76  # kg
t = 0  # seconds


# CONSTANTS
time_increment = 0.01  # seconds
earth_mass = 5.972 * 10 ** 24  # kg
earth_radius = 6371071.03  # meters
gravitational_constant = 6.67 * 10 ** -11

# Lake Jackson altitude
base_altitude = 4  # meters
