import sys
sys.path.append(".")

from Helpers.massProperties import MassObject

# Everything is in kilograms and meters

nose_cone = MassObject(10, 1)

loaded_parachutes = MassObject(1, 1)

avionics = MassObject(0.3, 1)

ox_tank = MassObject(20, 5)
# TODO: write reasonable linear approximations based on my equilibrium model of the ox tank
ox_tank.get_mass = lambda time=0 : time**2
ox_tank.get_distance = lambda time=0 : time**2


injector = MassObject(1, 1)


fuel_grain = MassObject(3, 5)

# Not sure if I sshould have this be a variable mass since it is an ablative, maybe we are just assuming that the change is negligible
phenolic = MassObject(0.4, 5)

fins = MassObject

nozzle = MassObject(2, 6)