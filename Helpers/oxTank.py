import numpy as np

# atm it is mostly DOD, I'm not sure I want it like that, especially when I add it into the frame-by-frame sim


def find_safety_factor(pressure, radius, thickness, failure_strength):
    stress = pressure * radius / thickness
    return failure_strength / stress


def find_minimum_wall_thickness(pressure, radius, safety_factor, failure_strength):    
    return pressure * radius * safety_factor / failure_strength


# bar
def find_nitrous_vapor_pressure(temperature):
    return 72.51 * np.e ** (309.57/temperature*(-6.71893*(1-temperature/309.57)+1.35966*(1-temperature/309.57)**(3/2)-1.3779*(1-temperature/309.57)**(5/2)+-4.051*(1-temperature/309.57)**(5)))

# kg/m**3
def find_nitrous_density(temperature):
    return 452 * np.e ** (1.72328 * (1 - (temperature/309.57))**(1/3) - 0.8395 * (1 - (temperature/309.57))**(2/3) + 0.5106 * (1 - (temperature/309.57)) - 0.10412 * (1 - (temperature/309.57))**(4/3))

def find_nitrous_volume(mass, temperature, ullage=0):
    return (mass / find_nitrous_density(temperature)) / (1 - ullage)

# TODO: Implement the hemispherial end adjustment (should increase required length)
def get_length(volume, radius, hemispherical_ends=False):
    if hemispherical_ends:
        pass
    else: # cylindrical ends
        return volume / (np.pi * radius ** 2)


if __name__ == '__main__':
    meop = 2000 # psi
    radius = 5 # in
    thickness = 0.5 # in 
    failure_strength = 40000 # psi
    
    print(find_safety_factor(meop, radius, thickness, failure_strength))
    print(find_minimum_wall_thickness(meop, radius, 2, failure_strength))

    # Structural stuff
    ox_mass = 68.4 # kg
    temperature = 273.15 # Kelvin
    
    print(find_nitrous_volume(ox_mass, temperature, ullage=0) * 35.3147) # multiplication converts to ft^3
    print(find_nitrous_volume(ox_mass, temperature, ullage=0.15) * 35.3147)
    print(get_length(find_nitrous_volume(ox_mass, temperature, ullage=0.15), radius * 0.0254) * 3.28084) # multiplying the radius converts it to meters, multiplying the output converts m to ft
