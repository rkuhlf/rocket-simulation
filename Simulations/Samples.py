


"""
# Fire the rocket from four different angles so that I'm sure it goes the correct way each time
rotations = [
    array([0.2, 0.1], dtype="float64"),
    array([2.7, 0.1], dtype="float64"),
    array([3.2, 0.1], dtype="float64"),
    array([5.0, 0.1], dtype="float64")]

i = 0
for rot in rotations:
    i += 1
    env = Environment({"time_increment": 0.01})
    motor = Motor()
    parachute = Parachute()
    rocket = Rocket({'rotation': rot.copy()}, environment=env,
                    motor=motor, parachute=parachute)

    logger = RocketLogger(
        rocket,
        ['position', 'velocity', 'acceleration', 'rotation',
         'angular_velocity', 'angular_acceleration'],
        target='outputRot' + str(i) + '.csv')

    logger.splitting_arrays = True

    sim = RocketSimulation({}, env, rocket, logger)
    sim.run_simulation()
"""

# Example 1
"""
environment = Environment()
motor = Motor()
rocket = Rocket(environment=environment, motor=motor)


logger = RocketLogger(
    rocket,
    ['position', 'velocity', 'acceleration', 'rotation',
     'angular_velocity', 'angular_acceleration'])
rocket.logger = logger

sim = RocketSimulation(environment, rocket, logger)

sim.run_simulation()
"""


# Example 2
"""
rocket = Rocket()
rocket.load_preset("TannerModel")


logger = Logger(rocket, ['position', 'rotation'])

sim = RocketSimulation(rocket.environment, rocket, logger)

sim.run_simulation()
"""
