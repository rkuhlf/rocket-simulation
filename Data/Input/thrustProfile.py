import pandas as pd

data = pd.read_csv("./Data/Input/thrustCurveToModify.csv")

desired_burn_time = 18
desired_average_thrust = 8100




times = list(data["time"])

burn_time = times[-1]

thrusts = list(data["thrust"])

total_impulse = 0

# We can just cut off the last one because we start and end with 0
# Don't worry too much about total impulse; it has extremely high variability between runs of the motor and depending on how you count the in betweens you can get a range of 5000 Ns
for i in range(len(times) - 1):
    total_impulse += (times[i + 1] - times[i]) * (thrusts[i] + thrusts[i + 1]) / 2



average_thrust = total_impulse / burn_time


data["time"] *= desired_burn_time / burn_time
data["thrust"] *= desired_average_thrust / average_thrust

print(data)

