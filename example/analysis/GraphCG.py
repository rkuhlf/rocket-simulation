# TODO: move all visualization to data


from matplotlib import pyplot as plt
import pandas as pd


df=pd.read_csv("Data/Output/motorOutput.csv")

plt.plot(df["time"], df["propellant_CG"])
plt.gca().invert_yaxis()

plt.show()