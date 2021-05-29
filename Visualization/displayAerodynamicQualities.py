# Several graphs intended to illustrate how different inputs affect the output of coefficient of drag and center of pressure

import sys
# This adds the project to te path so that I can import helpers
sys.path.append(".")
# Depending on how aggressive any autoformatting is it may be necessary to save this without formatting so that the path is affected at the start

from Helpers.general import numpy_from_string
import matplotlib.pyplot as plt
import pandas as pd
import os





# Files are relative to the project folder you are running in, not the file location
data = pd.read_csv("Data/Input/aerodynamicQualities.csv")

# data["x"] = data['position'].apply(lambda x: numpy_from_string(x)[0])
# data["y"] = data['CD'].apply(lambda x: numpy_from_string(x)[1])

data.plot.line(x='Mach', y='CD')
# data.plot.line(x='time', y='g-force')
# data.plot.line(x='time', y='mock')

plt.show()
