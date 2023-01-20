import matplotlib.pyplot as plt
import numpy as np

from helpers.general import get_radius

from rocketparts.motor.nozzle import Nozzle


#region Mathematical calculationss
def determine_expansion_ratio(combustion_chamber_pressure: float, atmospheric_pressure: float, isentropic_exponent: float):
    """
    Outputs the optimum expansion ratio for a converging-diverging nozzle based on a known atmospheric pressure and a combustion chamber pressure, as well as the isentropic expansion coefficient.
    Isentropic expansion coefficient is often written gamma or k, and is usually determined from a 3rd party software like CEA
    Notice that the units for pressure doesn't matter so long as they line up

    Note that there may be better expansion ratios for a given rocket
    """
    # For some reason this equation is upside down in my notes. I am rolling with it, I turn it over at the end
    # A_t / A_e = [(k+1)/2]^[1/(k-1)] * (P_e/P_c)^(1/k) * sqrt([(k+1)/(k-1)] * [1 - (P_e/P_c)^[(k-1)/k])

    # I felt like the equation was too long so I broke it up a bit
    pressure_ratio = atmospheric_pressure / combustion_chamber_pressure
    isentropic_less = isentropic_exponent - 1
    isentropic_more = isentropic_exponent + 1

    first_coefficient = (isentropic_more / 2) ** (1 / isentropic_less)
    second_coefficient = pressure_ratio ** (1 / isentropic_exponent)

    sqrt_base = isentropic_more / isentropic_less * (1 - pressure_ratio ** (isentropic_less / isentropic_exponent))

    throat_to_exit = first_coefficient * second_coefficient * sqrt_base ** (1/2)

    return 1 / throat_to_exit

def find_equilibrium_throat_area(Cstar, combustion_chamber_pressure, mass_flow):
    # c* = P_c * A_t / m-dot
    return Cstar * mass_flow / combustion_chamber_pressure

def find_equilibrium_throat_diameter(Cstar, combustion_chamber_pressure, mass_flow):
    return 2 * get_radius(find_equilibrium_throat_area(Cstar, combustion_chamber_pressure, mass_flow))

def find_nozzle_length(converging_angle, entrance_diameter, throat_diameter, diverging_angle, exit_diameter, conical_proportion=1):
    """
    Find the length of the nozzle consisting of two purely conical sections
    Converging angle is the radians north of west at the throat
    Diverging angle is the radians north of east at the throat
    """
    entrance_displacement = (entrance_diameter - throat_diameter) / 2
    exit_displacement = (exit_diameter - throat_diameter) / 2

    entrance_distance = entrance_displacement / np.tan(converging_angle)
    exit_distance = exit_displacement / np.tan(diverging_angle)

    return entrance_distance + exit_distance * conical_proportion

#endregion


def print_default_nozzle_coefficent(chamber_pressure=250_000):
    n = Nozzle()
    print(n.get_nozzle_coefficient(chamber_pressure))

def display_isentropic_exponent_importance():
    n = Nozzle()
    n.exit_pressure = 100

    for k in np.linspace(0.8, 1.4, num=6):
        n.isentropic_exponent = k

        inputs = np.linspace(0.01, 2_000_000, num=25) # Pa
        outputs = [n.get_nozzle_coefficient(pressure) for pressure in inputs]

        plt.plot(inputs, outputs, label=str(k))
    plt.legend()
    plt.show()    

def display_pressure_importance():
    """Considers a range of pressures. Assumes an isentropic exponent of 1.3"""

    pressures = np.linspace(20, 50)
    expansion_ratios = []

    for pressure in pressures:
        # Using bar for both and assuming atmospheric to be 1 bar
        expansion_ratios.append(determine_expansion_ratio(pressure, 1, 1.3))

    plt.plot(pressures, expansion_ratios)
    plt.title("Best Expansion Ratio vs Pressure")
    plt.xlabel("Pressure (bar)")
    plt.ylabel("Chamber Expansion Ratio ()")

    plt.show()


if __name__ == "__main__":
    # print_default_nozzle_coefficent()
    # display_isentropic_exponent_importance()

    print(determine_expansion_ratio(25, 0.9, 1.18))

    # display_pressure_importance()

    area = find_equilibrium_throat_area(1619, 25 * 10 ** 5, 2.3)
    print(f"Radius {get_radius(area):.4f} m; {get_radius(area) * 3.28 * 12:.2f} in")

    

    
    