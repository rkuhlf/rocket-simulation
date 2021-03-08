import numpy as np


# Orientation
position = np.array([0.0, 0.0], dtype='float64')
velocity = np.array([0.0, 0.0], dtype='float64')
rotation = np.array([1.7444444444444445], dtype='float64')
angular_velocity = np.array([0.0], dtype='float64')


# Rocket Features
radius = 0.05
height = 4
center_of_gravity = 2
center_of_pressure = 0.8
mass = 5.76


# Drag
drag_coefficient = 0.75
drag_coefficient_perpendicular = 1.08
vertical_area = 0.007853981633974483
sideways_area = 0.4


# Miscellaneous
base_altitude = 4
