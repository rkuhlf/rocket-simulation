# These are basically the globabl variables that all files need access to


import numpy as np
import pandas as pd

# INITIAL
position = np.array([0, 0], dtype="float64")
velocity = np.array([0, 0], dtype="float64")

# the acceleration isn't even necessary, but I do have to declare the previous value, so I'll just leave it here for clarity
acceleration = np.array([0, 0], dtype="float64")

# Using Euler X, Y, Z angles instead of quaternions because I am not a psychopath
# Only need one dimension of rotation for two dimensions of position
# When third dimension is added change it to three - this may cause some hard angle problems converting directional velocities to angular velocities in three dimensions
# start with a ten degree tilt (90 degrees is straight up)
rotation = np.array([100 * 3.14 / 180], dtype="float64")
angular_velocity = np.array([0], dtype="float64")

# the acceleration isn't even necessary, but I do have to declare the previous value, so I'll just leave it here for clarity
angular_acceleration = np.array([0], dtype="float64")

# indicates whether the rocket has begun to fall
turned = False


mass = 5.76  # kg
t = 0  # seconds

radius = 0.05  # meters
height = 4  # meters
center_of_gravity = 2  # meters from the bottom
center_of_pressure = 0.8  # meters from the bottom
dist_gravity_pressure = center_of_gravity - center_of_pressure

# Actually this sucks and is complicated because moment of inertia isn't a scalar quantity for a complex 3d shape
# use calculated value from Fusion 360/Other CAD, currently using random one
moment_of_inertia = 1 / 12 * mass * height ** 2



# CONSTANTS
time_increment = 0.01  # seconds
earth_mass = 5.972 * 10 ** 24  # kg
earth_radius = 6371071.03  # meters
gravitational_constant = 6.67 * 10 ** -11

# Lake Jackson altitude
base_altitude = 4  # meters
