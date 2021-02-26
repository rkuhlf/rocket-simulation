import numpy as np
import pandas as pd

# INITIAL
position = np.array([0, 0], dtype="float64")
p_position = np.copy(position)
velocity = np.array([0, 0], dtype="float64")
p_velocity = np.copy(velocity)
acceleration = np.array([0, 0], dtype="float64")
p_acceleration = np.copy(acceleration)

mass = 5.76  # kg
t = 0  # seconds


# CONSTANTS
time_increment = 0.01 # seconds
earth_mass = 5.972 * 10 ** 24 # kg
earth_radius = 6371071.03 # meters
gravitational_constant = 6.67 * 10 ** -11

# Lake Jackson altitude
base_altitude = 4  # meters
