# MASS OBJECT CLASS

import sys
sys.path.append(".")

from Helpers.data import DataType
from preset_object import PresetObject


class MassObject(PresetObject):
    """
    Everything that has mass on the rocket should inherit from this class
    Aside from storing the mass, this class also deals with the moment of inertia and the center of gravity. 

    With moment of inertia, all items are assumed to be flat-headed cylinders with uniformly distributed mass
    """

    def __init__(self, config={}, simulation=None):
        # This has the nice side effect that everything has access to the simulation now
        self.simulation = simulation

        # This mass does not include the mass of all of the subobjects located in here
        self.mass = 0

        # This is the distance from the front of the parent object that the front of this object is located
        self.front = 0

        # Once again, this number is for the mass of this object only, the actual center of gravity is calculated differently
        # This is the distance from the local front
        self.center_of_gravity = 0

        self.mass_objects = []

        self.mass_data_type = DataType.DEFAULT
        self.CG_data_type = DataType.DEFAULT
        self.moment_data_type = DataType.DEFAULT

        super().overwrite_defaults(config)

    @property
    def total_mass(self):
        if self.mass_data_type == DataType.DEFAULT:
            total = self.mass
            for mass_object in self.mass_objects:
                # This is the part that means you have to make sure not to double count objects
                # There is a potential fix where you just pass mass_objects up the chain and check for duplicates, but I don't want to do it
                total += mass_object.total_mass
            
            return total
        
        if self.mass_data_type == DataType.CONSTANT:
            return self.mass

        if self.mass_data_type == DataType.FUNCTION_TIME:
            return self.mass_given_time(self.simulation.environment.time)            


    def mass_given_time(self, time):
        raise NotImplementedError("If you are going to use a custom function for the mass over the time, you have to specify it by using 'set_mass_as_function_of_time'")

    def set_mass_as_function_of_time(self, function):
        self.mass_data_type = DataType.FUNCTION_TIME
        self.mass_given_time = function

    def set_mass_constant(self, value):
        self.mass_data_type = DataType.CONSTANT
        self.mass = value


    @property
    def total_CG(self, local=False):
        if self.CG_data_type == DataType.DEFAULT:
            current_CG = self.center_of_gravity
            current_CG_mass_weight = self.mass

            for mass_object in self.mass_objects:
                current_CG = (current_CG * current_CG_mass_weight + mass_object.total_mass * mass_object.total_CG) / (mass_object.total_mass + current_CG_mass_weight)
                current_CG_mass_weight += mass_object.total_mass

            # If we are wanting the CG of this relative to a parent object, we need to add the distance from the front of the parent object that we are at
            if not local:
                current_CG += self.front

            return current_CG

        if self.CG_data_type == DataType.CONSTANT:
            return self.center_of_gravity
        
        if self.CG_data_type == DataType.FUNCTION_TIME:
            return self.CG_given_time(self.simulation.environment.time)

    def CG_given_time(self, time):
        raise NotImplementedError("If you are going to use a custom function for the CG over the time, you have to specify it by using 'set_CG_as_function_of_time'")

    def set_CG_as_function_of_time(self, function):
        self.CG_data_type = DataType.FUNCTION_TIME
        self.CG_given_time = function

    def set_CG_constant(self, value):
        self.CG_data_type = DataType.CONSTANT
        self.center_of_gravity = value


    @property
    def total_moment_of_inertia(self):
        if self.moment_data_type == DataType.DEFAULT:
            # Right now, there are no individual moments of inertia anyways, but I will keep the convention
            total_moment = 0
            total_CG = self.total_CG

            # This one is much harder. We have to go through every single child individually, we can't do it recursively
            all_mass_subobjects = self.flattened_mass_objects
            for CG_from_front, mass_object in all_mass_subobjects:
                # Notice that here we have to use the single mass of the object, not the total of the subobjects
                total_moment += mass_object.mass * (CG_from_front - total_CG) ** 2

            return total_moment

    
        if self.moment_data_type == DataType.CONSTANT:
            # Notice that it is not set by default, so it will throw an error if you don't override it
            return self.moment_of_inertia
        
        if self.moment_data_type == DataType.FUNCTION_TIME:
            return self.moment_given_time(self.simulation.environment.time)

    def moment_given_time(self, time):
        raise NotImplementedError("If you are going to use a custom function for the moment of inertia over the time, you have to specify it by using 'set_moment_as_function_of_time'")

    def set_moment_as_function_of_time(self, function):
        self.moment_data_type = DataType.FUNCTION_TIME
        self.moment_given_time = function

    def set_moment_constant(self, value):
        self.moment_data_type = DataType.CONSTANT
        self.moment = value

    def get_flattened_mass_objects(self, distance_from_original_front):
        flattened = [(distance_from_original_front + self.front + self.center_of_gravity, self)]

        for mass_object in self.mass_objects:
            newly_flattened = mass_object.get_flattened_mass_objects(distance_from_original_front + self.front)
            flattened.extend(newly_flattened)
        
        return flattened

    @property
    def flattened_mass_objects(self, distance_from_original_front=0):
        """
        Return a flattened array of all of tuples of the mass objects that are underneath this
        First index is the CG distance from the start
        Second index is the actual mass object without any parent information
        """
        return self.get_flattened_mass_objects(distance_from_original_front)
        