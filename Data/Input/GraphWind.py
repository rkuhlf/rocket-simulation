# DISPLAY WIND OVER TIME


from scipy.io import netcdf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# # For some reason, the data I requested only has values starting at index 69383, and only the second recording device appears to be working
# f = netcdf.NetCDFFile('Data/Input/Wind/isfs_1Hz_20101110.nc', 'r')

# # Actually none of this works and it is super annoying so I just made a csv in the console
# data = f.variables["u"][:]

# df = pd.DataFrame(data)
# df = df[2]
# df = df[69383:]

# print(df)


# plt.plot(range(df.first_valid_index, df.last_valid_index()), df)

# plt.show()

# f.close()



df = pd.read_csv('Data/Input/Wind/windSample.csv')

fig = plt.figure()

plt.plot(df["index"], df["speed"])
fig.suptitle('Actual Wind')

plt.show()