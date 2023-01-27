
R = 8.314

def ideal_gas_pressure(volume: float, moles: float, temperature: float):
    return moles * R * temperature / volume

def van_der_waals_pressure(volume: float, moles: float, temperature: float, a: float, b: float) -> float:
    """
    Given a volume, a number of moles, and a temperature, use the two Van Der Waals constants (a and b) to calculate the pressure. a and b are dependent on the chemical structure of the gas in the container.

    The equation is (P + a (n/V)^2)(V - bn) = nRT
    Pressure is then nRT / (V - bn) - a * (n/V)^2

    volume: m^3, moles: moles of gas, temperature: in Kelvin
    a: J·m^3/mol^2
    b: m^3/mol

    Returns pressure in Pa
    """
    return moles * R * temperature / (volume - b * moles) - a * (moles / volume) ** 2




