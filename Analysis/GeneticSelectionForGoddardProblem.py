# ITERATIVELY SOLVE THE GODDARD PROBLEM
# Repeating simulations multiple times, determine which thrust profile optimizes apogee with a given total impulse and no limits on thrust shape.
# The file uses an evolution-based implementation of a Monte Carlo algorithm, in which many rockets are generated, simulated, and then either saved, mutated, or randomized
# By the end, the best shape for thrust should be clear.
# Side note: the solution to this problem is not very important for hybrid rockets (a short explanation that I wrote is available at https://www.overleaf.com/read/gccgffsnzwhh). Nevertheless, I think it is an interesting application of a python sim.
# There is a slightly more relevant simulation under OptimizeBurnTime.py, which just scales the thrust profile linearly

# apply the fitnesses so that the bottom 50 are deleted, the top 10 are kept, and 5 are randomly generated
# The remaining 85 are created by a weighted random selection of the top 50, each of them with random mutations


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from random import random, normalvariate
from copy import deepcopy

from environment import Environment
from simulation import RocketSimulationToApogee
# from rocket import Rocket
from Simulations.DesignedRocket import get_rocket
from RocketParts.motor import Motor


#region Global Variables
# FIXME: once I have debugged this, I want to change it back to use the wind
base_env = Environment(time_increment=1, apply_wind=False)
total_impulse = 120000
num_rockets = 6
# The leftover fraction is randomly generated
fraction_mutated = 0.75
fraction_copied = 0.2
cutoff = 0.3

num_iterations = 4
#endregion


def create_random_motor(target_total_impulse, point_count, mean_burn_time=20, std_burn_time=5):
    # Varying the CD and the area is pointless, since they are multiplied together the one time they are used
    # just going to use a constant number of points to approximate a curve. The thrust and time of each of the points will be completely random, then I will scale the motor to match a total impulse

    # Create a pandas dataframe with points with random x, y values that will be scaled
    data = np.random.uniform(size=(point_count, 2))
    data[0] = [0, 0]
    data[-1] = [1, 0]
    data = pd.DataFrame(data, columns=["time", "thrust"])
    data = data.sort_values(by=['time'], ignore_index=True)
    

    # Instantiate the motor from the dataframe
    motor = Motor()

    motor.set_thrust_data(data)

    # Scale the data frame to the normally distributed random burn time
    motor.scale_time(max(normalvariate(mean_burn_time, std_burn_time), 0.1))
    # Scale the thrust to match
    current_total = motor.get_total_impulse()
    motor.scale_thrust(target_total_impulse / current_total)

    return motor

def create_random_rocket(target_total_impulse, point_count=10):
    motor = create_random_motor(target_total_impulse, point_count)

    r = get_rocket()[0]
    r.environment = deepcopy(base_env)
    r.motor = motor

    return r

def create_simulation(rocket):
    "Add the constant environment"

    # Do not stop on errors, that way falling directly into the ground does not crash the entire program
    return RocketSimulationToApogee(rocket=rocket, environment=deepcopy(base_env), logger=None, stop_on_error=False)


def fitness(simulation: RocketSimulationToApogee):
    apogee = simulation.apogee

    if apogee is None:
        print(f"A rocket never recorded an apogee.")
        return 0
    
    return apogee

def weight_fits(sim_fit_pairs, exponent=4):
    # adjust the weighting mechanism to favor better motors more (https://www.desmos.com/calculator/guxyrwrwk2)
    for i in range(len(sim_fit_pairs)):
        f = sim_fit_pairs[i][1]
        sim_fit_pairs[i][1] = np.sign(f) * f ** exponent

    return sim_fit_pairs

def normalize(sim_fit_pairs):
    "Normalize in-place with traditional z-scores"
    if len(sim_fit_pairs) == 1:
        sim_fit_pairs[1] = 0
    
    fits = np.asarray(sim_fit_pairs)[:, 1]
    avg = np.average(fits)
    std = np.std(fits)

    for i in range(len(sim_fit_pairs)):
        sim_fit_pairs[i][1] = (sim_fit_pairs[i][1] - avg) / std
    
    return sim_fit_pairs

def delete_worst(sim_fit_pairs, z_cutoff=0):
    # a z_custoff of 0 should take about the top 50%

    # loop in lists backwards (so that deletion works), deleting bad ones
    for i in range(len(fits) - 1, -1, -1): # -1 because exclusive
        if sim_fit_pairs[i][1] < z_cutoff:
            print(f"Deleting fits index {i} because its fitness is too low")
            del sim_fit_pairs[i]

    return sim_fit_pairs


def mutate(motor: Motor):
    data = deepcopy(motor.thrust_data)
    current_burn_time = motor.get_burn_time()

    for index, row in data.iterrows():
        # You cannot just do a basic multiplication because it will get stuck at zero
        row["thrust"] = normalvariate(row["thrust"] , 0.05)
        row["thrust"] = max(0, row["thrust"])

        row["time"] += normalvariate(0, 0.05)
        if row["time"] < 0:
            row["time"] = -row["time"]
        if row["time"] > 1:
            row["time"] = 2 - row["time"]

    data = data.sort_values(by=['time'], ignore_index=True) 

    first = data.iloc[0]
    first["time"] = 0
    first["thrust"] = 0

    last = data.iloc[-1]
    last["time"] = 1
    last["thrust"] = 0
    


    m = Motor()
    m.set_thrust_data(data)

    # Scale the data frame to the normally distributed random burn time
    m.scale_time(current_burn_time * normalvariate(1, 0.15))
    # Scale the thrust to match
    current_total = m.get_total_impulse()
    m.scale_thrust(total_impulse / current_total)

    return m

def mutated_simulation(sim):
    # print("Original rocket motor for mutation", sim.rocket.motor.thrust_data)
    new_rocket = get_rocket()[0]
    new_rocket.motor = mutate(sim.rocket.motor)
    # print("New rocket motor after mutation", new_rocket.motor.thrust_data)

    return create_simulation(new_rocket)


def generate_random_rockets(target_array: "list[RocketSimulationToApogee]", count: int):
    for _ in range(count):
        print("Randomly generating")
        new_rocket = create_random_rocket(total_impulse)

        target_array.append(create_simulation(new_rocket))

def generate_copied_rockets(target_array: "list[RocketSimulationToApogee]", count: int, sim_fit_pairs):
    """Accepts a sorted list of sim_fit_pairs, then adds until the desired number is reached, looking back to repeat rockets if necessary"""

    added = 0
    end = len(sim_fit_pairs) - 1
    current_index = end

    while added < count:
        sim_to_add, fit = sim_fit_pairs[current_index]
        target_array.append(sim_to_add)

        added += 1
        current_index -= 1
        # If we have reached the beginning, go back to the end. Only necessary if it loops through twice
        # Otherwise python automatically works with negative indices
        if current_index == -1:
            current_index = end

def generate_mutated_rockets(target_array: "list[RocketSimulationToApogee]", count: int, sim_fit_pairs, scaling_factor=1.5):
    # Generate selector data
    fit_selector = []
    total_fit = 0
    max_fit = 0
    for sim, fit in sim_fit_pairs:
        total_fit += fit
        max_fit = max(max_fit, fit)
        fit_selector.append((sim, total_fit))


    for _ in range(count):
        # scaling factor weights the best rocket much more
        selection = random() * total_fit * scaling_factor 
        appended = False

        for sim, cumulative_fit in fit_selector:
            if selection < cumulative_fit:
                target_array.append(mutated_simulation(sim))
                appended = True
                break
        
        # This will happen a lot depending on the scaling factor. If we selected too big, just add the best rocket
        if not appended:
            target_array.append(mutated_simulation(sims[-1]))



def run_simulations(sims: "list[RocketSimulationToApogee]", fits: list):
    print("RUNNING SIMULATIONS")
    for i, sim in enumerate(sims):
        print(f"Simming {sim.rocket.motor.thrust_data} with {sim.rocket.motor.get_total_impulse()} Ns")

        sim.run_simulation()
        fit = fitness(sim)
        fits.append(fit)

        print(f"Sim index {i} has fitness {fit}")

    tuples = sorted(zip(sims, fits), key=lambda pair: pair[1])
    # Return a list of tuples, the sim_fit_pairs
    return [list(x) for x in tuples]


def graph_sim_thrust(sim, **kwargs):
    data = sim.rocket.motor.thrust_data
    thrust_scale = sim.rocket.motor.thrust_multiplier
    time_scale = sim.rocket.motor.time_multiplier

    plt.plot(np.asarray(data["time"]) * time_scale, np.asarray(data["thrust"] * thrust_scale), **kwargs)


BEST_CURVES = "Best Curves"
ALL_CURVES = "All Curves"
PERCENTILES = "Percentiles"
PROGRESSION = "Progression"


def initialize_figs():
    figs = []

    figs.append(plt.figure(BEST_CURVES))
    plt.title("Best Thrust Curves")
    plt.xlabel("Time [s]")
    plt.ylabel("Thrust [N]")
    plt.legend()


    figs.append(plt.figure(ALL_CURVES))
    plt.title("All Thrust Curves")
    plt.xlabel("Time [s]")
    plt.ylabel("Thrust [N]")


    figs.append(plt.figure(PERCENTILES))
    plt.title("Progression of Simulation Percentiles")
    plt.xlabel("Iteration Number")
    plt.ylabel("Fitness")

    figs.append(plt.figure(PROGRESSION))
    plt.title("Overall Progression")
    plt.xlabel("Iteration Number")
    plt.ylabel("Average Fitness")
    plt.legend()

    return figs


# Just call this display results function after every single iteration
def display_best(sim_fit_pairs: "list[tuple[RocketSimulationToApogee, float]]", cutoff):
    count = int(np.ceil(cutoff * num_rockets))
    
    plt.figure(BEST_CURVES)
    for sim, fit in sim_fit_pairs[-count:]:
        graph_sim_thrust(sim, alpha=1/np.sqrt(count))
    
    best = sim_fit_pairs[-1][0]
    graph_sim_thrust(best, label="Best")

    print("Apparently, the best rocket thrust profile is as follows:")
    print(best.rocket.motor.thrust_data)
    print("It had a fitness of", sim_fit_pairs[-1][1])


def display_all(sim_fit_pairs):
    plt.figure(ALL_CURVES)

    for sim, fit in sim_fit_pairs:
        graph_sim_thrust(sim)


def display_progression(collective_fits, cutoff):
    top_fits = []
    average_fits = []

    plt.figure(PROGRESSION)
    for trial in collective_fits:
        top_fits.append(np.average(trial[-round(num_rockets * cutoff):]))
        average_fits.append(np.average(trial))

    collective_fits = np.transpose(np.asarray(collective_fits))

    fig = plt.figure(PERCENTILES)
    # Plot how the best rocket progressed over time, then the second best progressed over time, and so on
    for percentile in collective_fits:
        plt.plot(range(len(percentile)), percentile)

    simulated_so_far = len(average_fits)
    plt.plot(range(simulated_so_far), average_fits, label="Average")
    plt.plot(range(simulated_so_far), top_fits, label="Top")
    fig.canvas.draw()



shown = False
def display_results(collective_fits, sim_fit_pairs, cutoff=0.2):
    global shown
    figs = initialize_figs()
    if not shown:
        plt.show(False)
        shown = True

    print("FINAL SIMULATIONS")
    display_best(sim_fit_pairs, cutoff)

    display_all(sim_fit_pairs)

    print("PROGRESSION")
    display_progression(collective_fits, cutoff)

    plt.draw()


if __name__ == "__main__":
    sims: "list[RocketSimulationToApogee]" = []
    fits = []
    collective_fits = []

    generate_random_rockets(sims, num_rockets)

    for iteration in range(num_iterations):
        fits = []
        sim_fit_pairs = run_simulations(sims, fits)
        display_results(collective_fits, sim_fit_pairs, cutoff)

        fits: np.ndarray = np.asarray(fits)
        
        print("AVERAGE FITNESS", fits.mean())

        # Storing the fitness of every iteration in an array
        collective_fits.append(sorted(fits))


        sim_fit_pairs = normalize(sim_fit_pairs)

        sim_fit_pairs = delete_worst(sim_fit_pairs)
        print(f"There are only {len(sim_fit_pairs)} rockets left")

        sim_fit_pairs = weight_fits(sim_fit_pairs)

        new_sims = []
        generate_copied_rockets(new_sims, round(num_rockets * fraction_copied), sim_fit_pairs)
        generate_mutated_rockets(new_sims, round(num_rockets * fraction_mutated), sim_fit_pairs)
        generate_random_rockets(new_sims, num_rockets - len(new_sims))

        # print("NEW SIMULATIONS")
        print(f"We have ended up with {len(new_sims)}")
        # print(new_sims)

        sims = new_sims


    
    fits = []
    sim_fit_pairs = run_simulations(sims, fits)
    
    display_results(collective_fits, sim_fit_pairs, cutoff)

    plt.show()
    
    

#region Generated:
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
#endregion