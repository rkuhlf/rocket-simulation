# The rocket's mass over time is actually going to be totally independent of the objects that provide the rocket's thrust and parachuting and nose cones and stuff
# This is bad in some ways because it means that the objects can be desynchronized, but it is good in some ways because it will cut way down on the code
# And it means that it will be slightly easier to make changes that other people have supplied



class MassObject:
    def __init__(self, mass, distance):
        self.mass = mass
        self.distance = distance

    def get_mass(self, time=0):
        return self.mass

    def get_distance(self, time=0):
        return self.distance

    def get_moment_of_inertia_contribution(self, center_of_gravity):
        # Assumes that the mass object is a node (infinitely small volume); should be okay and better than just using a cylinder
        return self.get_mass() * (self.get_distance() - center_of_gravity) ** 2


# Functions to calculate mass over time

# Functions to calculate the center of gravity over time


def total_moment_of_inertia(center_of_gravity, masses):
    # Return the primary axis moment of inertia for a cylinder
    total = 0

    for mass_object in masses:
        total += mass_object.get_moment_of_inertia_contribution(center_of_gravity)
        
    return total