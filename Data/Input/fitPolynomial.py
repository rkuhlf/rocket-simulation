from numpy.polynomial import Chebyshev
import pandas as pd

# If you are using VS Code, paths are relative to the project folder
data = pd.read_csv("Data/Input/airQuantities.csv")

print(data["Altitude"])
print(data["Density"])

c = Chebyshev.fit(data["Altitude"], data["Density"], deg=2)

print(c)
