import numpy as np


# Orientation
global position
position = np.array([1.0, 0.0], dtype='float64')
global velocity
velocity = np.array([0.0, 0.0], dtype='float64')
global rotation
rotation = np.array([1.7444444444444445], dtype='float64')
global angular_velocity
angular_velocity = np.array([0.0], dtype='float64')


# Rocket Features
global radius
radius = 0.05
global height
height = 4
global center_of_gravity
center_of_gravity = 2
global center_of_pressure
center_of_pressure = 0.8
global mass
mass = 5.76


# Drag
global drag_coefficient
drag_coefficient = 0.75
global drag_coefficient_perpendicular
drag_coefficient_perpendicular = 1.08
global vertical_area
vertical_area = 0.007853981633974483
global sideways_area
sideways_area = 0.4


# Miscellaneous
global base_altitude
base_altitude = 4
