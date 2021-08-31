import sys
sys.path.append(".")


from Helpers.general import angles_from_vector_3d
from numpy import array
from simulation import Simulation
from logger import Feedback_Logger  # , Logger
from RocketParts.parachute import Parachute
from rocket import Rocket
from RocketParts.motor import Motor
from environment import Environment




# Find best launch angle based on a constant wind speed

# It is trivial to determine that you should be launching either directly into or directly away from the wind
# Uses mostly class defaults
env = Environment({"time_increment": 0.01})
motor = Motor()
parachute = Parachute()
rocket = Rocket(environment=env, motor=motor, parachutes=[parachute])

sim = Simulation({}, env, rocket)

air_direction = angles_from_vector_3d(env.get_air_speed())[0]

# Very basic optimization program, it will get stuck in local minimums
# If you want to optimize it the other direction, you will have to make this negative
# 54 -> 0.37
learning_rate = 0.001
start_angle = -0.4

rocket.rotation = array([air_direction, start_angle], dtype="float64")

p_distance_from_start = -1
distance_from_start = -1
i = 0
print("Initialized simulation")
while distance_from_start <= p_distance_from_start or p_distance_from_start == -1:
    print(rocket.rotation)
    p_distance_from_start = distance_from_start

    sim.run_simulation()

    distance_from_start = (
        rocket.position[0] ** 2 + rocket.position[1] ** 2) ** (1 / 2)
    sim.reset()

    rocket = sim.rocket

    print(
        str(start_angle + i * learning_rate) + " angle completed: ",
        distance_from_start)


    i += 1
    rocket.rotation = array(
        [air_direction, start_angle + i * learning_rate],
        dtype="float64")

print(str(air_direction) + ", " + str(start_angle + (i - 2)
                                      * learning_rate) + " is the best angle")
