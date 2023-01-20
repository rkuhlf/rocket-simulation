# DISPLAY WIND OVER TIME
# Show some of the wind data I downloaded so that I can try to match it

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


def display_measured_wind():
    # Some wind data from Utah
    df = pd.read_csv('Data/Input/Wind/MoreData.csv')

    fig, (ax1, ax2) = plt.subplots(2)

    ax1.plot(df["index"], df["Magnitude"])
    ax1.set(title='Actual Speeds')

    ax2.scatter(df["index"], df["Direction"], s=1)
    ax2.set(title='Actual Directions')

    fig.tight_layout()

    plt.show()


if __name__ == "__main__":
    display_measured_wind()