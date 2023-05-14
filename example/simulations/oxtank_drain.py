from matplotlib import pyplot as plt
from src.rocketparts.motorparts.oxtank import OxTank

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
        temperatures.append(tank._temperature)
    del times[0]

    fig, (ax1, ax2) = plt.subplots(1, 2)

    ax1.plot(times, masses)
    ax1.plot(times, gas_masses)
    ax1.plot(times, liquid_masses)

    ax2.plot(times, temperatures)


    plt.show()



        