

def confirm_range(temperature):
    # Errors if temperature is outside the acceptable range
    if temperature > 273.15 + 36:
        raise ValueError(
            "The model is not accurate beyond nitrous's critical point. You may not be there yet, but it is close enough that everything gets weird")
    if temperature < 273.15 - 90:
        raise ValueError(
            "The model is not accurate below Nitrous's boiling point. I don't know why this would happen (check that your temperature is in Kelvin?)")


# Also important for getting the tank pressure
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
