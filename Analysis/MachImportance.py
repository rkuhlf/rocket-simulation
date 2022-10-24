# Calculate which mach numbers are the most important for our rocket by determining the dynamic pressure at every point in a flight, and summing them over the time spent at each mach number.
# Knowing which Mach number CDs have the highest coefficients and which we spend the most time at is useful for determining which values we need to minimize the CD for.
# For example, if you are hitting the transonic region, but you are below transonic for 95% of the flight, you might want a subsonic nose cone (or you might not, since the squared velocity term contributes a lot to the dynamic pressure).

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Helpers.data import interpolated_lookup



def display_mach_importance(flight_data: pd.DataFrame, atmosphere_data: pd.DataFrame):
    """
    Create and show a matplotlib bar chart of the importance of each Mach number in the drag of a rocket's flight.
    """

    flight_data["Dynamic Pressure"] = 0
    
    for index, row in flight_data.iterrows():
        density = interpolated_lookup(atmosphere_data, "Altitude", row["position3"], "Density", safe=True)

        # P = 1/2 * rho * v^2
        flight_data.loc[index, "Dynamic Pressure"] = 1/2 * row["relative velocity3"] ** 2 * density


    min_mach = 0
    max_mach = 2
    num_buckets = 10
    bucket_labels = np.linspace(min_mach, max_mach, num_buckets)
    bucket_values = np.zeros(bucket_labels.size)

    p_time = 0
    for index, row in flight_data.iterrows():
        
        for bucket_index, label in enumerate(bucket_labels):
            if label > row["Mach"]:
                bucket_values[bucket_index] += row["Dynamic Pressure"] * (row["time"] - p_time)
                break
        
        p_time = row["time"]
    
    # Graph in matplotlib
    plt.bar(bucket_labels, bucket_values)
    
    plt.title("Drag Importance of Mach Numbers")
    plt.xlabel("Mach Number ()")
    plt.ylabel("Weighted Density (Pa)")
    
    plt.show()





if __name__ == "__main__":
    flight_data = pd.read_csv("Data/Output/TestingData/testRocketFlightOutput.csv")
    atmosphere_data = pd.read_csv("Data/Input/airQuantities.csv")

    display_mach_importance(flight_data, atmosphere_data)
