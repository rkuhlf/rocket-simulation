# DISPLAY AERODYNAMIC DATA OVER MACH
# Looking over mach numbers should give the same information as looking over Reynolds numbers
# Several graphs intended to illustrate how different inputs affect the output of coefficient of drag and center of pressure

import matplotlib.pyplot as plt
import pandas as pd
import os

import sys
sys.path.append(".")

from Helpers.general import numpy_from_string


# Files are relative to the project folder you are running in, not the file location
data = pd.read_csv("Data/Input/aerodynamicQualities.csv")

# data["x"] = data['position'].apply(lambda x: numpy_from_string(x)[0])
# data["y"] = data['CD'].apply(lambda x: numpy_from_string(x)[1])

data.plot.line(x='Mach', y='CD')
# data.plot.line(x='time', y='g-force')
# data.plot.line(x='time', y='mock')

# TODO: show 10-odd isolines for different angles of attack over mach numbers

plt.show()
