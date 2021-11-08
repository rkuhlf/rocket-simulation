# USE GRAPHS TO DEMONSTRATE ACCURACY OF DATA MODELS
# Display the input points along with the fitted line to match them
# It's important to visually verify that we aren't getting significant error in the inputs

import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np

# ctrl-K, ctrl-shift-s to save without screwing this up
sys.path.append(".")

from Data.Input.models import *



# Files are relative to the project folder you are running in, not the file location
data = pd.read_csv("Data/Input/airQuantities.csv")

inputs = np.arange(0, 13, 0.1)
# print(get_density(5))
outputs = get_density(inputs)

# data.plot.scatter(x='Altitude', y='Density')
# plt.plot(inputs, outputs, 'r')

# plt.show()



data = pd.read_csv("Data/Input/aerodynamicQualities.csv")

# Rasaero outputs to a max of 21
inputs = np.arange(0, 25, 0.1)

outputs = list(map(get_splined_coefficient_of_drag, inputs))
# outputs = get_coefficient_of_drag(inputs)

data.plot.scatter(x='Mach', y='CD')
plt.plot(inputs, outputs, 'r')

plt.show()


data = pd.read_csv("Data/Input/airQuantities.csv")

inputs = np.arange(0, 13, 0.1)

outputs = list(map(get_speed_of_sound, inputs))

# data.plot.scatter(x='Altitude', y='Speed of sound')
# plt.plot(inputs, outputs, 'r')

# plt.show()
