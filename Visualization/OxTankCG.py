import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append(".")


from RocketParts.Motor.oxTank import OxTank

# Higher than 36 Celsius is super critical. Please don't do that
ox = OxTank({
    "ox_mass": 52.43,
    "length": 2.54,
    "radius": 0.1905 / 2,
    "temperature": 293.15
})
# ox.set_temperature(30 + 273.15)
# With a linear drain

masses = []
ullages = []
centers = []
temperatures = []
pressures = []

for _ in range(60):
    masses.append(ox.ox_mass)
    ullages.append(ox.ullage)
    centers.append(ox.get_center_of_mass() / ox.length)
    temperatures.append(ox.temperature)
    pressures.append(ox.get_pressure())
    ox.update_drain(1)

important_temperatures = temperatures[:int(len(temperatures) * 0.75)]
print(f"The average of the first 3/4 of temperatures is {np.average(important_temperatures)} Kelvin")

important_pressures = pressures[:int(len(pressures) * 0.75)]
print(f"The average of the first 3/4 of pressures is {np.average(important_pressures) / 10**5} bar")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

ax1.plot(masses, ullages, label="Ullage")
ax1.plot(masses, centers, label="Center of Mass")

ax1.set_title("Ullage over Mass Drain")

ax1.set_xlim(1, 60)
ax1.set_xlabel("Ox Mass [kg]")
ax1.invert_xaxis()

ax1.set_ylim(0, 1)
ax1.set_ylabel("Fraction")
ax1.invert_yaxis()


ax1.legend(loc="upper right")


ax2.plot(masses, temperatures)
ax2.set_title("Temperature over Mass Drain")
ax2.set_xlabel("Ox Mass [kg]")
ax2.set_ylabel("Temperature [K]")
ax2.invert_xaxis()

ax3.plot(masses, pressures)
ax3.set_title("Pressure over Mass Drain")
ax3.set_xlabel("Ox Mass [kg]")
ax3.set_ylabel("Pressure [Pa]")
ax3.invert_xaxis()

fig.tight_layout()

plt.show()