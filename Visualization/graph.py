import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
# This adds the project to te path so that I can import helpers
sys.path.append(".")
# Depending on how aggressive any autoformatting is it may be necessary to save this without formatting so that the path is affected at the start
from Helpers.general import numpy_from_string





"""
# Files are relative to the project folder you are running in, not the file location
data = pd.read_csv("Data/Output/conversions.csv")

# data["x"] = data['position'].apply(lambda x: numpy_from_string(x)[0])
data["y"] = data['position'].apply(lambda x: numpy_from_string(x)[1])

data.plot.line(x='time', y='y')
data.plot.line(x='time', y='g-force')
data.plot.line(x='time', y='mock')

plt.show()
"""


# rap everytin
"""
data = pd.read_csv("Data/Output/output.csv")

# data["x"] = data['position1']
# data["y"] = data['position3']

data.plot.line()

plt.show()
"""

data = pd.read_csv("Data/Output/output.csv")

data["x"] = data['position1']
data["y"] = data['position3']

data.plot.line(x="x", y="y")

plt.show()
