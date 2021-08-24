# Wait wouldn't it make a lot of sense to pass in moment of inertia as a CSV too
# Maybe moment of inertia should be its own class. It would be stored by the rocketMass and the rocketMass would pass in the necessary values whenever it needs to be calculated
# I think a functional programming style makes more sense in retrospect

# TODO: Remove mass needs to affect the moment of inertia class if it is calculated. It could just add a negative point mass


class RocketMass(PresetObject):
    """Aside from storing the rocket's mass, this class also deals with the rocket's moment of inertia and the center of gravity. There are other classes for determining the rocket's CG differently, but you have to pass an argument to change how moment of inertia is calculated, since that is mostly internal. 

    The main reason this is a separate class from the main rocket is to make it easier to implement different methods of passing in CG data"""

    def __init__(self, config={}):
        self.center_of_gravity = 2

        # Defaults to the constant one because we will definitely have enough information for it
        self.rocket_inertia = RocketInertia()

        super().overwrite_defaults(config)

    def get_mass(self):
        # This doesn't really need to be a function, I just made it one to fit in with the rest of the getters we have going on
        return self.mass

    def get_CG(self):
        return self.center_of_gravity

    def get_moment_of_inertia(self):
        return self.rocket_inertia.get_moment(self.mass)

    def remove_mass(self, amount, distance_from_nose):
        "Remove amount of mass from distance_from_nose. This method will update the mass, CG, and moment of inertia"

        # TODO: Implement
        # I think I'll figure out the complexities of which point the mass is removed from in the motor class. I can just have a function there that says 'get burn point' or something, which just returns the distance relative to the nose
        pass


class LookupMass(RocketMass):
    """This class replaces the constant center of gravity with a variable lookup in a CSV table.

    It expects a table with headers for CG at a given mass (?), I have no idea what the convention is for doing center of gravity this way (it could be time or mass or something to do with thrust)
    """

    def __init__(self, data_path, config={}):
        # Meters from the nose tip
        self.center_of_gravity_data = data_path

        # We are assuming that the CSV file will also contain information about the moment of inertia
        # If it doesn't, throw a very explicit error explaining that you have to override the rocket_inertia when creating it
        if ("data_path" in config.keys()):
            # If the user overrides the datapath for the inertia, then we use that one
            self.rocket_inertia = LookupInertia(config["data_path"])
        else:
            # Otherwise, we'll just stick with the same path as for the mass
            self.rocket_inertia = LookupInertia(data_path)

        super().overwrite_defaults(config)

        self.get_data()

    def get_data(self):
        # load in the specified csv file so that it can be accessed over and over again during the simulation
        pass

    def get_CG(self, mach):
        # Load it in from the variables
        pass


class CalculatedMass(RocketMass):
    "Simply allows the user to pass in dist-weight pairs and calculate them, other than that it is identical to the standard class. In the future I hope to make it so that it will simulate the sloshing of water based on the angle of flight, but this is a bit beyond the scope at the moment"

    def __init__(self, config={}):
        # Meters from the nose tip
        # I think that this one requires a list of several tuples of dist-weight pairs
        self.weights = [(2, 0.1), (3, 0.2), (4, 0.3)]

        self.rocket_inertia = CalculateInertia(self.weights)


        super().overwrite_defaults(config)


        # Calculate the cg and assign it to the variable



class RocketInertia(PresetObject):
    "Supplies a constant moment of inertia"

    def __init__(self, config={}):
        # Meters from the nose tip
        self.moment_of_inertia = 10

        super().overwrite_defaults(config)

    # The mass is only provided so that this rocketInertia can be called in the same way as its children
    def get_moment(self, mass=-1):
        return self.moment_of_inertia


class LookupInertia(RocketInertia):
    """
    Reads the moment of inertia from a CSV file based on the mass of the rocket
    """

    def __init__(self, datapath, config={}):
        # Meters from the nose tip
        # I think I need to require this argument
        self.center_of_gravity_data = ""

        super().overwrite_defaults(config)


        self.get_data()

    def get_data(self):
        # load in the specified csv file so that it can be accessed over and over again during the simulation
        pass

    def get_moment(self):
        pass


class CalculateInertia(RocketInertia):
    def __init__(self, weights, config={}):
        # I think we only need the centroid of the weight. That will have the same effect as taking the integral over the average

        super().overwrite_defaults(config)

    def get_moment(self, mass):
        # Atm it just uses a cylinder of uniform density as approximation, this is not a very good approximation

        pass
