import pandas as pd
import matplotlib.pyplot as plt

from Analysis.MonteCarloFlightData.AnalyzeMonteCarloFlight import read_sims



def display_end_temperature_distribution(sims):
    start_temps = []
    end_temps = []

    for sim in sims:
        try:
            start_temps.append((sim.iloc[0]["ox_tank.temperature"] - 273.15) * 9/5 + 32)
            end_temps.append((sim.iloc[-1]["ox_tank.temperature"] - 273) * 9/5 + 32)
        except Exception:
            print("Skipping because of error; probable non-simulation included in folder")
    
    plt.scatter(end_temps, start_temps)
    plt.xlabel("Final Temperature (F)")
    plt.ylabel("Initial Temperature (F)")
    plt.title("Range of Final Temperatures")

    plt.show()



if __name__ == "__main__":
    sims = read_sims("Analysis/MotorMonteCarlo3-Temporary")

    display_end_temperature_distribution(sims)

    # print(sims)
    