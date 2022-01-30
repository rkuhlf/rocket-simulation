import pandas as pd

from Analysis.MonteCarloFlightData.AnalyzeMonteCarloFlight import read_sims



if __name__ == "__main__":
    sims = read_sims("Analysis/MotorMonteCarlo-Temporary")

    print(sims)
    