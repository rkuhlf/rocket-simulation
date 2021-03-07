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
# I think the function call required by recursion might be doing it
# Changing it to multiply by direction in the inequality doesnt make it any faster
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
    # Assumes the same area and drag coefficient for both sides
    altitude = base_altitude + position[1]

    # one of these values is two dimensional, and I think that is causing a problem
    # It's probably area
    air_density = get_air_density(altitude)
    renold = air_density * area * drag_coefficient / 2

    # FIXME: maybe should be the other way around
    relative_velocity = velocity - get_air_speed()

    magnitude = np.linalg.norm(relative_velocity)
    if np.isclose(magnitude, 0):
        return np.array([0, 0])

    unit_direction = relative_velocity / magnitude


    # You can't square each component of velocity and have it be in the same direction
    # So, multiply by the magnitude of the square, as the formula intends, then by the unit direction
    air_resistance = renold * (magnitude ** 2)


    # In the same direction, so wen we subtract it later the velocity will decrease
    air_resistance *= unit_direction

    # Somehow x is bigger than y when the rocket should be shooting straight up
    return air_resistance


def get_drag_torque(drag_coefficient):
    altitude = base_altitude + position[1]

    air_density = get_air_density(altitude)

    # Might need this later for getting drag_coefficient better
    # renold = air_density * area * drag_coefficient / 2

    # just totally ignore frictional angular drag
    # and use the equation CD * pi * h * density * Angular velocity ^ 2 * radius ^ 4
    # The coefficient of drag is the same as for a regular cylinder moving through the round side


    drag_force = drag_coefficient * np.pi * height * \
        air_density * (angular_velocity ** 2) * radius ** 4

    # In the same direction, so wen we subtract it the velocity will decrease
    drag_torque = drag_force * np.sign(angular_velocity)

    return drag_torque
