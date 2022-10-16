
from matplotlib import pyplot as plt
import pandas as pd
from Data.Input.models import get_density, get_speed_of_sound

from Helpers.data import interpolated_lookup
from Simulations.FlightMotor2022 import get_sim


def get_mass(time: float, motor_output: pd.DataFrame, dry_mass: float):
    """Looks up the mass of the rocket given the requested time, the data from the motor, and the dry mass of the rocket."""

    prop_mass = interpolated_lookup(motor_output, "time", time, "propellant_mass", safe=True)

    return dry_mass + prop_mass

def calculate_forces_from_telemetrum(telemetrum_data, motor_output, CD_data, burn_time=30, parachute_time=50, save_path="./Data/MeasuredOutput/TelemetrumDataCalculations.csv", frontal_area=0.0262677157, dry_mass=48):
    """
    Based on the data output by a Telemetrum, calculate the weight, drag, and thrust over time experienced by the rocket.
    """

    # Ignoring everything that happens after parachute because I am not super concerned with tumbling simulations
    telemetrum_data = telemetrum_data[telemetrum_data["Time (s)"] < parachute_time]

    predictions = pd.DataFrame()
    predictions["Time (s)"] = telemetrum_data["Time (s)"]

    net_forces = []
    weights = []
    drags = []
    thrusts = []
    predicted_drags = []
    for index, row in telemetrum_data.iterrows():
        mass = get_mass(row["Time (s)"], motor_output, dry_mass)
        net_force = row["acceleration"] * mass

        weight = mass * 9.81
        
        # If the motor is burning, we have to guess what the drag should be
        density = get_density(row["altitude"] / 1000)
        speed = row["speed"]
        speed_of_sound = get_speed_of_sound(row["altitude"] / 1000)

        CD = interpolated_lookup(CD_data, "Mach", speed / speed_of_sound, "CD", safe=True)
        
        predicted_drags.append(-1/2 * density * speed ** 2 * frontal_area * CD)
        if row["Time (s)"] < burn_time:
            drag = 1/2 * density * speed ** 2 * frontal_area * CD
        else:
            drag = abs(net_force) - abs(weight)
        
        weights.append(-weight)
        net_forces.append(net_force)
        drags.append(-drag)
        
    telemetrum_data["Weight"] = weights
    telemetrum_data["Net Force"] = net_forces
    telemetrum_data["Drag"] = drags
    telemetrum_data["Thrust"] = telemetrum_data["Net Force"] - telemetrum_data["Weight"] - telemetrum_data["Drag"]
    predictions["Drag"] = predicted_drags

    telemetrum_data.to_csv(save_path)

    return predictions, telemetrum_data    

def compare_motor_to_actual():
    """Graphs the data output by the Telemetrum compared to the motor simulation that I tried to make match the flight conditions."""

    motor_simulation = get_sim()
    motor_simulation.logger.target = "motorOutput2022FlightConditions.csv"
    motor_simulation.run_simulation()
    motor_output = pd.read_csv(motor_simulation.logger.full_path)

    telemetrum_data = pd.read_csv("Data/MeasuredOutput/TelemetrumData.csv")
    CD_data = pd.read_csv("Data/Input/Aerodynamics/FinalGuessAtWSMR.CSV")

    predictions, telemetrum_data15 = calculate_forces_from_telemetrum(telemetrum_data, motor_output, CD_data, burn_time=15)
    predictions, telemetrum_data30 = calculate_forces_from_telemetrum(telemetrum_data, motor_output, CD_data, burn_time=30)

    

    # plt.plot(telemetrum_data["Time (s)"], telemetrum_data["Net Force"])
    # plt.plot(telemetrum_data["Time (s)"], telemetrum_data["Weight"])
    plt.plot(telemetrum_data15["Time (s)"], telemetrum_data15["Thrust"], label="Actual Thrust (15 sec)", zorder=50)
    plt.plot(telemetrum_data30["Time (s)"], telemetrum_data30["Thrust"], label="Actual Thrust (30 sec)", zorder=1)
    plt.plot(motor_output["time"], motor_output["thrust"], label="Predicted Thrust", zorder=100)

    # plt.plot(telemetrum_data["Time (s)"], telemetrum_data["Net Force"], label="Net Force")
    # plt.plot(telemetrum_data["Time (s)"], telemetrum_data["Drag"], label="Drag")
    # plt.plot(telemetrum_data["Time (s)"], telemetrum_data["Weight"], label="Weight")

    # plt.plot(predictions["Time (s)"], predictions["Drag"], label="Predicted Drag")

    plt.xlabel("Time (s)")
    plt.ylabel("Force (N)")
    plt.title("Flight Comparison")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    compare_motor_to_actual()

    pass
