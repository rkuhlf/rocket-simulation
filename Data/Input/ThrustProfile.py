# LINEARLY SCALE THRUST PROFILE
# Many times, I would like to have a basic motor simulation for a given burn time and average thrust (or total impulse)
# In order to generate one, I can just scale up a reasonable thrust curve for a hybrid motor.
# This file is used particularly often with RASAero .eng files.

import pandas as pd

def scale_saved_curve(path, desired_burn_time, desired_average_thrust, target_path=None):
    if target_path is None:
        if path.endswith("csv"):
            target_path = path[:-4] + "Scaled" + ".csv"
        else:
            target_path = path + "Scaled"
    
    data = pd.read_csv(path)

    data = scale_curve(data, desired_burn_time, desired_average_thrust)
        
    data.set_index("time", inplace=True)

    data.to_csv(target_path)


def scale_curve(data, desired_burn_time, desired_average_thrust):
    times = list(data["time"])

    burn_time = times[-1]

    thrusts = list(data["thrust"])

    total_impulse = 0

    # Don't worry too much about total impulse; it has extremely high variability between runs of the motor and depending on how you count the in betweens you can get a range of 5000 Ns
    for i in range(len(times) - 1):
        # Use a trapezoidal reimann sum to approximate the integral
        total_impulse += (times[i + 1] - times[i]) * (thrusts[i] + thrusts[i + 1]) / 2



    average_thrust = total_impulse / burn_time


    data["time"] *= desired_burn_time / burn_time
    data["thrust"] *= desired_average_thrust / average_thrust
    
    return data


if __name__ == "__main__":        
    scale_saved_curve("./Data/Input/thrustCurveO6300.csv", 22, 5000, "./Data/Input/thrustCurveSmaller.csv")
    
