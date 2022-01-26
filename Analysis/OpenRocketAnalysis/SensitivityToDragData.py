import os

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from torch import mul
import javaInitialization
from Analysis.OpenRocketAnalysis.overrideCDListener import OverrideCDConstant, OverrideCDDataFrame

import orhelper
from orhelper import FlightDataType, FlightEvent
from openRocketHelpers import getSimulationNames, most_updated_sim, new_or_instance
from net.sf.openrocket.aerodynamics import FlightConditions


def display_constant_CD_effect():
    apogees = []
    CDs = np.linspace(0.3, 3, 4)

    with new_or_instance() as instance:
        
        orh = orhelper.Helper(instance)

        sim = most_updated_sim(orh)


        for CD in CDs:
            orh.run_simulation(sim, listeners=[OverrideCDConstant(sim, CD)])
            apogee = sim.getSimulatedData().getMaxAltitude() * 3.28084
            print(f"CD = {CD} --> {apogee} feet")
            apogees.append(apogee)
        
        plt.plot(CDs, apogees)
        plt.title("CD Impact")
        plt.xlabel("Coefficient of Drag")
        plt.ylabel("Apogee [feet]")

        plt.ylim(bottom=0)

        plt.show()

        # OverrideCDConstant(sim, 1.8) --> 10,800 meters = 35000 feet
        # [] --> 23,000 meters = 75000 feet


def display_multiplied_CD_effect():
    apogees = []
    multipliers = np.linspace(0.25, 2, 50)

    df = pd.read_csv("Data/Input/aerodynamicQualities.csv")

    with new_or_instance() as instance:
        
        orh = orhelper.Helper(instance)

        sim = most_updated_sim(orh)

        p_multiplier = 1
        for multiplier in multipliers:
            df["CD"] *= multiplier / p_multiplier
            orh.run_simulation(sim, listeners=[OverrideCDDataFrame(sim, df)])
            apogee = sim.getSimulatedData().getMaxAltitude() * 3.28084
            print(f"multiplier = {multiplier} --> {apogee} feet")
            apogees.append(apogee)

            p_multiplier = multiplier
        
        plt.plot(multipliers, apogees)
        plt.title("CD Impact")
        plt.xlabel("CD Multiplier")
        plt.ylabel("Apogee [feet]")

        plt.ylim(bottom=0)

        plt.show()

        # OverrideCDConstant(sim, 1.8) --> 10,800 meters = 35000 feet
        # [] --> 23,000 meters = 75000 feet



if __name__ == "__main__":
    display_multiplied_CD_effect()


    pass
