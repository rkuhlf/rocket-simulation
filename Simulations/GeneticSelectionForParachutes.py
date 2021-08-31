from environment import Environment
from simulation import Simulation
from rocket import Rocket
from RocketParts.motor import Motor
from RocketParts.parachute import ApogeeParachute, Parachute
from logger import Feedback_Logger
import numpy as np
from random import random, normalvariate
from copy import deepcopy
import sys

sys.path.append(".")










def create_random_parachute():
    # Varying the CD and the area is pointless, since they are multiplied together the one time they are used
    if random() < 0.5:
        return ApogeeParachute({"radius": random() * 2})
    else:
        # Using on transonic data which only goes about 2000
        return Parachute(
            {"target_altitude": random() * 2000, "radius": random() * 2})


def create_random_rocket():
    parachutes = []

    # 1 percent chance of no parachutes (idk why, just feel like it)
    if random() > 0.01:
        parachutes.append(create_random_parachute())

        # 50 percent is two
        if random() < 0.5:
            parachutes.append(create_random_parachute())

            # 5 percent is 3
            if random() < 0.1:
                parachutes.append(create_random_parachute())

    return Rocket(environment=deepcopy(base_env), motor=deepcopy(base_motor),
                  parachutes=parachutes)



def fitness(landing_velocity, distance, num_parachutes):
    # Returns a combination of low speed and low distance away from the launch site
    # I also want to minimize the number of parachutes we have
    # Maybe I'll just make it zero if it lands too fast

    # In the future, I should probably also minimize max g-force and max Q

    # The plus five is just there to make it easier to have multiple parachutes
    return 0 if abs(landing_velocity) > 30 else 1 / (
        distance * (num_parachutes + 5))


def mutate(rocket):
    # atm we only have to adjust parachutes
    parachutes = rocket.parachutes

    if random() < 0.02:
        parachutes.append(create_random_parachute())

    if len(parachutes) == 0:
        return

    if random() < 0.02:
        random_index = int(random() * len(parachutes))
        del parachutes[random_index]

    if len(parachutes) == 0:
        return

    # 75% of the time we mutate the altitude a little bit
    if random() < 0.75:
        random_index = int(random() * len(parachutes))

        # Doesnt matter for apogee parachutes but also won't break them
        base_alt = parachutes[random_index].target_altitude
        parachutes[random_index].target_altitude = normalvariate(
            base_alt, base_alt * 0.07)

    # 50% of the time we mutate the area a little bit
    if random() < 0.5:
        random_index = int(random() * len(parachutes))

        # Doesnt matter for apogee parachutes but also won't break them
        base_radius = parachutes[random_index].radius
        parachutes[random_index].calculate_area(normalvariate(
            base_radius, base_radius * 0.07))

    # No return statement is required because no copies are made; all modification is in place


def mutated_simulation(sim):
    print("original parachute")
    print(sim.rocket.parachutes[0].radius)

    new_sim = deepcopy(sim)
    mutate(new_sim.rocket)

    print("new parachute")
    print(new_sim.rocket.parachutes[0].radius)


    return new_sim


# I think that the wind should be the same for all of them if they all use the same environment
base_env = Environment({"time_increment": 0.1})
base_motor = Motor()

num_rockets = 10
sims = []
fits = []

for i in range(num_rockets):
    new_rocket = create_random_rocket()
    # logger = Feedback_Logger(
    #     new_rocket,
    #     ['position', 'velocity', 'acceleration', 'rotation',
    #      'angular_velocity', 'angular_acceleration'])

    # logger.splitting_arrays = True
    sims.append(Simulation({}, deepcopy(base_env), new_rocket))

print("Initialized Rockets: ", sims)


for iteration in range(5):
    fits = []
    for sim in sims:
        print()
        print(sim.environment)
        print(sim.rocket)
        print(sim.rocket.parachutes)
        for para in sim.rocket.parachutes:
            print(para.radius, para.target_altitude)

        print(sim)
        sim.run_simulation()

        print("Rocket landed at %.2f m/s %.2f meters from where it started, using %d parachutes" %
              (sim.landing_speed(), sim.dist_from_start(), len(sim.rocket.parachutes)))
        fit = fitness(
            sim.landing_speed(),
            sim.dist_from_start(),
            len(sim.rocket.parachutes))

        # I dont understand why it doesn't work without this
        sim.reset()

        print("Calculated fitness is", str(fit))

        fits.append(fit)

    # apply the fitnesses so that the bottom 50 are deleted, the top 10 are kept, and 5 are randomly generated
    # The remaining 85 are created by a weighted random selection of the top 50, each of them with random mutations

    # First thing is to normalize the fits
    # I am just going to use a very simple normalization algorithm to start, settin everytin between 0 and 1
    fits = np.asarray(fits)
    min_fit = np.min(fits)
    max_fit = np.max(fits)
    fits = (fits - min_fit) / (max_fit - min_fit)

    cutoff = np.median(fits)

    fits = list(fits)

    for i in range(len(fits) - 1, 0, -1):
        if fits[i] < cutoff:
            del fits[i]
            del sims[i]

    new_sims = []

    sim_fit_pairs = sorted(zip(sims, fits), key=lambda pair: pair[1])


    for sim, fit in sim_fit_pairs[-2:]:
        sim.reset()
        new_sims.append(sim)

    for _ in range(1):
        new_rocket = create_random_rocket()

        new_sims.append(
            Simulation(
                {},
                deepcopy(base_env),
                new_rocket))


    fit_selector = []
    total_fit = 0
    # Generate selector data
    for sim, fit in sim_fit_pairs:
        total_fit += fit
        fit_selector.append((sim, total_fit))


    for _ in range(7):
        selection = random() * total_fit
        for sim, cumulative_fit in fit_selector:
            if selection < cumulative_fit:
                print("Appending mutated", sim)
                new_sims.append(mutated_simulation(sim))
                break

    print("NEW SIMULATIONS")
    print(len(new_sims))
    print(new_sims)

    sims = new_sims


print("FINAL SIMULATIONS")
for sim in sims:
    print(sim.rocket.parachutes)
    for parachute in sim.rocket.parachutes:
        print(parachute.radius)
        print(parachute.target_altitude)

    print()
