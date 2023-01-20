# TEST THE EFFECT OF VARIOUS FUEL GRAINS REGRESSION FUNCTIONS

# Unfortunately, there are a lot of models for helical skin friction, and I wanted to compare them. That leaves me using a 3rd party instead of coding everything myself
from fluids.friction import friction_factor, helical_turbulent_fd_Prasad, Blasius, friction_factor_curved, friction_laminar
import numpy as np
import matplotlib.pyplot as plt


from rocketparts.motor.grain import bath_correction_for_helical_regression



def display_helical_effects(reynolds_numbers=[10 ** 4], helix_diameters=np.linspace(0.0001, 10, 200), port_diameters=[0.1]):
    # Apparently it can be predicted without knowing the pitch; I am not going to bother with investigation because I do not have time
    # It does look like helix diameter of 75 cm is the best for us (10 cm port); 
    # In general, it looks like the highest friction helixes have diameter about 10 * port diameter
    # The benefit sort of tails off at the end, so 35 cm helix would be good too. This is rough because the ID of the fuel grain has to be 6.5 inches = 17 cm

    # I think that helical is probably not super well researched below a certain level of helix diameter, because it actually predicts a lower skin friction than cylindrical

    Re = 10 ** 4
    # 10 cm is pretty much what we are going to use
    port_diameter = 0.1
    helix_diameter = 0.2


    # The bath correction (Gnielinski skin friction) is very odd, because it says that as the diameter of the helix decreases, the skin friction increases
    # print(bath_correction_for_helical_regression(1, Re, port_diameter, helix_diameter))
    # print(helical_turbulent_fd_Prasad(Re, port_diameter, helix_diameter) / Blasius(Re))

    for Re in reynolds_numbers:
        for port_diameter in port_diameters:
            friction_coefficients = []

            for helix_diameter in helix_diameters:
                friction_coefficients.append(friction_factor_curved(Re, port_diameter, helix_diameter))
            

            plt.plot(helix_diameters, friction_coefficients, label=f"{port_diameter:.2f} and {Re:.1e}")

            if len(port_diameters) == 1 and len(reynolds_numbers) == 1:
                baseline_friction = friction_factor(Re)

                plt.plot([helix_diameters[0], helix_diameters[-1]], [baseline_friction, baseline_friction])

    plt.legend()

    plt.show()


if __name__ == "__main__":
    # display_helical_effects(port_diameters=np.linspace(0.01, 0.5, 10))
    display_helical_effects(reynolds_numbers=np.logspace(1, 10, 10))
    # display_helical_effects()

    pass
