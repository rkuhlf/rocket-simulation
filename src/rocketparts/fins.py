# FIN CLASSES
# Fins are basically just a mass object with a few additional evaluation methods.
# Since all of the drag data on the rocket is determined by a CD lookup, it is not necessary to include a fin object, but I want one anyways just for some fin flutter stuff
# Note that all of the masses on the fins are determined by a density per area


import numpy as np

from helpers.general import constant
from rocketparts.massObject import MassObject


def trapezoidal_area(fins: "Fins"):
    return (fins.root + fins.tip) / 2 * fins.height


def basic_fin_density_closure(density=2700):
    def basic_fin_density(fins: "Fins"):
        return fins.area * fins.count * fins.thickness * density
    
    return basic_fin_density


# TODO: write an abstract class with a basic init defined for the Fins

class Fins(MassObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # CR	=	fin root chord
        self.root = 0.381
        # CT	=	fin tip chord
        self.tip = 0.127
        # S	=	fin semispan
        self.height = 0.127
        
        self.sweep = 0.254

        self.thickness = 0.009525

        # N	=	number of fins
        self.count = 4

        # Arbitrarily set to 2 kg
        self.mass_function = basic_fin_density_closure()
        # Area function for a single fin
        self.area_function = trapezoidal_area

        super().overwrite_defaults(**kwargs)
    
    @property
    def area(self):
        return self.area_function(self)

    @property
    def mass(self):
        return self.mass_function(self)
    
    @mass.setter
    def mass(self, m):
        # You cannot set the mass
        pass





# Elliptical fin class





# Convert all of these from inches to meters
def layered_closure(layer_thickness, core_density, layer_density, layers):

    def layered_mass(fins: Fins):
        core_volume = fins.thickness * fins.area
        layer_volume = layer_thickness * layers * fins.area

        return fins.count * (core_volume * core_density + 2 * layer_volume * layer_density)
    
    return layered_mass


def tip_to_tip_closure(layer_thickness, core_density, layer_density, layers, outer_diameter):
    # TODO: add in the mass of layers around the body of the rocket

    base = layered_closure(layer_thickness, core_density, layer_density, layers)

    def tip_to_tip_mass(fins: Fins):
        outer_volume = outer_diameter * np.pi * fins.root * layer_thickness * layers

        return base(fins) + layer_density * outer_volume
    
    return tip_to_tip_mass


# 5 mm thickness
# 58 kg/m^3 for styrofoam core
# 1750–2000 kg/m^3 for carbon fiber
# 7 in for OD
basic_CF_layup = tip_to_tip_closure(layer_thickness=0.6e-3, core_density=58, layer_density=1900, layers=4, outer_diameter=0.17907)


# Extremely sensitive to the thickness of the layers


if __name__ == "__main__":
    fins = Fins()
    fins.mass_function = layered_closure(layer_thickness=0.6e-3, core_density=58, layer_density=2300, layers=4)
    fins.mass_function = tip_to_tip_closure(layer_thickness=0.000254, core_density=58, layer_density=2300, layers=4, outer_diameter=0.17907)
    # fins.mass_function = basic_CF_layup

    print("Fins have a mass of", fins.mass, "kg")