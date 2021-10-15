import matplotlib.pyplot as plt

import sys
sys.path.append(".")


from RocketParts.Motor.oxTank import OxTank

# Higher than 36 Celsius is super critical. Please don't do that
ox = OxTank()
ox.set_temperature(25 + 273.15) # 36.6667
# With a linear drain

masses = []
ullages = []
centers = []
temperatures = []

for _ in range(70):
    masses.append(ox.ox_mass)
    ullages.append(ox.ullage)
    centers.append(ox.get_center_of_mass() / ox.length)
    temperatures.append(ox.temperature)
    ox.update_drain(1)

fig, ax = plt.subplots()

ax.plot(masses, ullages, label="Ullage")
ax.plot(masses, centers, label="Center of Mass")

ax.set_title("Ullage over Masses")

ax.set_xlim(1, 70)
ax.set_xlabel("Ox Mass [kg]")
ax.invert_xaxis()

ax.set_ylim(0, 1)
ax.set_ylabel("Fraction")
ax.invert_yaxis()


plt.legend(loc="upper right")


plt.show()

plt.plot(masses, temperatures)
plt.show()


plt.plot(range(len(ox.inaccuracies)), ox.inaccuracies)
plt.show()

print(ox.inaccuracies)