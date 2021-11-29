# ITERATIVELY SOLVE THE GODDARD PROBLEM
# Repeating simulations multiple times, determine which thrust profile optimizes apogee with a given total impulse and no limits on thrust shape.
# The file uses an evolution-based implementation of a Monte Carlo algorithm, in which many rockets are generated, simulated, and then either saved, mutated, or randomized
# By the end, the best shape for thrust should be clear.
# Side note: the solution to this problem is not very important for hybrid rockets (a short explanation that I wrote is available at https://www.overleaf.com/read/gccgffsnzwhh). Nevertheless, I think it is an interesting application of a python sim.
# There is a slightly more relevant simulation under OptimizeBurnTime.py, which just scales the thrust profile linearly

# apply the fitnesses so that the bottom 50 are deleted, the top 10 are kept, and 5 are randomly generated
# The remaining 85 are created by a weighted random selection of the top 50, each of them with random mutations

# TODO: run this again for the redesigned simulation

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from random import random, normalvariate
from copy import deepcopy

import sys
sys.path.append(".")

from environment import Environment
from simulation import RocketSimulation
from rocket import Rocket
from RocketParts.motor import Motor


def create_random_motor(target_total_impulse, point_count=10):
    # Varying the CD and the area is pointless, since they are multiplied together the one time they are used
    # just going to use a constant number of points to approximate a curve. The thrust and time of each of the points will be completely random, then I will scale the motor to match a total impulse
    # The only funny business comes from deciding which axis to scale. If

    # Create a pandas dataframe with the random points
    data = np.random.uniform(size=(point_count, 2))
    data[0] = [0, 0]
    data[-1] = [1, 0]
    data = pd.DataFrame(data, columns=["time", "thrust"])
    data = data.sort_values(by=['time'], ignore_index=True)
    

    # Instantiate the motor from the dataframe
    motor = Motor()

    motor.set_thrust_data(data)

    # Scale the data frame to the normally distributed random burn time
    motor.scale_time(max(normalvariate(6, 2), 0.1))
    # Scale the thrust to match
    current_total = motor.get_total_impulse()
    motor.scale_thrust(target_total_impulse / current_total)

    return motor


def create_random_rocket(target_total_impulse):
    motor = create_random_motor(target_total_impulse)

    return Rocket(environment=deepcopy(base_env), motor=motor)



def fitness(apogee):
    # This should really just have the rocket as a parameter
    # Returns a combination of low speed and low distance away from the launch site
    # I also want to minimize the number of parachutes we have
    # Maybe I'll just make it zero if it lands too fast

    # In the future, I should probably also minimize max g-force and max Q

    # The plus five is just there to make it easier to have multiple parachutes
    return apogee


def mutate(rocket):
    motor = rocket.motor
    # There is a side effect here that I need to get rid of
    data = deepcopy(motor.thrust_data)
    current_burn_time = motor.get_burn_time()
    target_total_impulse = motor.get_total_impulse()

    for index, row in data.iterrows():
        row["thrust"] *= normalvariate(1, 0.5)
        row["thrust"] = max(0, row["thrust"])

        row["time"] += normalvariate(0, 0.05)
        if row["time"] < 0:
            row["time"] = -row["time"]
        if row["time"] > 1:
            row["time"] = 2 - row["time"]

    data["time"][:1] = [0]
    data["thrust"][:1] = [0]

    data["time"][-1:] = [1]
    data["thrust"][-1:] = [0]
    

    data = data.sort_values(by=['time'], ignore_index=True) 
        


    m = Motor()

    m.set_thrust_data(data)

    # Scale the data frame to the normally distributed random burn time
    m.scale_time(current_burn_time * normalvariate(1, 0.05))
    # Scale the thrust to match
    current_total = m.get_total_impulse()
    m.scale_thrust(target_total_impulse / current_total)

    return m

    # No return statement is required because no copies are made; all modification is in place

def mutated_simulation(sim):
    print("Original rocket motor for mutation", sim.rocket.motor.thrust_data)
    new_sim = sim.copy()
    new_sim.rocket.motor = mutate(new_sim.rocket)
    new_sim.update_saved_state()

    print("Original rocket motor; should be the same", sim.rocket.motor.thrust_data)
    print("New rocket motor for mutation", new_sim.rocket.motor.thrust_data)

    return new_sim


if __name__ == "__main__":
    base_env = Environment(time_increment=0.1, apply_wind=False)
    total_impulse = 100000

    num_rockets = 2

    num_iterations = 1
    sims = []
    fits = []
    average_fits = []
    collective_fits = []

    for i in range(num_rockets):
        new_rocket = create_random_rocket(total_impulse)
        sims.append(RocketSimulation(environment=deepcopy(base_env), rocket=new_rocket))


    for iteration in range(num_iterations):
        
        fits = []
        for i in range(len(sims)):
            sim = sims[i]
            sim.run_simulation()
            
            try:
                fit = fitness(sim.apogee())
            except Exception as e:
                fit = 0

            print("Simming ", sim.rocket.motor.thrust_data)
            print("It has ", sim.rocket.motor.get_total_impulse())
            print(f"Sim index {i} has fitness", str(fit))

            fits.append(fit)


        # First thing is to normalize the fits
        # I am just going to use a very simple normalization algorithm to start, settin everytin between 0 and 1. Actually this doesn't work very well when one of the rockets is a total failure. Switching to traditional z-score normalization
        collective_fits.append(sorted(fits))
        fits = np.asarray(fits)
        print("AVERAGE FITNESS", np.average(fits))
        average_fits.append(np.average(fits))
        fits -= np.average(fits)
        fits /= np.std(fits)

        # should take about the top 25%
        cutoff = 0

        fits = list(fits)
        # loop in lists backwards, deleting bad ones
        # Sometimes this deletes the wrong one. It deletes the best
        for i in range(len(fits) - 1, -1, -1):
            if fits[i] < cutoff:
                print(f"Deleting fits index {i} because its fitness is too low")
                del fits[i]
                del sims[i]
            else:
                # all of the sims have to be reset at some point anyways
                sims[i].reset()

        # adjust the weighting mechanism to favor better motors more
        for i in range(len(fits)):
            fits[i] = fits[i] ** 10

        new_sims = []

        sim_fit_pairs = sorted(zip(sims, fits), key=lambda pair: pair[1])


        print(f"there are only {len(sim_fit_pairs)} rockets left")

        target_reserved_rockets = num_rockets * 0.2
        current_index = len(sim_fit_pairs) - 1
        while (len(new_sims) < target_reserved_rockets):
            sim_to_add, fit = sim_fit_pairs[current_index]
            sim.reset()
            new_sims.append(deepcopy(sim_to_add))

            current_index -= 1
            if current_index == -1:
                current_index = len(sim_fit_pairs) - 1
            
        
        fit_selector = []
        total_fit = 0
        # Generate selector data
        for sim, fit in sim_fit_pairs:
            total_fit += fit
            fit_selector.append((sim, total_fit))

        for _ in range(round(num_rockets * 0.7)):
            selection = random() * total_fit * 1.5 # scaling factor to select higher
            appended = False
            for sim, cumulative_fit in fit_selector:
                if selection < cumulative_fit:
                    # print("Appending mutated", sim)
                    new_sims.append(mutated_simulation(sim))
                    appended = True
                    break
            if not appended:
                new_sims.append(mutated_simulation(sims[-1]))
            print("mutated appendage", new_sims[-1].rocket.motor.thrust_data)

        for _ in range(num_rockets - len(new_sims)):
            print("Randomly generating")
            new_rocket = create_random_rocket(total_impulse)

            new_sims.append(
                RocketSimulation(
                    {},
                    deepcopy(base_env),
                    new_rocket))

        # print("NEW SIMULATIONS")
        print(len(new_sims))
        # print(new_sims)

        sims = new_sims


    
    fits = []
    for i in range(len(sims)):
        sim = sims[i]
        sim.run_simulation()
        
        try:
            fit = fitness(sim.apogee())
        except Exception as e:
            fit = 0

        # I dont understand why it doesn't work without this
        sim.reset()

        # print("Calculated fitness is", str(fit))

        fits.append(fit)

    sim_fit_pairs = sorted(zip(sims, fits), key=lambda pair: pair[1])
    
    print("FINAL SIMULATIONS")
    for sim, fit in sim_fit_pairs[-round(0.2 * num_rockets):]:
        data = sim.rocket.motor.thrust_data
        thrust_scale = sim.rocket.motor.thrust_multiplier
        time_scale = sim.rocket.motor.time_multiplier
        # print(data)

        plt.plot(np.asarray(data["time"]) * time_scale, np.asarray(data["thrust"] * thrust_scale), alpha=0.1)


    plt.show()

    top_fits = []
    for trial in collective_fits:
        top_fits.append(np.average(trial[-round(num_rockets * 0.2):]))

    collective_fits = np.transpose(np.asarray(collective_fits))

    for percentile in collective_fits:
        plt.plot(range(len(percentile)), percentile)
    plt.show()

    

    plt.plot(range(num_iterations), average_fits)
    plt.plot(range(num_iterations), top_fits)
    plt.show()

    print("Apparently, the best rocket thrust profile is as follows:")
    best = sim_fit_pairs[-1][0].rocket.motor
    data = best.thrust_data
    data['time'] *= best.time_multiplier
    data['thrust'] *= best.thrust_multiplier
    print(data)
    print("It had a fitness of", sim_fit_pairs[-1][1])
    

# Generated:
'''
0  0.000000     0.000000
1  1.256881  1107.605155
2  1.912713  2879.295138
3  2.669230     0.000000
It had a fitness of 1683.801762261541
'''

'''
0  0.000000     0.000000
1  0.160235    32.031430
2  0.460823  6420.931929
3  1.121207     0.000000
It had a fitness of 1644.529439212358 (confirmed by regular sim)
'''

'''
0  0.000000     0.000000
1  0.386891   856.287747
2  1.694458  2961.528633
3  1.985442     0.000000
It had a fitness of 1738.779290500912
'''
'''
0  0.000000      0.000000
1  0.204627     49.527358
2  0.256816   6003.019970
3  0.395159   2205.838998
4  0.741824   2256.975580
5  0.839057      0.000000
6  0.901387  37289.365676
7  0.917359      0.000000
8  1.206704    108.740455
9  1.258324      0.000000
It had a fitness of 2199.805851873474
'''