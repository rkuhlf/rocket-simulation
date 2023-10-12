from matplotlib import pyplot as plt
from src.rocketparts.motorparts.oxtank import OxTank

# Temperature stays constant in the gas only phase because I am not accounting for the cooling from gas expansion, and we stopped having evaporation.

if __name__ == "__main__":
    tank = OxTank(length=2.65, diameter=0.17, ox_mass=45, temperature=293)

    times = [0]
    masses = []
    gas_masses = []
    liquid_masses = []
    temperatures = []

    while tank.ox_mass > 0:
        tank.drain_mass(0.01)
        times.append(times[-1] + 0.1)
        masses.append(tank.ox_mass)
        gas_masses.append(tank._gas_mass)
        liquid_masses.append(tank._liquid_mass)
        # temperatures.append((tank._temperature - 273) * 9/5 + 32)
        temperatures.append(tank._temperature)
    del times[0]

    fig, (ax1, ax2) = plt.subplots(1, 2)

    ax1.plot(times, masses, label="Total Mass")
    ax1.plot(times, gas_masses, label="Gas Mass")
    ax1.plot(times, liquid_masses, label="Liquid Mass")
    ax1.legend()

    ax2.plot(times, temperatures, label="Temperature")

    ax1.set_xlabel("Iterations ()")
    ax2.set_xlabel("Iterations ()")

    ax1.set_ylabel("Mass (kg)")
    ax2.set_ylabel("Temperature (F)")
    ax2.set_title("Temperature over Time")

    plt.show()



        