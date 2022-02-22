# LOOP OVER OFs, CONSIDERING DIFFERENT INPUTS

# CONCLUSIONS:
# It performs best when there is less acrylonitrile
# It performs better when there is more butadiene
# Performs best when there is no styrene, but it shifts the OF way up without having a large effect
# ABS gives a relatively narrow peak for the optimal O/F

import numpy as np
import matplotlib.pyplot as plt

from rocketcea.cea_obj import CEA_Obj

from Data.Input.CEA.CEAPropellants import define_ABS_nitrous
from Data.Input.CEA.AnalyzeOFAtPressure import find_efficiencies, display_OF_graph
from Helpers.visualization import make_matplotlib_big

abs_nitrous: CEA_Obj = None


def save_full_output(name="absNitrous.txt"):
    output = abs_nitrous.get_full_cea_output(362.6, 6.18, 5.09)

    with open(f"Data/Input/CEAOutput/{name}", "w") as f:
        f.write(output)

    print(output)


def display_effect_of_acrylonitrile():
    global abs_nitrous

    fig, ax = plt.subplots()

    for acrylonitrile in np.linspace(20, 60, 16):
        abs_nitrous = define_ABS_nitrous(percent_acrylonitrile=acrylonitrile)
        _, impulses, OFs = find_efficiencies(abs_nitrous)
        
        ax.plot(OFs, impulses, label=f"{acrylonitrile}")

    ax.set(title="Effect of Acrylonitrile Concentration")
    ax.legend()

    plt.show()

def display_effect_of_butadiene():
    global abs_nitrous

    fig, ax1 = plt.subplots()

    for butadiene in np.linspace(10, 60, 10):
        abs_nitrous = define_ABS_nitrous(percent_butadiene=butadiene)
        _, impulses, OFs = find_efficiencies(abs_nitrous)
        
        ax1.plot(OFs, impulses, label=f"{butadiene}")

    ax1.set(title="Effect of Butadiene Concentration")

    fig.legend()
    plt.show()

def display_effect_of_styrene():
    global abs_nitrous

    fig, ax1 = plt.subplots()

    for styrene in np.linspace(0, 30, 10):
        abs_nitrous = define_ABS_nitrous(percent_styrene=styrene)
        _, impulses, OFs = find_efficiencies(abs_nitrous)
        
        ax1.plot(OFs, impulses, label=f"{styrene}")

    ax1.set(title="Effect of Styrene Concentration")

    plt.legend()
    plt.show()

def display_effect_of_pressure(pressures=np.linspace(100, 1000, 10)):
    global abs_nitrous

    
    for pressure, color in zip(pressures, np.linspace(0.8, 0.3, len(pressures))):
        _, impulses, OFs = find_efficiencies(abs_nitrous, chamber_pressure=pressure)
        
        plt.plot(OFs, impulses, label=f"{pressure}", c=f"{color}")

    plt.title("Effect of Pressure on Efficiency")
    plt.xlabel("O/F ()")
    plt.ylabel("Specific Impulse (s)")

    # plt.legend()
    plt.show()


if __name__ == "__main__":
    abs_nitrous = define_ABS_nitrous()

    # display_effect_of_styrene()

    chamber_pressure = 362.6
    environmental_pressure = 11.965613
    # display_OF_graph(abs_nitrous, chamber_pressure=chamber_pressure, area_ratio=5.09)
    # print(abs_nitrous.get_eps_at_PcOvPe(chamber_pressure, 6.18, chamber_pressure/environmental_pressure))

    make_matplotlib_big()
    display_effect_of_pressure(pressures=np.linspace(100, 10000, 20))

    # abs_nitrous = define_ABS_nitrous()
    # save_full_output()
    pass

