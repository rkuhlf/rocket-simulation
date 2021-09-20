import sys
sys.path.append(".")

from environment import Environment
from simulation import Simulation
from rocket import Rocket
from RocketParts.motor import Motor
from RocketParts.parachute import ApogeeParachute, Parachute
from logger import Feedback_Logger
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from random import random, normalvariate
from copy import deepcopy

import time


def create_random_motor(target_total_impulse, point_count):
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


def create_random_rocket():
    motor = create_random_motor(3092.55, 4)

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
    # atm we only have to adjust parachutes
    data = rocket.motor.thrust_data
    current_burn_time = rocket.motor.get_burn_time()
    target_total_impulse = rocket.motor.get_total_impulse()

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

    rocket.motor = m

    # No return statement is required because no copies are made; all modification is in place


def mutated_simulation(sim):
    new_sim = deepcopy(sim)
    mutate(new_sim.rocket)

    return new_sim


if __name__ == "__main__":
    '''
    m = create_random_motor(2400)
    print(m.get_total_impulse())

    d = m.thrust_data

    plt.plot(d["time"], d["thrust"])
    plt.show()
    '''


    base_env = Environment({"time_increment": 0.1, "apply_wind": False})

    num_rockets = 10
    num_iterations = 5
    sims = []
    fits = []
    average_fits = []
    collective_fits = []

    for i in range(num_rockets):
        new_rocket = create_random_rocket()
        logger = Feedback_Logger(
            new_rocket,
            ['position', 'velocity', 'acceleration'], target="GoddardSim" + str(i) + ".csv")

        logger.splitting_arrays = True
        sims.append(Simulation({}, deepcopy(base_env), new_rocket, logger=logger))

    # print("Initialized Rockets: ", sims)


    for iteration in range(num_iterations):
        
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

        # apply the fitnesses so that the bottom 50 are deleted, the top 10 are kept, and 5 are randomly generated
        # The remaining 85 are created by a weighted random selection of the top 50, each of them with random mutations

        # First thing is to normalize the fits
        # I am just going to use a very simple normalization algorithm to start, settin everytin between 0 and 1. Actually this doesn't work very well when one of the rockets is a total failure. Switching to traditional z-score normalization
        collective_fits.append(sorted(fits))
        fits = np.asarray(fits)
        print("AVERAGE FITNESS", np.average(fits))
        average_fits.append(np.average(fits))
        fits -= np.average(fits)
        fits /= np.std(fits)

        # should take about the top 25%
        cutoff = 1.5

        fits = list(fits)
        # loop in lists backwards, deleting bad ones
        for i in range(len(fits) - 1, 0, -1):
            if fits[i] < cutoff:
                del fits[i]
                del sims[i]

        # adjust the weighting mechanism to favor better motors more
        for i in range(len(fits)):
            fits[i] = fits[i] ** 10

        new_sims = []

        sim_fit_pairs = sorted(zip(sims, fits), key=lambda pair: pair[1])


        # FIXME: For some reason, the highest one does not fly the same height every time
        # Probably because the rocket is being mutated, changing this one as well as the other one
        # Actually my best guess now is that it is an issue with the environment. I can't figure out why the 'same' rocket is flying different heights. Maybe I should make a simpler test case of this
        for sim, fit in sim_fit_pairs[round(-num_rockets * 1):]:

            sim.reset()
            new_sims.append(deepcopy(sim))

        print(new_sims[-1].rocket.motor.thrust_data)
        
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

        for _ in range(num_rockets - len(new_sims)):
            new_rocket = create_random_rocket()

            new_sims.append(
                Simulation(
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
    # TODO: probably just do top 50%
    for sim, fit in sim_fit_pairs[-round(0.2 * num_rockets):]:
        data = sim.rocket.motor.thrust_data
        thrust_scale = sim.rocket.motor.thrust_multiplier
        time_scale = sim.rocket.motor.time_multiplier
        # print(data)

        plt.plot(np.asarray(data["time"]) * time_scale, np.asarray(data["thrust"] * thrust_scale), alpha=0.1)

    plt.show()

    collective_fits = np.transpose(np.asarray(collective_fits))

    for percentile in collective_fits:
        plt.plot(range(len(percentile)), percentile)
    plt.show()

    print(average_fits)
    plt.plot(range(num_iterations), average_fits)
    plt.show()
    
