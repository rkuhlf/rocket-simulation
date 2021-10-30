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
    ox_pressures = []
    combustion_pressures = []
    thrusts = []
    chamber_temperatures = []
    ox_temperatures = []
    OFs = []
    grain_diameters = []
    c_stars = []
    specific_impulses = []

    # TODO: refactor this into a separate simulation class
    while True:
        motor.simulate_step()
        times.append(time)
        time += env.time_increment

        combustion_pressures.append(motor.combustion_chamber.pressure)
        ox_pressures.append(ox.get_pressure())
        thrusts.append(motor.thrust)
        chamber_temperatures.append(motor.combustion_chamber.temperature)
        ox_temperatures.append(ox.temperature)
        grain_diameters.append(grain.inner_radius * 2)
        OFs.append(motor.OF)
        c_stars.append(motor.combustion_chamber.cstar)
        specific_impulses.append(motor.thrust / (motor.combustion_chamber.mass_flow_out * 9.81))

        if ox.get_pressure() < chamber.pressure:
            print("Stopping Sim because pressure difference flipped.")
            break

        if ox.ox_mass <= 0:
            print("Stopping sim because ox drained completely")
            break


    total_impulse = np.sum(thrusts) * env.time_increment
    print(f"TOTAL IMPULSE: {total_impulse}")

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ax1.plot(times, np.asarray(combustion_pressures) / 10 ** 5)
    ax1.plot(times, np.asarray(ox_pressures) / 10 ** 5)
    ax1.set(title="Pressures over Time", xlabel="Time [s]", ylabel="Pressure [bar]")

    ax2.set(title="Ox Tank Pressure over Time")

    ax2.plot(times, thrusts)
    ax2.set(title="Thrust over Time", xlabel="Time [s]", ylabel="Thrust [N]")

    ax3.plot(times, chamber_temperatures)
    ax3.set(title="Chamber Temperatures over Time")

    ax4.plot(times, ox_temperatures)
    ax4.set(title="Ox Temperatures over Time", xlabel="Time [s]", ylabel="Temperature [K]")

    fig.tight_layout()

    plt.show()

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

    ax1.plot(times, OFs)
    ax1.set(title="Mixing Ratio", xlabel="Time [s]", ylabel="O/F")

    ax2.plot(times, np.array(grain_diameters) * 100)
    ax2.set(title="Grain Diameter", xlabel="Time [s]", ylabel="Diameter [cm]")

    # FIXME: The C* values for combustion seem to be slightly low. I think it is probably just a combination
    ax3.plot(times, c_stars)
    ax3.set(title="Combustion Efficiency", xlabel="Time [s]", ylabel="C* [m/s]")

    ax4.plot(times, specific_impulses)
    ax4.set(title="Combustion Efficiency", xlabel="Time [s]", ylabel="Specific Impulse [s]")

    fig.tight_layout()

    plt.show()