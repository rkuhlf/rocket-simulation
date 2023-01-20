# Determine Coefficients for the a * G^n equation for regression


import lmfit
import numpy as np
import matplotlib.pyplot as plt

data = [
    [242, 1.02],
    [242, 1.02],
    [327, 1.32],
    [327, 1.34],
    [261, 1.3],
    [261, 1.31],
    [280, 1.1],
    [280, 1.13],
    [278, 1.05],
    [278, 1.12],
    [272, 1.18],
    [272, 1.11],
    [268, 1.17],
    [268, 1.1],
    [270, 1.1],
    [272, 1.07],
]
data = np.asarray(data).transpose()

def space_averaged_regression(G, a, n):
    return a * G ** n


model = lmfit.Model(space_averaged_regression)

params = model.make_params(a=0.001, n=1)
result = model.fit(
    data[1],
    params, G=data[0])

print(result.params)

fluxes = np.linspace(min(data[0]) - 10, max(data[0]) + 10)
plt.plot(fluxes, model.eval(result.params, G=fluxes))
plt.scatter(data[0], data[1])

plt.show()