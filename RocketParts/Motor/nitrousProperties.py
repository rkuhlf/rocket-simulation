# NITROUS PROPERTIES
# This is a selection of functions to calculate the properties of saturated nitrous at a given temperature
# All equations come from http://edge.rit.edu/edge/P07106/public/Nox.pdf
# Note that equations of state for Nitrous, particularly non-saturated equations of state, are not all equally accurate

import numpy as np

# This is Nitrous's boiling point. Below this, the solution is no longer saturated, and you need to use a different model
minimum_temperature = 273.15 - 90.82 # Kelvin
critical_temperature = 309.57 # Kelvin; about 36 C = 96.8 F

# TODO: change everything to get instead of find


# ! important TODO: this is thhrowing an uncaught error in the motor monte carlo
def confirm_range(temperature):
    # Errors if temperature is outside the acceptable range
    if temperature > critical_temperature:
        raise ValueError(
            "The model is not accurate beyond nitrous's critical point. You may not be there yet, but it is close enough that everything gets weird")
    if temperature < minimum_temperature:
        raise ValueError(
            "The model is not accurate below Nitrous's boiling point. I don't know why this would happen (check that your temperature is in Kelvin?)")

def get_liquid_dynamic_viscosity(temperature: float):
    # Returns the value in N * s / m^2
    confirm_range(temperature)
    
    
    # For some reason this 5.24 is correct, it does not need to be converted to Kelvin or anything
    theta = (critical_temperature - 5.24) / (temperature - 5.24)
    
    # Division by 1000 converts from mN to N
    return 0.0293423 / 1000 * np.exp(1.6089 * (theta - 1) ** (1/3) + 2.0439 * (theta - 1) ** (4/3))


# Also important for getting the tank pressure
def get_nitrous_vapor_pressure(temperature):
    """Returns the vapor pressure for a saturated solution of nitrous in bar"""
    # bar
    confirm_range(temperature)
    return 72.51 * np.e ** (309.57 / temperature *
                            (-6.71893 * (1 - temperature / 309.57) + 1.35966 *
                             (1 - temperature / 309.57) ** (3 / 2) - 1.3779 *
                             (1 - temperature / 309.57) ** (5 / 2) + -4.051 *
                             (1 - temperature / 309.57) ** (5)))


def get_liquid_nitrous_density(temperature):
    # kg / m**3
    confirm_range(temperature)
    return 452 * np.e ** (1.72328 * (1 - (temperature / 309.57)) ** (1 / 3) -
                          0.8395 * (1 - (temperature / 309.57)) ** (2 / 3) +
                          0.5106 * (1 - (temperature / 309.57)) - 0.10412 *
                          (1 - (temperature / 309.57)) ** (4 / 3))


minimum_liquid_density = get_liquid_nitrous_density(critical_temperature)

def get_gaseous_nitrous_density(temperature):
    """Returns vapor density in kg / m^3"""

    confirm_range(temperature)

    b1 = -1.00900
    b2 = -6.28792
    b3 = 7.50332
    b4 = -7.90463
    b5 = 0.629427
    Tr = temperature / 309.57
    pc = 452
    base = 1 / Tr - 1
    exponent = b1 * base ** (1 / 3) + b2 * base ** (
        2 / 3) + b3 * base + b4 * base ** (4 / 3) + b5 * base ** (5 / 3)
    return pc * np.e ** exponent


def find_specific_enthalpy_of_liquid_nitrous(temperature):
    """Returns number of kilojoules in one kilogram of nitrous"""

    coefficients = [-200, 116.043, -917.225, 794.779, -589.587]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** ((i) / 3)

    return total


def find_specific_enthalpy_of_gaseous_nitrous(temperature):
    """Intended for saturated vapor"""
    # kJ / kg
    coefficients = [-200, 440.055, -459.701, 434.081, -485.338]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** ((i) / 3)

    return total


def find_heat_of_vaporization(temperature):
    # kJ / kg
    return find_specific_enthalpy_of_gaseous_nitrous(temperature) - find_specific_enthalpy_of_liquid_nitrous(temperature)


def find_liquid_heat_capacity(temperature):
    # kJ / (kg * K)
    coefficients = [0.023454, 1, -3.80136, 13.0945, -14.5180]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** (i - 1)

    return 2.49973 * total


def find_gaseous_heat_capacity(temperature):
    # kJ / (kg * K)
    coefficients = [0.052187, -0.364923, 1, -1.20233, 0.536141]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** ((i - 2) / 3)

    return 132.632 * total


def calculate_maximum_liquid_expansion(temperature=293.15, max_temperature=None):
    """Expects temperature in Kelvin. Will use the max temperature (the last point before it goes supercritical; about 36 C)"""
    
    min_density = minimum_liquid_density
    if max_temperature is not None:
        min_density = get_liquid_nitrous_density(max_temperature)
        
    current_density = get_liquid_nitrous_density(temperature)

    # The maximum expansion - you want big over small. At a higher temperature, the density will be smaller
    return current_density / min_density





import matplotlib.pyplot as plt

def graph_pressure_by_temperature():
    temperatures = np.linspace(273.15 - 90, 273.15 + 36, num=50)
    pressures = [get_nitrous_vapor_pressure(t) for t in temperatures]
    
    temperatures = [(t - 273.15) * 9/5 + 32 for t in temperatures]
    pressures = [p * 14.5038 for p in pressures]
    
    plt.plot(temperatures, pressures)
    plt.xlabel("Temperature (F)")
    plt.ylabel("Pressure (psi)")
    plt.show()



if __name__ == "__main__":
    graph_pressure_by_temperature()
    # print(get_liquid_dynamic_viscosity(-30 + 273.15))
    
    
    
    # print("Calculating Compressibility Ratios")


    # temperatures = np.linspace(273.15 - 90, 273.15 + 36, num=50)
    # compressibilities = []

    # for t in temperatures:
    #     P = get_nitrous_vapor_pressure(t)* 10**5
    #     rho = get_gaseous_nitrous_density(t)
    #     R = 188.91 # J/ kgK

    #     compressibilities.append(P / (rho * t * R))

    # for i in range(len(temperatures)):
    #     print(temperatures[i], compressibilities[i])

    
    
    pass