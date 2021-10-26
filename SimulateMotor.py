import matplotlib.pyplot as plt
import numpy as np

from RocketParts.motor import CustomMotor
from RocketParts.Motor.oxTank import OxTank
from RocketParts.Motor.injector import Injector
from RocketParts.Motor.combustionChamber import CombustionChamber
from RocketParts.Motor.grain import Grain
from RocketParts.Motor.nozzle import Nozzle
from environment import Environment



if __name__ == "__main__":
    ox = OxTank()
    grain = Grain({"debug": True})
    chamber = CombustionChamber(fuel_grain=grain)
    injector = Injector(ox_tank=ox, combustion_chamber=chamber)
    nozzle = Nozzle(fuel_grain=grain)
    env = Environment({
        "time_increment": 0.25
    })

    motor = CustomMotor(ox_tank=ox, injector=injector, combustion_chamber=chamber, nozzle=nozzle, environment=env)

    time = 0
    times = []
    pressures = []
    thrusts = []
    temperatures = []
    OFs = []
    grain_diameters = []

    # TODO: refactor this into a separate simulation class
    while True:
        motor.simulate_step()
        times.append(time)
        time += env.time_increment

        pressures.append(motor.combustion_chamber.pressure)
        thrusts.append(motor.thrust)
        temperatures.append(motor.combustion_chamber.temperature)
        grain_diameters.append(grain.inner_radius * 2)
        OFs.append(motor.OF)

        if ox.get_pressure() < chamber.pressure:
            print("Stopping Sim because pressure difference flipped.")
            break

        if ox.ox_mass <= 0:
            print("Stopping sim because ox drained completely")
            break

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ax1.plot(times, np.asarray(pressures) / 10 ** 5)
    ax1.set(xlabel="Chamber Pressure [bar]")

    ax2.plot(times, thrusts)
    ax2.set(title="Thrust over Time", xlabel="Time [s]", ylabel="Thrust [N]")

    ax3.plot(times, temperatures)

    ax4.plot(times, grain_diameters)

    fig.tight_layout()

    plt.show()

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

    ax1.plot(times, OFs)


    plt.show()