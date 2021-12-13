# TEST THE EFFECT OF VARIOUS FUEL GRAINS REGRESSION FUNCTIONS

# Unfortunately, there are a lot of models for helical skin friction, and I wanted to compare them. That leaves me using a 3rd party instead of coding everything myself
from fluids.friction import helical_turbulent_fd_Prasad, Blasius
import sys
sys.path.append(".")

from RocketParts.Motor.grain import bath_correction_for_helical_regression



def display_helical_effects():
    Re = 10 ** 4
    port_diameter = 0.01
    helix_diameter = 0.2

    # The bath correction (Gnielinski skin friction) is very odd, because it says that as the diameter of the helix decreases, the skin friction increases
    print(bath_correction_for_helical_regression(1, Re, port_diameter, helix_diameter))
    print(helical_turbulent_fd_Prasad(Re, port_diameter, helix_diameter) / Blasius(Re))

if __name__ == "__main__":
    display_helical_effects()


    pass
