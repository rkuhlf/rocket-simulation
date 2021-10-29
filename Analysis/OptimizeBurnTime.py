# LOOP OVER DIFFERENT BURN TIMES TO DETERMINE ALTITUDE
# Uses the O6300 thrust curve
# Scales it up linearly


import numpy as np


base_curve = "Data/Inputs/thrustCurveO6300.csv"

total_impulse = 200000 # Ns

min_time = 3
max_time = 30

iterations = 10

for burn_time in np.linspace(min_time, max_time, iterations):
    # Create a new thrust curve with the new burn time
    average_thrust = total_impulse / burn_time
    scale_saved_curve("./Data/Inputs/thrustCurveO6300.csv", burn_time, average_thrust, f"./Data/Inputs/Temporary/generatedThrustCurve{burn_time}.csv")
    
    
