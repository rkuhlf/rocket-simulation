# NITROUS PROPERTIES
# This is a selection of functions to calculate the properties of saturated nitrous at a given temperature
# All equations come from http://edge.rit.edu/edge/P07106/public/Nox.pdf
# This one might also be helpful: https://pubs.acs.org/doi/10.1021/je050186n
# Note that equations of state for Nitrous, particularly non-saturated equations of state, are not all equally accurate

# For some reason I did everything in kilojoules and kilograms.

from enum import Enum, auto
import math
import numpy as np

# This is Nitrous's boiling point. Below this, the solution is no longer saturated, and you need to use a different model
minimum_temperature = 273.15 - 90.82 # Kelvin
critical_temperature = 309.57 # Kelvin; about 36 C = 96.8 F

class NitrousState(Enum):
    EQUILIBRIUM = auto()
    LIQUID_ONLY = auto()
    GAS_ONLY = auto()
    SUPERCRITICAL = auto()

def confirm_range(temperature: float, clamped=False, override_low=False, override_high=False):
    """
    If clamped, instead of throwing an error, it will return whichever extreme the function is still defined for. Useful only as a very rough approximation.
    """
    if isinstance(temperature, complex):
        temperature = temperature.real

    # Errors if temperature is outside the acceptable range
    if temperature > critical_temperature and not override_high:
        if clamped:
            return critical_temperature - 0.1
            
        raise ValueError(
            f"The model is not accurate beyond nitrous's critical point ({temperature} > {critical_temperature}). You may not be there yet, but it is close enough that everything gets weird")
    if temperature < minimum_temperature and not override_low:
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
    # temperature = confirm_range(temperature, clamped)
    return 72.51 * np.e ** (309.57 / temperature *
                            (-6.71893 * (1 - temperature / 309.57) + 1.35966 *
                             (1 - temperature / 309.57) ** (3 / 2) - 1.3779 *
                             (1 - temperature / 309.57) ** (5 / 2) + -4.051 *
                             (1 - temperature / 309.57) ** (5)))


def get_liquid_nitrous_density(temperature, clamped=False, override_low=False):
    # kg / m**3
    # It looks reasonable even when it's purely liquid. It's basically a straight line of increasing density as it gets colder.
    temperature = confirm_range(temperature, clamped, override_low)

    return 452 * np.e ** (1.72328 * (1 - (temperature / 309.57)) ** (1 / 3) -
                          0.8395 * (1 - (temperature / 309.57)) ** (2 / 3) +
                          0.5106 * (1 - (temperature / 309.57)) - 0.10412 *
                          (1 - (temperature / 309.57)) ** (4 / 3))


minimum_liquid_density = get_liquid_nitrous_density(critical_temperature)

def get_gaseous_nitrous_density(temperature, clamped=False, override_low=False):
    """Returns vapor density in kg / m^3"""

    temperature = confirm_range(temperature, clamped, override_low)

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
    
    try:
        return pc * np.e ** exponent
    except OverflowError:
        return float("inf") 


def get_specific_enthalpy_of_liquid_nitrous(temperature, clamped=False, override_low=False):
    """
    Returns number of kilojoules in one kilogram of nitrous.
    This property happens to appear to be relatively accurate all the way to absolute zero, so you are allowed to override it to use the number beyond the range it was generated.
    """
    temperature = confirm_range(temperature, clamped, override_low)

    coefficients = [-200, 116.043, -917.225, 794.779, -589.587]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** ((i) / 3)

    return total

def get_specific_enthalpy_of_gaseous_nitrous(temperature, clamped=False, override_low=False):
    """Intended for nitrous that is not saturated"""
    temperature = confirm_range(temperature, clamped, override_low)
    coefficients = [-209.559, 61.3277, -52.5969, 249.352, -38.4368]
    total = 0
    for i in range(5):
        total += coefficients[i] * (temperature / critical_temperature) ** (i / 2)

    return total

def get_specific_enthalpy_of_nitrous_vapor(temperature, clamped=False, override_low=False):
    """Intended for saturated vapor. Temperature in Kelvin."""
    temperature = confirm_range(temperature, clamped, override_low)
    # kJ / kg
    coefficients = [-200, 440.055, -459.701, 434.081, -485.338]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** ((i) / 3)

    return total


def get_heat_of_vaporization(temperature, clamped=False):
    # kJ / kg
    return get_specific_enthalpy_of_nitrous_vapor(temperature, clamped) - get_specific_enthalpy_of_liquid_nitrous(temperature, clamped)


def get_liquid_specific_heat(temperature, clamped=False, override_low=False):
    # kJ / (kg * K)
    temperature = confirm_range(temperature, clamped, override_low=override_low)
    coefficients = [0.023454, 1, -3.80136, 13.0945, -14.5180]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** (i - 1)

    return 2.49973 * total


def get_gaseous_specific_heat(temperature, clamped=False, override_low=False):
    # kJ / (kg * K)
    temperature = confirm_range(temperature, clamped, override_low=override_low)
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

def get_enthalpy(temperature, liquid_mass, gas_mass, override_low=False):
    if liquid_mass == 0:
        # We assume it is in the gas only phase.
        return gas_mass * get_specific_enthalpy_of_gaseous_nitrous(temperature, override_low=override_low)

    return gas_mass * get_specific_enthalpy_of_nitrous_vapor(temperature, override_low=override_low) + liquid_mass * get_specific_enthalpy_of_liquid_nitrous(temperature, override_low=override_low)

def get_liquid_mass(volume: float, mass: float, temperature: float, override_low=False) -> float:
    """Expects temperature in Kelvin. Will assume no gaseous mass if the temperature is less than 200 K, where it is pretty much negligable."""
    if temperature < 200:
        return mass
    
    gas_density = get_gaseous_nitrous_density(temperature, override_low=override_low)
    # If all of the gas can evaporate, assume that it does.
    if gas_density * volume > mass:
        return 0
    
    liquid_density = get_liquid_nitrous_density(temperature, override_low=override_low)
    # Occasionally the liquid mass is more than the mass provided. This is the point where it has gone supercritical.
    
    return (volume - mass / gas_density) / (1 / liquid_density - 1 / gas_density)


# Unfortunately, binary search doesn't appear to work here, because the function I have for the enthalpy of gaseous nitrous is not always increasing wrt to temperature. I have no idea how this is possible.
def calculate_temperature(volume: float, mass: float, heat: float, iters=10) -> tuple[float, NitrousState]:
    """
    The volume represents the volume of the receptacle.
    The mass is the equivalent mass of liquid
    The heat is the equivalent to the enthalpy in the system. This is very badly named.

    Note that the range is about 130 K that it could be, so do 130 / 2^iters to figure out your accuracy.

    returns a tuple with the temperature first, then the phase.    
    """
    # We return room temperature if there is nothing in here.
    if mass == 0:
        return 293, NitrousState.GAS_ONLY

    # Check if we have enough energy to go supercritical.
    required_heat = get_specific_enthalpy_of_nitrous_vapor(critical_temperature) * mass
    if required_heat <= heat: # There's more than enough heat to do this.
        # There's more than enough mass (pressure) to do this.
        required_mass = get_gaseous_nitrous_density(critical_temperature, override_low=True) * volume
        if mass >= required_mass:
            # Find the temperature of the supercritical fluid.
            heat -= required_heat
            start_temperature = critical_temperature
            # Assume that it should be 2 kJ/kg/K.
            # This is kinda what carbon dioxide is.
            # It will be good enough for our purposes, where we never hit this region.
            temperature_increase = heat / (2 * mass)

            temperature = start_temperature + temperature_increase

            return temperature, NitrousState.SUPERCRITICAL

    # There's a bit of a discrepancy in this graph where the transition from vapor to gas-only flatlines for a bit. This is because of the discrepancy in enthalpy function between the ideal gas and the gas vapor.

    minimum_temperature = 0
    maximum_temperature = critical_temperature

    for _ in range(iters):
        candidate_temperature = (minimum_temperature + maximum_temperature) / 2
        liquid_mass = get_liquid_mass(volume, mass, candidate_temperature, True)
        gas_mass = mass - liquid_mass
        candidate_enthalpy = get_enthalpy(candidate_temperature, liquid_mass, gas_mass, True)

        # If this system is too hot, we need a cooler temperature.
        if candidate_enthalpy > heat:
            maximum_temperature = candidate_temperature
        else:
            minimum_temperature = candidate_temperature

    phase = NitrousState.EQUILIBRIUM
    if liquid_mass == 0:
        phase = NitrousState.GAS_ONLY
    elif gas_mass == 0:
        phase = NitrousState.LIQUID_ONLY

    return candidate_temperature, phase



def calculate_heat(volume: float, mass: float, temperature: float, iters=20, temp_iters=None):
    """
        This is constructed a little bit akwardly in order to give it better compatibility with calculate_temperature. Basically, it will iteratively try heat inputs until it matches the temperature, that way the model for calculating heat and the model for calculating temperature are guaranteed to be consistent.

        temp_iters defaults to iters/2.
        It will include iters * temp_iters calls.
    """
    
    if mass == 0:
        return 0

    if temp_iters is None:
        temp_iters = iters // 2

    # Find upper bound. Iteratively double until it is bigger. It will almost always be negative, so this should pretty much run once.
    max_possible = 1
    while True:
        stored_temp = calculate_temperature(volume, mass, max_possible)[0]

        # Once the temp is too high, we can stop.
        if stored_temp > temperature:
            break
        
        max_possible *= 2
    
    # If you are basically at absolute zero, which is completely unrealistic, then we need to arbitrarily set the minimum at absolute zero energy, for which our model will not be great.
    if temperature < 1:
        min_possible = get_specific_enthalpy_of_liquid_nitrous(temperature) * mass
    else:
        min_possible = -1024 # Set at an arbitrarily somewhat large value to speed up.
        while True:
            stored_temp = calculate_temperature(volume, mass, min_possible)[0]

            # Once the temp is too low, we can stop.
            if stored_temp < temperature:
                break
            
            min_possible *= 2
    

    for _ in range(iters):
        heat = (min_possible + max_possible) / 2
        stored_temp = calculate_temperature(volume, mass, heat, iters=temp_iters)[0]

        if stored_temp > temperature:
            max_possible = heat
        else:
            min_possible = heat

    return (min_possible + max_possible) / 2


import matplotlib.pyplot as plt

def graph_property(property, xlabel, ylabel, units="F", temperatures=np.linspace(minimum_temperature, critical_temperature, num=50), label=None):
    outputs = [property(t) for t in temperatures]
    
    # Convert everything to K
    if units == "F":
        temperatures = [(t - 273.15) * 9/5 + 32 for t in temperatures]
    elif units == "K":
        temperatures = [t for t in temperatures]

    outputs = [p for p in outputs]
    
    label = f"{label} (K)" if label != None else ""
    plt.plot(temperatures, outputs, label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

def graph_specific_heat_by_temperature():
    graph_property(lambda t: get_liquid_specific_heat(t), xlabel="Temperature (K)", ylabel="Heat Capacity (J/kg)", units="K")

    graph_property(lambda t: get_gaseous_specific_heat(t), xlabel="Temperature (K)", ylabel="Heat Capacity (J/kg)", units="K")

    plt.show()

def graph_enthalpy_by_temperature():
    inputs = np.linspace(0, 300, 80)
    graph_property(lambda t: get_specific_enthalpy_of_liquid_nitrous(t, override_low=True), xlabel="Temperature (K)", ylabel="Enthalpy (J/kg)", units="K", temperatures=inputs, label="Liquid")
    graph_property(lambda t: get_specific_enthalpy_of_nitrous_vapor(t, override_low=True), xlabel="Temperature (K)", ylabel="Enthalpy (J/kg)", units="K", temperatures=inputs, label="Vapor")
    graph_property(lambda t: get_specific_enthalpy_of_gaseous_nitrous(t, override_low=True), xlabel="Temperature (K)", ylabel="Enthalpy (J/kg)", units="K", temperatures=inputs, label="Gas")
    plt.show()

def graph_vapor_pressure_by_temperature():
    graph_property(lambda t: get_vapor_pressure(t), xlabel="Temperature (K)", ylabel="Pressure (bar)", units="K", temperatures=np.linspace(0, 300, 50))
    plt.show()

def graph_pressure_by_temperature():
    graph_property(lambda t: get_vapor_pressure(t) * 14.5038, xlabel="Temperature (F)", ylabel="Pressure (psi)")
    plt.show()

def graph_density_by_temperature():
    inputs = np.linspace(0, 300, 80)
    graph_property(lambda t: get_liquid_nitrous_density(t, override_low=True), xlabel="Temperature (K)", ylabel="Density (kg/m^3)", units="K", temperatures=inputs, label="Liquid")
    graph_property(lambda t: get_gaseous_nitrous_density(t, override_low=True), xlabel="Temperature (K)", ylabel="Density (kg/m^3)", units="K", temperatures=inputs, label="Gas")
    plt.legend()
    plt.show()

def graph_distributions(mass=30):
    # This is just a scaling that shows the full heating curve usually (depending on volume).
    min_heat, max_heat = -400 * mass, 0 * mass

    heats = np.linspace(min_heat, max_heat, num=100)
    outputs = [calculate_temperature(3.14 * 0.0889 ** 2 * 2.4, mass, h, iters=60) for h in heats]
    temperatures = [t for t, p in outputs]
    phases = [p for t, p in outputs]

    color_lookup = {
        NitrousState.EQUILIBRIUM: "g",
        NitrousState.LIQUID_ONLY: "b",
        NitrousState.GAS_ONLY: "r",
        NitrousState.SUPERCRITICAL: "y",
    }
    colors = [color_lookup[p] for p in phases]

        
    plt.scatter(heats, temperatures, color=colors)
    # plt.plot(heats, phases)
    plt.xlabel("Heat (kJ)")
    plt.ylabel("Temperature (K)")
    plt.show()

if __name__ == "__main__":
    # print(get_specific_enthalpy_of_nitrous_vapor(critical_temperature))
    # print(calculate_temperature(3.14 * 0.0889 ** 2 * 2.4, 2, -144.5, iters=10))
    # print(calculate_temperature(3.14 * 0.0889 ** 2 * 2.4, 15, -600, iters=60))
    graph_distributions(45)
    # graph_density_by_temperature()
    # graph_enthalpy_by_temperature()
    # graph_pressure_by_temperature()
    # graph_specific_heat_by_temperature()
    # graph_vapor_pressure_by_temperature()
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