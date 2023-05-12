# NITROUS PROPERTIES
# This is a selection of functions to calculate the properties of saturated nitrous at a given temperature
# All equations come from http://edge.rit.edu/edge/P07106/public/Nox.pdf
# Note that equations of state for Nitrous, particularly non-saturated equations of state, are not all equally accurate

import numpy as np

# This is Nitrous's boiling point. Below this, the solution is no longer saturated, and you need to use a different model
minimum_temperature = 273.15 - 90.82 # Kelvin
critical_temperature = 309.57 # Kelvin; about 36 C = 96.8 F

# TODO: change everything to get instead of find


def confirm_range(temperature: float, clamped=False):
    """
    If clamped, instead of throwing an error, it will return whichever extreme the function is still defined for. Useful only as a very rough approximation.
    """
    if isinstance(temperature, complex):
        temperature = temperature.real

    # Errors if temperature is outside the acceptable range
    if temperature > critical_temperature:
        if clamped:
            return critical_temperature - 0.1
            
        raise ValueError(
            f"The model is not accurate beyond nitrous's critical point ({temperature} > {critical_temperature}). You may not be there yet, but it is close enough that everything gets weird")
    if temperature < minimum_temperature:
        if clamped:
            return minimum_temperature + 0.1

        raise ValueError(
            f"The model is not accurate below Nitrous's boiling point ({temperature} < {minimum_temperature}). I don't know why this would happen (check that your temperature is in Kelvin?)")
    
    return temperature

def get_liquid_dynamic_viscosity(temperature: float, clamped=False):
    # Returns the value in N * s / m^2
    temperature = confirm_range(temperature, clamped)
    
    
    # For some reason this 5.24 is correct, it does not need to be converted to Kelvin or anything
    theta = (critical_temperature - 5.24) / (temperature - 5.24)
    
    # Division by 1000 converts from mN to N
    return 0.0293423 / 1000 * np.exp(1.6089 * (theta - 1) ** (1/3) + 2.0439 * (theta - 1) ** (4/3))


# Also important for getting the tank pressure
def get_vapor_pressure(temperature, clamped=False):
    """Returns the vapor pressure for a saturated solution of nitrous in bar"""
    # bar
    temperature = confirm_range(temperature, clamped)
    return 72.51 * np.e ** (309.57 / temperature *
                            (-6.71893 * (1 - temperature / 309.57) + 1.35966 *
                             (1 - temperature / 309.57) ** (3 / 2) - 1.3779 *
                             (1 - temperature / 309.57) ** (5 / 2) + -4.051 *
                             (1 - temperature / 309.57) ** (5)))


def get_liquid_nitrous_density(temperature, clamped=False):
    # kg / m**3
    temperature = confirm_range(temperature, clamped)
    return 452 * np.e ** (1.72328 * (1 - (temperature / 309.57)) ** (1 / 3) -
                          0.8395 * (1 - (temperature / 309.57)) ** (2 / 3) +
                          0.5106 * (1 - (temperature / 309.57)) - 0.10412 *
                          (1 - (temperature / 309.57)) ** (4 / 3))


minimum_liquid_density = get_liquid_nitrous_density(critical_temperature)

def get_gaseous_nitrous_density(temperature, clamped=False):
    """Returns vapor density in kg / m^3"""

    temperature = confirm_range(temperature, clamped)

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


def get_specific_enthalpy_of_liquid_nitrous(temperature, clamped=False, override_range=False):
    """
    Returns number of kilojoules in one kilogram of nitrous.
    This property happens to appear to be relatively accurate all the way to absolute zero, so you are allowed to override it to use the number beyond the range it was generated.
    """
    try:
        temperature = confirm_range(temperature, clamped)
    except ValueError as e:
        if override_range:
            pass
        else:
            raise e

    coefficients = [-200, 116.043, -917.225, 794.779, -589.587]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** ((i) / 3)

    return total


def get_specific_enthalpy_of_gaseous_nitrous(temperature, clamped=False):
    """Intended for saturated vapor"""
    temperature = confirm_range(temperature, clamped)
    # kJ / kg
    coefficients = [-200, 440.055, -459.701, 434.081, -485.338]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** ((i) / 3)

    return total


def get_heat_of_vaporization(temperature, clamped=False):
    # kJ / kg
    return get_specific_enthalpy_of_gaseous_nitrous(temperature, clamped) - get_specific_enthalpy_of_liquid_nitrous(temperature, clamped)


def get_liquid_heat_capacity(temperature, clamped=False):
    # kJ / (kg * K)
    temperature = confirm_range(temperature, clamped)
    coefficients = [0.023454, 1, -3.80136, 13.0945, -14.5180]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** (i - 1)

    return 2.49973 * total


def get_gaseous_heat_capacity(temperature, clamped=False):
    # kJ / (kg * K)
    temperature = confirm_range(temperature, clamped)
    coefficients = [0.052187, -0.364923, 1, -1.20233, 0.536141]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** ((i - 2) / 3)

    return 132.632 * total


def get_maximum_liquid_expansion(temperature=293.15, max_temperature=None):
    """Expects temperature in Kelvin. Will use the max temperature (the last point before it goes supercritical; about 36 C)"""
    
    min_density = minimum_liquid_density
    if max_temperature is not None:
        min_density = get_liquid_nitrous_density(max_temperature)
        
    current_density = get_liquid_nitrous_density(temperature)

    # The maximum expansion - you want big over small. At a higher temperature, the density will be smaller
    return current_density / min_density

def get_enthalpy(temperature, liquid_mass, gas_mass):
    return gas_mass * get_specific_enthalpy_of_gaseous_nitrous(temperature) + liquid_mass * get_specific_enthalpy_of_liquid_nitrous(temperature)



# I'm going to need another function to set the temperature and determine the heat. Can probably just start with liquid at that temperature, then double/binary search it until we get something close.
def calculate_temperature(volume: float, mass: float, heat: float, iters=10):
    """
    The volume represents the volume of the receptacle.
    The mass is the equivalent mass of liquid
    The heat is the equivalent to the enthalpy in the system.

    Note that the range is about 130 K that it could be, so do 130 / 2^iters to figure out your accuracy.
    """

    # Check the boundary points to see if it is even in vapor phase equilibrium.

    # Is the amount of heat so low that the temperature is less than -90 C?
    # We need to find whether the specific enthalpy of liquid is low enough.
    stored_heat = get_specific_enthalpy_of_liquid_nitrous(minimum_temperature) * mass
    if heat <= stored_heat: # There's not even enough heat to do this.
        # We want to use specific heat, since we can just assume that's constant and then just do division, but I wanted to do enthalpy to keep the data source consistent.

        min_possible = 0
        max_possible = minimum_temperature

        for _ in range(iters):
            temperature = (min_possible + max_possible) / 2
            stored_heat = get_specific_enthalpy_of_liquid_nitrous(temperature, override_range=True) * mass
            if stored_heat > heat:
                max_possible = temperature
            else:
                min_possible = temperature
        
        return temperature

    # Gaseous and liquid parameters are interchangeable here. This doesn't always become true, even when it should.
    stored_heat = get_specific_enthalpy_of_gaseous_nitrous(critical_temperature) * mass
    if stored_heat <= heat: # There's more than enough heat to do this.
        heat -= stored_heat
        start_temperature = critical_temperature
        # Assume that it should be 2 kJ/kg/K.
        # This is kinda what carbon dioxide is.
        # It will be good enough for our purposes, where we never hit this region.
        temperature_increase = heat / (2 * mass)

        temperature = start_temperature + temperature_increase

        return temperature

    # Now we know that it's definitely not liquid-only, and it's definitely not supercritical, so it must be in vapor-equilibrium. However, it might be in a vapor equilibrium where it is all gas, and there is no liquid. That's a little bit harder to check, so we'll just put it in the iterative code.

    # Now we just need to iterate (with binary search) temperature values until we find one that satisfies our constraints. The only requirement with binary search is that the enthalpy is increasing with temperature.

    min_possible = minimum_temperature
    max_possible = critical_temperature

    for _ in range(iters):
        # We try a temperature.
        temperature = (min_possible + max_possible) / 2

        gas_density = get_gaseous_nitrous_density(temperature)
        liquid_density = get_liquid_nitrous_density(temperature)
        liquid_mass = (volume - mass / gas_density) / (1 / liquid_density - 1 / gas_density)
        # If the system generated at that temperature has a negative mass of liquid, then we know it's too hot, so we try a lower temperature.
        if liquid_mass < 0:
            max_possible = temperature
            continue

        # If the system generated at that temperature has more heat than we do, we know we need to try a lower temperature.
        stored_heat = get_enthalpy(temperature, liquid_mass, mass - liquid_mass)
        if stored_heat > heat:
            max_possible = temperature
        else:
            min_possible = temperature
    
    return (min_possible + max_possible) / 2






import matplotlib.pyplot as plt

def graph_property(property, xlabel, ylabel, units="F"):
    temperatures = np.linspace(minimum_temperature, critical_temperature, num=50)
    outputs = [property(t) for t in temperatures]
    
    if units == "F":
        temperatures = [(t - 273.15) * 9/5 + 32 for t in temperatures]
    elif units == "K":
        temperatures = [t for t in temperatures]

    outputs = [p for p in outputs]
    
    plt.plot(temperatures, outputs)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

def graph_heat_capacity_by_temperature():
    graph_property(lambda t: get_liquid_heat_capacity(t), xlabel="Temperature (K)", ylabel="Heat Capacity (J/kg)", units="K")

    graph_property(lambda t: get_gaseous_heat_capacity(t), xlabel="Temperature (K)", ylabel="Heat Capacity (J/kg)", units="K")

    plt.show()

def graph_enthalpy_by_temperature():
    graph_property(lambda t: get_specific_enthalpy_of_gaseous_nitrous(t), xlabel="Temperature (K)", ylabel="Enthalpy (J/kg)", units="K")

def graph_pressure_by_temperature():
    graph_property(lambda t: get_vapor_pressure(t) * 14.5038, xlabel="Temperature (F)", ylabel="Pressure (psi)")

def graph_distributions():
    heats = np.linspace(-43000, -10000, num=200)
    temperatures = [calculate_temperature(3.14 * 0.0889 ** 2 * 2.4, 52, h) for h in heats]
        
    plt.plot(heats, temperatures)
    plt.xlabel("Heat")
    plt.ylabel("Temperature")
    plt.show()

if __name__ == "__main__":
    graph_distributions()
    # graph_enthalpy_by_temperature()
    # graph_pressure_by_temperature()
    # graph_heat_capacity_by_temperature()
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