# LINEARLY SCALE THRUST PROFILE
# Many times, I would like to have a basic motor simulation for a given burn time and average thrust (or total impulse)
# In order to generate one, I can just scale up a reasonable thrust curve for a hybrid motor.
# This file is used particularly often with RASAero .eng files.

import pandas as pd




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
    data = pd.read_csv("./Data/Input/thrustCurveO6300.csv")

    data = scale_curve(data, 22, 10000)
    
    print(data)
    
    data.set_index("time", inplace=True)

    data.to_csv("./Data/Input/currentGoddard.csv")
    
