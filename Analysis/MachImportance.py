# Calculate which mach numbers are the most important for our rocket

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Helpers.data import interpolated_lookup



def display_mach_importance(sim: pd.DataFrame):
    # 1/2 * rho * v^2
    sim["Dynamic Pressure"] = 1/2 * sim["relative velocity3"] ** 2 * interpolated_lookup(atmosphere, "altitude", sim["position3"], "Density")


    # min_mach, max_mach, num_buckets
    bucket_labels = np.linspace(0, 2, 10)
    bucket_values = np.zeros(bucket_labels.size[0])

    for index, row in sim.iterrows():
        for bucket_index, label in enumerate(bucket_labels):
            if label > row["Mach"]:
                bucket_values[bucket_index] += row["Dynamic Pressure"]
                break
    
    # Graph in matplotlib
    plt.bar(bucket_labels, bucket_values)
    
    plt.title("Drag Importance of Mach Numbers")
    plt.xlabel("Mach Number ()")
    plt.ylabel("Weighted Density (Pa)")
    
    plt.show()





if __name__ == "__main__":
    data = pd.read_csv("Data/Output/output5DOFWind.csv")
    atmosphere = pd.read_csv("Data/Input/airQuantities.csv")

    display_mach_importance(data)