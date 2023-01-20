

def get_propellant_mass(total_mass, prop_frac=0.5):
    return total_mass * prop_frac

def get_ox_mass(propellant_mass, OF):
    return propellant_mass * OF / (OF + 1)

def get_fuel_mass(propellant_mass, OF):
    return propellant_mass / (OF + 1)