from dataclasses import dataclass, fields
from math import pi
from matplotlib import pyplot as plt
from numpy import arctan
import pandas as pd

from src.data.input.models import get_speed_of_sound


DATA_PATH = "./Data/Output/WSMRFlightData"
STRATOLOGGER_PATH = f"{DATA_PATH}/stratologger.csv"
TELEGPS_PATH = f"{DATA_PATH}/teleGPS.csv"
TELEMETRUM_PATH = f"{DATA_PATH}/telemetrum.csv"

@dataclass
class dataSet:
    stratologger: pd.DataFrame
    teleGPS: pd.DataFrame
    telemetrum: pd.DataFrame
    

def load_sources():
    strat = pd.read_csv(STRATOLOGGER_PATH)
    gps = pd.read_csv(TELEGPS_PATH)
    tele = pd.read_csv(TELEMETRUM_PATH)

    return dataSet(stratologger=strat, teleGPS=gps, telemetrum=tele)

def load_sources_with_converted_units():
    data = load_sources()
    
    # Convert out of ft to m
    src.data.stratologger["altitude"] /= 3.28
    src.data.stratologger["speed"] /= 3.28
    # This is around the average altitude at WSMR
    # There was actually ~100m of disagreement on launch altitude between telemetrum and teleGPS
    src.data.stratologger["altitude"] += 1192

    # I like F more than C
    src.data.telemetrum["temperature"] = src.data.telemetrum["temperature"] * 9/5 + 32

    time_offset = 8056.71
    src.data.teleGPS = src.data.teleGPS[data.teleGPS["time"] > time_offset]
    src.data.teleGPS["time"] -= time_offset

    return data

def load_sources_with_calculations():
    """Loads the data and performs calculations to try and ensure that all sources have the same columns"""
    data = load_sources_with_converted_units()

    # Calculate teleGPS speed
    speeds = []
    p_row = src.data.teleGPS.iloc[0]
    for index, row in src.data.teleGPS.iterrows():
        if index == 0:
            continue
        if p_row["time"] == row["time"]:
            speeds.append(speeds[-1] if len(speeds) > 0 else 0)
        else:
            speeds.append((row["pad_range"] - p_row["pad_range"]) / (row["time"] - p_row["time"]))

        p_row = row

    src.data.teleGPS["speed"] = speeds
    
    # Calculate Mach number for all devices
    for field in fields(data):
        data_source = getattr(data, field.name)

        machs = []
        for index, row in data_source.iterrows():
            speed_of_sound = get_speed_of_sound(row["altitude"])
            machs.append(row["speed"] / speed_of_sound)
            
        data_source["mach"] = machs
    
    # Calculate angles for teleGPS, which has no accelerometer
    # lateral_velocity = []
    # angles = []
    # for index, row in src.data.teleGPS.iterrows():
    #     if row["pad_dist"] == 0:
    #         angle = 90
    #     else:
    #         angle = arctan(row["altitude"] / row["pad_dist"]) * 180 / pi

    #     angles.append(angle)
        
    # data_source["angle"] = angles

    # Calculate angles for stratologger, which has an accelerometer
    
    return data


def compare_altitude(data):
    plt.plot(data.telemetrum["time"], src.data.telemetrum["altitude"], label="Telemetrum")
    plt.plot(data.stratologger["time"], src.data.stratologger["altitude"], label="Stratologger")
    plt.plot(data.teleGPS["time"], src.data.teleGPS["altitude"], label="TeleGPS")

    plt.title("Altitude Comparison")
    plt.ylabel("Altitude MSL (m)")
    plt.xlabel("Time (s)")
    plt.legend()

    plt.show()

def compare_speed(data):
    plt.plot(data.telemetrum["time"], src.data.telemetrum["speed"], label="Telemetrum")
    plt.plot(data.stratologger["time"], src.data.stratologger["speed"], label="Stratologger")
    plt.plot(data.teleGPS["time"], src.data.teleGPS["speed"], label="TeleGPS")

    plt.title("Speed Comparison")
    plt.ylabel("Speed (m/s)")
    plt.xlabel("Time (s)")
    plt.legend()

    plt.show()

def compare_mach(data):
    plt.plot(data.telemetrum["time"], src.data.telemetrum["mach"], label="Telemetrum")
    plt.plot(data.stratologger["time"], src.data.stratologger["mach"], label="Stratologger")
    plt.plot(data.teleGPS["time"], src.data.teleGPS["mach"], label="TeleGPS")

    plt.title("Mach Comparison")
    plt.ylabel("Mach ()")
    plt.xlabel("Time (s)")
    plt.legend()

    plt.show()

def compare_net_force(data):
    pass

def compare_lat_long(data):
    fig = plt.figure()
    ax_all = fig.add_subplot(111, frameon=False)
    ax_all.set_title("Coordinates Comparison", y=1.05)
    ax_all.set_ylabel("Coordinates (degrees)", labelpad=35)
    ax_all.set_xlabel("Time (s)", labelpad=15)
    ax_all.set_xticks([])
    ax_all.set_yticks([])

    ax1 = fig.add_subplot(121)
    ax1.plot(data.telemetrum["time"], src.data.telemetrum["latitude"], label="Telemetrum")
    ax1.plot(data.teleGPS["time"], src.data.teleGPS["latitude"], label="TeleGPS")
    ax1.legend()
    ax1.set_title("Latitude")

    ax2 = fig.add_subplot(122)
    ax2.plot(data.telemetrum["time"], src.data.telemetrum["longitude"], label="Telemetrum")
    ax2.plot(data.teleGPS["time"], src.data.teleGPS["longitude"], label="TeleGPS")
    ax2.legend()
    ax2.set_title("Longitude")
    
    plt.tight_layout()

    plt.show()

def compare_temperature(data):
    plt.plot(data.telemetrum["time"], src.data.telemetrum["temperature"], label="Telemetrum")
    plt.plot(data.stratologger["time"], src.data.stratologger["temperature"], label="Stratologger")

    plt.title("Temperature Comparison")
    plt.ylabel("Temperature (F)")
    plt.xlabel("Time (s)")
    plt.legend()

    plt.show()

def compare_flight_angle(data):
    # Assuming that it is pointed directly towards velocity, which is wrong but close enough here
    plt.plot(data.telemetrum["time"], src.data.telemetrum["angle"], label="Telemetrum")
    plt.plot(data.teleGPS["time"], src.data.teleGPS["angle"], label="TeleGPS")

    plt.title("Ground Angle Comparison")
    plt.ylabel("Angle (degrees)")
    plt.xlabel("Time (s)")
    plt.legend()

    plt.show()


if __name__ == "__main__":
    data = load_sources_with_calculations()

    compare_altitude(data)
    # compare_speed(data)
    # compare_mach(data)
    # compare_temperature(data)
    # compare_lat_long(data)
    # compare_flight_angle(data)


    pass
