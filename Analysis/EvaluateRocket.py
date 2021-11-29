# PROVIDE A DATA-BASED EVALUATION OF A SIMULATED ROCKET
# Based on instantaneous conditions at every time frame, the script will calculate optimal coefficients/values and measure the distance away from them that we are


import pandas as pd
import numpy as np

# Easier safety factors

# Fin flutter safety; should be easy

# Max Q

# Max g-force


# I think there is some way to do this with ballistic coefficient. I just want an indicator of how close we are to the best possible mass for a time


# I want to have something in here for stability. Maybe I will optimize so that the CP is as close to the CG as possible divided by moment of inertia


# I guess I could import the Goddard problem solver and determine how close our thrust curve is to the best thrust curve for a flight of otherwise identical dimensions.
# It will be hard to make this work for variable mass ox tank. I guess I could just assume O/F based mass drain matched to the thrust profile

def find_max_compressive_force(data):
    # Assume that thrust and drag are acting in the exact same directions
    # This is not true, but it should be very close, and it is a worst case for compression
    data["Drag Magnitude"] = np.sqrt(data["Drag1"] ** 2 + data["Drag2"] ** 2 + data["Drag3"] ** 2)
    data["Compressive"] = data["Thrust"] + data["Drag Magnitude"]

    return np.max(data["Compressive"])


def find_total_impulse(data):
    # Just use a rectangular approximation instead of the trapezoid
    return np.sum(data["Thrust"]) * (data.iloc[1]["time"] - data.iloc[0]["time"])


if __name__ == "__main__":
    script_path = "Data/Output/output.csv"
    data = pd.read_csv(script_path)

    print(f"The total impulse used in the simulation was {find_total_impulse(data)} Ns")
    print(f"The maximum compressive force experienced in the simulation was {find_max_compressive_force(data)} N")
