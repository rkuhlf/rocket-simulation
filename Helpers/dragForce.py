from Helpers.variables import *
from Helpers.general import interpolate

# https://www.digitaldutch.com/
density = 1  # kg/m^3 - this is density of the air, not the rocket
density_data = pd.read_csv("Data/Input/airQuantities.csv")


def get_air_density(altitude):
    altitude /= 1000  # convert to kilometers
    previous_density = density_data[density_data["Altitude"] < altitude]

    next_density = density_data[density_data["Altitude"] > altitude]

    previous_density = previous_density.iloc[-1]
    next_density = next_density.iloc[0]

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
