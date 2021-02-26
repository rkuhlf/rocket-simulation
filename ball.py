import numpy as np

# INITIAL
position = np.array([2, 1], dtype="float64")
velocity = np.array([1, 10], dtype="float64")
acceleration = np.array([0, 0], dtype="float64")
t = 0


# CONSTANTS
time_increment = 0.01
gravity = -9.8


output = open("output.csv", "w")
output.write("time,position,velocity,acceleration\n")

def log_data(file, data):
  for val in data:
    file.write(str(val) + ",")
  file.write("\n")

while position[1] >= 0:
  log_data(output, [t, position, velocity, acceleration])
  t += time_increment
  position += velocity * time_increment
  velocity += acceleration * time_increment
  acceleration = gravity
  # find air resistance

output.close()