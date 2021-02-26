import matplotlib.pyplot as plt
import pandas as pd


# Files are relative to the project folder you are running in, not the file location
data = pd.read_csv("Data/Output/output.csv")

data.plot.line(x='time', y='y')
