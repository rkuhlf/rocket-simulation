from Helpers.variables import *
from Helpers.general import interpolate



# Air speeds


def get_air_speed():
    # this tells us how the rocket is moving through space relative to the surrounding fluids
    return np.zeros((2))


# https://www.digitaldutch.com/
density = 1  # kg/m^3 - this is density of the air, not the rocket
density_data = pd.read_csv("Data/Input/airQuantities.csv")
density_data.drop(columns=["Viscosity", "Temperature", "Pressure"])
altitude_data = np.array(density_data["Altitude"])


# for some reason this is slower but I don't really care because it is better
# I think the function call might be doing it
# Changing it to multiply by direction doesnt make it any faster
def get_next(index, previous_index, direction, altitude):
    # if density_data.iloc[index]["Altitude"] * direction > direction * altitude:
    #     return index, previous_index
    if direction < 0 and altitude_data[index] < altitude:
        return index, previous_index
    elif direction > 0 and altitude_data[index] > altitude:
        return index, previous_index
    else:
        previous_index = index
        index += direction

        return get_next(index, previous_index, direction, altitude)



previous_index = 0

# It turns out lookups from pandas are much slower than from numpy


def get_air_density(altitude):
    global previous_index

    altitude /= 1000  # convert to kilometers

    index = previous_index
    if altitude_data[index] > altitude:
        index, previous_index = get_next(index, previous_index, -1, altitude)
    elif altitude_data[index] < altitude:
        index, previous_index = get_next(index, previous_index, 1, altitude)



    previous_density = density_data.iloc[previous_index]

    next_density = density_data.iloc[index]

    # previous_density = previous_density.iloc[-1]
    # next_density = next_density.iloc[0]

    return interpolate(
        altitude, previous_density["Altitude"],
        next_density["Altitude"],
        previous_density["Density"],
        next_density["Density"])


# find air resistance
def get_drag_force(area, drag_coefficient):
    altitude = base_altitude + position[1]

    air_density = get_air_density(altitude)
    renold = air_density * area * drag_coefficient / 2

    air_resistance = renold * (velocity ** 2)

    # In the same direction, so wen we subtract it the velocity will decrease
    air_resistance *= np.sign(velocity)

    return air_resistance
