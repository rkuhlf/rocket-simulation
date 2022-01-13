import pandas as pd



if __name__ == "__main__":
    df = pd.read_csv("./Analysis/MonteCarloFlightData/output.csv")

    print(df)

    # print(df[df["Lateral Velocity"] > 150])
    print(df[df["Apogee"] > 20000][["Apogee", "Lateral Velocity", "Total Impulse", "Mean Wind Speed", "Wind Speed Deviation"]])