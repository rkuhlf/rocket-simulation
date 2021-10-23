# GRAPH AN OVERVIEW OF A FLIGHT SIMULATION
# One graph with all of the outputs, one graph with some conversions, one graph with flight path, one graph for rotations, etc.

import os
import pandas as pd
import matplotlib.pyplot as plt

import sys
sys.path.append(".")

from Helpers.general import numpy_from_string





def graph_conversions():
    """Recommended that you run CalculateConversions.py to generate this file."""
    # Files are relative to the project folder you are running in, not the file location
    data = pd.read_csv("Data/Output/conversions.csv")

    # data["x"] = data['position'].apply(lambda x: numpy_from_string(x)[0])
    data["y"] = data['position'].apply(lambda x: numpy_from_string(x)[1])

    data.plot.line(x='time', y='y')
    data.plot.line(x='time', y='g-force')
    data.plot.line(x='time', y='mock')

    plt.show()



# graph everything
def graph_all():
    data = pd.read_csv("Data/Output/output.csv")


    data.plot.line()

    plt.show()



def graph_flight_path():
    data = pd.read_csv("Data/Output/output.csv")

    data["x"] = data['position1']
    data["y"] = data['position3']

    data.plot.line(x="x", y="y")

    plt.show()


def graph_vertical_acceleration():
    data = pd.read_csv("Data/Output/output.csv")

    data.plot.line(x="time", y=["rotation2", "Direction of translational drag3", "area", "flipped", "mag", "coeff"])
    # data.plot.line(x="time", y="rotation2")

    plt.show()

def graph_angle_of_attack():
    data = pd.read_csv("Data/Output/output.csv")

    data.plot.line(x="time", y="AOA1")
    data.plot.line(x="time", y="rotation2")

    plt.show()


if __name__ == "__main__":
    # graph_conversions()
    # graph_all()
    # graph_flight_path()
    # graph_vertical_acceleration()
    graph_angle_of_attack()