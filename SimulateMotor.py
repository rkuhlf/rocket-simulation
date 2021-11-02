# RUN A BASIC SIMULATION OF A HYBRID MOTOR
# All of the math is located within different files, and the motor file brings them all together
# This script simply instantiates them, runs the simulation, then makes a ton of graphs
# Right now, all of the inputs are based off of the Heros 3 rocket, developed at Stuttgart, because I am trying to confirm that my simulated output vaguely matches theirs
# FIXME: at the moment, the combustion chamber pressure is at ~10 bar when it should be 30-35 bar


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
    grain = Grain(verbose=True)
    chamber = CombustionChamber(fuel_grain=grain)
    injector = Injector(ox_tank=ox, combustion_chamber=chamber)
    # Stuttgart optimized at 30 bar, but that gives me a totally funny shape because the pressure never reaches it
    # 0.08 gives me a reasonable thrust profile for the pressure I am workin at
    nozzle = Nozzle(throat_diameter=0.08, fuel_grain=grain) # meters
    env = Environment(time_increment=0.25)

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
        ox_pressures.append(ox.pressure)
        thrusts.append(motor.thrust)
        chamber_temperatures.append(motor.combustion_chamber.temperature)
        ox_temperatures.append(ox.temperature)
        grain_diameters.append(grain.inner_radius * 2)
        OFs.append(motor.OF)
        c_stars.append(motor.combustion_chamber.cstar)
        specific_impulses.append(motor.thrust / (motor.combustion_chamber.mass_flow_out * 9.81))

        if ox.pressure < chamber.pressure:
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