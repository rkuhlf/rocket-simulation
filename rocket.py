# TODO: account for change in mass due to fuel
# TODO: account for slow acceleration with fuel
# TODO: add parachute logic
# When the velocity flips
# Change drag coefficient
# Change area
# TODO: account better for drift
# Account for air resistance of rocket shape
# Account for gravity decreasing as you leave the atmosphere
# TODO: three degree of freedom - in x, y, and z modelling 
# Model rotation in x, y, and z

import numpy as np
import pandas as pd

# INITIAL
position = np.array([0, 0], dtype="float64")
p_position = np.copy(position)
velocity = np.array([0, 0], dtype="float64")
p_velocity = np.copy(velocity)
acceleration = np.array([0, 0], dtype="float64")
p_acceleration = np.copy(acceleration)

# 5.76 kg
mass = 5.76 # kg
t = 0 # seconds


# CONSTANTS
time_increment = 0.01
earth_mass = 5.972 * 10 ** 24 
earth_radius = 6371071.03
gravitational_constant = 6.67 * 10 ** -11
base_altitude = 4 # meters

# Thrust
# https://www.thrustcurve.org/motors/Hypertek/1685CCRGL-L550/
propellant_mass = 1552 / 1000 # in kg
mass += propellant_mass
thrust_data = pd.read_csv("thrustCurve.csv")
total_thrust = 0 # 3,094.7
# this is close but not exactly correct (actually it's exactly what the data indicates, but not the experimental value) - I changed it to better match the experimental
for index, row in thrust_data.iterrows():
  if index == 0:
    continue

  p_row = thrust_data.iloc[index - 1]
  change_in_time = row["time"] - p_row["time"]
  average_thrust = (row["thrust"] + p_row["thrust"]) / 2
  total_thrust += change_in_time * average_thrust

# print(total_thrust)

mass_per_thrust = propellant_mass / total_thrust


def interpolate(current_time, start_time, end_time, start_thrust, end_thrust):
  # map the data linearly between the two
  return (current_time - start_time) / (end_time - start_time) * (end_thrust - start_thrust) + start_thrust

finished_thrusting = False
def get_thrust(current_time):
  global finished_thrusting

  if finished_thrusting:
    return 0
  # this isn't very efficient, but there are barely 100 data points so it should be instant
  try:
    previous_thrust = thrust_data[thrust_data["time"] < current_time]

    next_thrust = thrust_data[thrust_data["time"] > current_time]

    previous_thrust = previous_thrust.iloc[-1]
    next_thrust = next_thrust.iloc[0]

    return interpolate(current_time, previous_thrust["time"], next_thrust["time"], previous_thrust["thrust"], next_thrust["thrust"])
  except IndexError:
    finished_thrusting = True
    return 0



# https://www.digitaldutch.com/
density = 1 # kg/m^3 - this is density of the air, not the rocket
density_data = pd.read_csv("airQuantities.csv")

def get_density(altitude):
  altitude /= 1000 # convert to kilometers
  previous_density = density_data[density_data["Altitude"] < altitude]

  next_density = density_data[density_data["Altitude"] > altitude]

  previous_density = previous_density.iloc[-1]
  next_density = next_density.iloc[0]

  return interpolate(altitude, previous_density["Altitude"], next_density["Altitude"], previous_density["Density"], next_density["Density"])

density = get_density(base_altitude)
# print(density)

# Calculate using http://www.rasaero.com/dl_software_ii.htm
drag_coefficient = 0.75 # double check that it would be the same both up and sideways
# TODO: Find real data for areas
vertical_area = 0.01 # m^2
sideways_area = 0.1 # m^2
area = np.array([sideways_area, vertical_area])

# indicates whether te rocket has begun to fall
turned = False

output = open("output.csv", "w")
output.write("x,y,x_acc,y_acc\n")

def log_data(file, data):
  for val in data:
    file.write(str(val) + ",")
  file.write("\n")

print("Launching rocket")
while position[1] >= 0:
  log_data(output, [position[0], position[1], acceleration[0], acceleration[1]])
  t += time_increment

  # You have to reset acceleration every time
  force = np.array([0., 0.])
  gravity = gravitational_constant * earth_mass / (earth_radius + position[1] + base_altitude) ** 2
  force[1] -= gravity
  
  
  thrust = get_thrust(t - time_increment / 2)
  # thrust is newtons, so the change in momentum it is multiplied by time_interval
  force += thrust

  new_mass = mass - thrust * mass_per_thrust * time_increment
  # print(new_mass)

  # adjust for momentum
  velocity *= mass / new_mass

  mass = new_mass
  
  # find air resistance
  altitude = base_altitude + position[1]
  density = get_density(altitude)
  renold = density * area * drag_coefficient / 2

  air_resistance = renold * (velocity ** 2)

  # In the same direction, so wen we subtract it the velocity will decrease
  air_resistance *= np.sign(velocity)
  # someow this increases sideways velocity
  force -= air_resistance
  # print(force)
  acceleration = force / mass
  

  # Taking the average of the current acceleration and the previous acceleration is a better approximation of the change over the time_interval
  # It is basically a riemann midpoint integral over the acceleration so that it is more accurate finding the change in velocity
  combined_acceleration = (p_acceleration + acceleration) / 2

  velocity += acceleration * time_increment

  combined_velocity = (p_velocity + velocity) / 2

  position += combined_velocity * time_increment

  # y is the second index
  if not turned and position[1] < p_position[1]:
    print('Reached the turning point at %.3s seconds with a height of %.5s meters' % (t, position[1]))
    turned = True
  
  p_position = np.copy(position)
  p_velocity = np.copy(velocity)
  p_acceleration = np.copy(acceleration)

output.close()