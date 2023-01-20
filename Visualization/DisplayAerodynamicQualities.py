# DISPLAY AERODYNAMIC DATA OVER MACH
# Looking over mach numbers should give the same information as looking over Reynolds numbers
# Several graphs intended to illustrate how different inputs affect the output of coefficient of drag and center of pressure

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


from data.input.models import get_splined_coefficient_of_drag


data = pd.read_csv("Data/Input/aerodynamicQualities.csv")


zero_AOA = data[data["Alpha"] == 0]
zero_AOA.sort_values(["Mach"], inplace=True)
zero_AOA.plot.line(x='Mach', y='CD')

# machs = np.linspace(0, 5, 50)
# zero_AOA_model = get_splined_coefficient_of_drag(machs, 0)

# plt.plot(machs, zero_AOA_model)


# TODO: show 10-odd isolines for different angles of attack over mach numbers

plt.show()
