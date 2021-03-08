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



# Calculate using http://www.rasaero.com/dl_software_ii.htm
# TODO: figure out a way to simulate this so that it works in 3D
# Probably the theoretical best thing to do is to calculate the drag coefficient of the object rotated so that the relative velocity is only in one dimension. Calculating separate drag coefficients for two components of velocity doesn't make sense, so it is necessary to rotate the shape so that it is at the same angle against a one component velocity, find the consequent drag force, then combine that to the unrotated force
drag_coefficient = 0.75
drag_coefficient_perpendicular = 1.08

vertical_area = np.pi * radius ** 2  # 0.008  # m^2
sideways_area = radius * 2 * height  # 0.4 m^2



# CONSTANTS
time_increment = 0.01  # seconds
earth_mass = 5.972 * 10 ** 24  # kg
earth_radius = 6371071.03  # meters
gravitational_constant = 6.67 * 10 ** -11

# Lake Jackson altitude
base_altitude = 4  # meters









save_preset = True

if save_preset:
    from presets import save_preset

    # Swap this out for an input at some point
    save_as = 'TannerModel'

    save_preset(save_as, globals())


load_preset = False

if load_preset:
    from presets import load_preset

    # Swap this for an input statemetn
    to_load = 'TannerModel'

    load_preset(to_load)




# Calculated variables
# Need to go after any importing prefabs shenanigans
area = np.array([sideways_area, vertical_area])
dist_gravity_pressure = center_of_gravity - center_of_pressure
