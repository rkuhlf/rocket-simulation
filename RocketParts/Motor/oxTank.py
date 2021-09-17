import numpy as np
import matplotlib.pyplot as plt

# atm it is mostly DOD, I'm not sure I want it like that, especially when I add it into the frame-by-frame sim


def confirm_range(temperature):
    # Errors if temperature is outside the acceptable range
    if temperature > 273.15 + 36:
        raise ValueError(
            "The model is not accurate beyond nitrous's critical point. You may not be there yet, but it is close enough that everything gets weird")
    if temperature < 273.15 - 90:
        raise ValueError(
            "The model is not accurate below Nitrous's boiling point. I don't know why this would happen (check that your temperature is in Kelvin?)")


def find_nitrous_vapor_pressure(temperature):
    # bar
    confirm_range(temperature)
    return 72.51 * np.e ** (309.57 / temperature *
                            (-6.71893 * (1 - temperature / 309.57) + 1.35966 *
                             (1 - temperature / 309.57) ** (3 / 2) - 1.3779 *
                             (1 - temperature / 309.57) ** (5 / 2) + -4.051 *
                             (1 - temperature / 309.57) ** (5)))


def find_liquid_nitrous_density(temperature):
    # kg/m**3
    confirm_range(temperature)
    return 452 * np.e ** (1.72328 * (1 - (temperature / 309.57)) ** (1 / 3) -
                          0.8395 * (1 - (temperature / 309.57)) ** (2 / 3) +
                          0.5106 * (1 - (temperature / 309.57)) - 0.10412 *
                          (1 - (temperature / 309.57)) ** (4 / 3))


def find_gaseous_nitrous_density(temperature):
    # kg / m**3
    # could definitely have done this with a loop and like one array
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
    # kJ / kg
    coefficients = [-200, 116.043, -917.225, 794.779, -589.587]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** ((i) / 3)

    return total


def find_specific_enthalpy_of_gaseous_nitrous(temperature):
    # kJ / kg
    coefficients = [-200, 440.055, -459.701, 434.081, -485.338]
    total = 0
    for i in range(0, 5):
        total += coefficients[i] * (1 - temperature / 309.57) ** ((i) / 3)

    return total


def find_heat_of_vaporization(temperature):
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


def find_combined_total_heat_capacity(gaseous_mass, liquid_mass,
                                      gaseous_specific_heat,
                                      liquid_specific_heat):
    # kJ / K
    # Notice that we use mass. This is a scientific thing. You do not heat up a volume of something, you heat up a mass of particles.
    return gaseous_mass * gaseous_specific_heat + liquid_mass * liquid_specific_heat


# This is the main one for the overall engine sim
def find_ullage(
        ox_mass, volume, temperature, constant_temperature=True,
        already_gas_mass=0, iterations=3, iters_so_far=0,
        temperature_change_so_far=0):
    # if the temperature is changing, we need to know how much is already in gas phase
    # Because the change in phase is associated with a temperature change, we need to recalculate to adjust the densities. Since this is cyclical, we'll just loop through a couple of times and hope it converges (it should, unless the temperature is so large it causes more phase change than the initial)
    # If the temperature is constant, we will not account for the enthalpy absorbed by nitrous shifting to the gas phase
    liquid_density = find_liquid_nitrous_density(temperature)
    gas_density = find_gaseous_nitrous_density(temperature)

    # volume = gas_volume + liquid_volume
    # mass = gas_mass + liquid_mass
    # gas_mass = mass - liquid_mass

    # volume = gas_mass / gas_density + liquid_mass / liquid_density
    # Substitute; volume = (mass - liquid_mass) / gas_density + liquid_mass / liquid_density
    # Distribute and Undistribute to separate the liquid mass
    # volume = mass / gas_density - liquid_mass / gas_density + liquid_mass / liquid_density
    # volume = mass / gas_density + liquid_mass * (1 / liquid_density - 1 / gas_density)

    # liquid_mass = (volume - mass / gas_density) / (1 / liquid_density - 1 / gas_density)
    liquid_mass = (
        volume - ox_mass / gas_density) / (1 / liquid_density - 1 / gas_density)
    gas_mass = ox_mass - liquid_mass

    ullage = (gas_mass / gas_density) / volume

    if not constant_temperature and iters_so_far < iterations:
        newly_evaporated_gas = gas_mass - already_gas_mass
        print("vap", find_heat_of_vaporization(temperature))
        heat_absorbed = newly_evaporated_gas * \
            find_heat_of_vaporization(temperature)
        print("absorbed", heat_absorbed)
        total_heat_capacity = find_combined_total_heat_capacity(
            gas_mass, liquid_mass,
            find_gaseous_heat_capacity(temperature),
            find_liquid_heat_capacity(temperature))
        temperature_change = -heat_absorbed / total_heat_capacity
        print(temperature_change)

        return find_ullage(
            ox_mass, volume, temperature + temperature_change,
            constant_temperature=False, already_gas_mass=gas_mass,
            iterations=iterations, iters_so_far=iters_so_far + 1,
            temperature_change_so_far=temperature_change_so_far +
            temperature_change)


    if ullage > 1:
        raise Warning(
            "Your ox tank is filled completely with gas. Be sure to use your own calculations for density rather than the saturated model.")
        return 1
    elif ullage < 0:
        raise ValueError(
            "Your ox tank is overfull. I don't know what happens when you put more volume of liquid than can fit into a container, but there are likely going to be some extra stresses here.")

    return [ullage, temperature_change_so_far]


def find_safety_factor(pressure, radius, thickness, failure_strength):
    stress = pressure * radius / thickness
    return failure_strength / stress


def find_minimum_wall_thickness(
        pressure, radius, safety_factor, failure_strength):
    return pressure * radius * safety_factor / failure_strength



def find_nitrous_volume(mass, temperature, ullage=0):
    # This ullage adjustment is an approximation, and not a very good one
    return (mass / find_liquid_nitrous_density(temperature)) / (1 - ullage)

# TODO: Implement the hemispherial end adjustment (should increase required length)


def get_length(volume, radius, hemispherical_ends=False):
    if hemispherical_ends:
        end_volume = 4 / 3 * np.pi * radius ** 3
        volume -= end_volume
        straight_length = volume / (np.pi * radius ** 2)

        # The spheres provide two radiuses of length on either end
        return straight_length + radius * 2
    else:  # cylindrical ends
        return volume / (np.pi * radius ** 2)


if __name__ == '__main__':
    '''
    # print(find_specific_enthalpy_of_gaseous_nitrous(273 - 0))
    ox_mass = 68.5  # kg
    # 3ish cubic feet converted to meters cubed
    volume = 3 / 35.3147
    print(find_ullage(ox_mass, volume, 273, constant_temperature=False))
    print(find_ullage(ox_mass, volume, 273, constant_temperature=True))
    '''

    '''
    # print(find_gaseous_nitrous_density(273.15 + 40))
    ox_mass = 68.5  # kg
    # 3ish cubic feet converted to meters cubed
    volume = 3 / 35.3147
    print(find_ullage(ox_mass, volume, 273))


    volumes = np.linspace(2.8, 10) / 35.3147
    ullages = []
    for v in volumes:
        ullages.append(find_ullage(ox_mass, v, 273))

    plt.plot(volumes, ullages)
    plt.show()

    # Conclusions:
    # It doesn't take that much of a volume increase to give your nitrous way more breathing room
    # That means that decreasing the mass by 5% will give us a more than 5% increase in ullage
    # As you increase the volume though, you get less and less ullage.
    '''


    '''
    meop = 2000  # psi
    radius = 5  # in
    thickness = 0.5  # in
    failure_strength = 40000  # psi

    print(find_safety_factor(meop, radius, thickness, failure_strength))
    print(find_minimum_wall_thickness(meop, radius, 2, failure_strength))

    # Structural stuff
    ox_mass = 68.4  # kg
    temperature = 273.15  # Kelvin

    print(find_nitrous_volume(ox_mass, temperature, ullage=0)
          * 35.3147)  # multiplication converts to ft^3
    print(find_nitrous_volume(ox_mass, temperature, ullage=0.15) * 35.3147)
    # multiplying the radius converts it to meters, multiplying the output converts m to ft
    print(
        get_length(
            find_nitrous_volume(ox_mass, temperature, ullage=0.15),
            radius * 0.0254) * 3.28084)
    '''
