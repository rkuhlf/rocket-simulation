# FIN CLASSES
# Fins are basically just a mass object with a few additional evaluation methods.
# Since all of the drag data on the rocket is determined by a CD lookup, it is not necessary to include a fin object, but I want one anyways just for some fin flutter stuff
# Note that all of the masses on the fins are determined by a density per area

# TODO: finish implementing this class



from Helpers.general import constant
from RocketParts.massObject import MassObject


def trapezoidal_area(fins: "Fins"):
    return (fins.root + fins.tip) / 2 * fins.height


# TODO: write an abstract class with a basic init defined for the Fins

class Fins(MassObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: convert everything to inches
        # CR	=	fin root chord
        self.root = 15
        # CT	=	fin tip chord
        self.tip = 5
        # S	=	fin semispan
        self.height = 5
        
        self.sweep = 10

        self.thickness = 3/8

        # N	=	number of fins
        self.count = 4

        # Arbitrarily set to 2 kg
        self.mass_function = constant(2)
        # Area function for a single fin
        self.area_function = trapezoidal_area

        self.layers = 1

        super().overwrite_defaults(**kwargs)
    
    def area(self):
        return self.area_function(self)

    def mass(self):
        return self.mass_function(self)





# Elliptical fin class





# Convert all of these from inches to meters
def tip_to_tip_closure(layer_thickness, core_density, layer_density, layers):

    def tip_to_tip_mass(fins: Fins):
        core_volume = fins.thickness * fins.area
        layer_volume = layer_thickness * layers * fins.area

        return fins.count * (core_volume * core_density + 2 * layer_volume * layer_density)
    
    return tip_to_tip_mass


# 5 mm thickness
# 58 kg/m^3 for styrofoam core
# 1750–2000 kg/m^3 for carbon fiber
basic_CF_layup = tip_to_tip_closure(layer_thickness=0.5e-3, core_density=58, layer_density=1900, layers=4)




if __name__ == "__main__":
    fins = Fins()

    print("Fins have a mass of", fins.mass, "kg")