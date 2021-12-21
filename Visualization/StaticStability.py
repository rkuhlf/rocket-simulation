

import pandas as pd
import matplotlib.pyplot as plt




def display_margin(data):
    plt.plot(data["time"], data["Stability [Calibers]"])

    plt.show()


if __name__ == "__main__":
    data = pd.read_csv("Data/Output/output.csv")

    display_margin(data)