
import sys
sys.path.append(".")

from preset_object import PresetObject
from Helpers.general import interpolate, binary_solve
import pandas as pd



# You know what, I'm just going to go for a data-oriented design with the whole engine
# Functions for everything. Later, I can have functions for sensitivity analysis
# from preset_object import PresetObject


class Motor(PresetObject):
    def __init__(self, config={}):
        # https://www.thrustcurve.org/motors/Hypertek/1685CCRGL-L550/
        # Mass including the propellant
        self.mass = 3.898
        self.propellant_mass = 1.552
        self.thrust_curve = "thrustCurve"

        self.thrust_multiplier = 1
        self.time_multiplier = 1


        super().overwrite_defaults(config)

        # somehow it thinks there's more thrust mass than there is
        self.thrust_data = pd.read_csv(
            "Data/Input/" + self.thrust_curve + ".csv")


        self.set_thrust_data(self.thrust_data)


        self.finished_thrusting = False


    def set_thrust_data(self, dataframe):
        self.thrust_data = dataframe

        total_thrust = 0  # 3,094.7
        # this is close but not exactly correct (actually it's exactly what the data indicates, but not the experimental value) - I changed the first point of the base data to better match the experimental
        for index, row in self.thrust_data.iterrows():
            if index == 0:
                continue

            p_row = self.thrust_data.iloc[index - 1]
            change_in_time = row["time"] - p_row["time"]
            average_thrust = (row["thrust"] + p_row["thrust"]) / 2
            total_thrust += change_in_time * average_thrust

        self.total_impulse = total_thrust

        self.burn_time = self.thrust_data.iloc[-1]["time"]

        self.mass_per_thrust = self.propellant_mass / total_thrust
        # print(self.mass_per_thrust)




    def get_thrust(self, current_time):
        if self.finished_thrusting:
            return 0

        # The longer we want the burn time, the more we want to shrink the lookup time
        current_time /= self.time_multiplier
        # this isn't very efficient, but there are barely 100 data points so it should be instant
        try:
            previous_thrust = self.thrust_data[self.thrust_data["time"] <=
                                               current_time]

            next_thrust = self.thrust_data[self.thrust_data["time"] >=
                                           current_time]

            previous_thrust = previous_thrust.iloc[-1]
            next_thrust = next_thrust.iloc[0]

            return self.thrust_multiplier * interpolate(
                current_time, previous_thrust["time"],
                next_thrust["time"],
                previous_thrust["thrust"],
                next_thrust["thrust"])
        except IndexError as e:
            self.finished_thrusting = True
            return 0

    def thrust_to_mass(self, thrust, time):
        return thrust * self.mass_per_thrust * time / (self.thrust_multiplier * self.time_multiplier)

    def get_total_impulse(self):
        # This has got to be the most confusing way possible to do this. There is a total impulse that is te total impulse of the data without multipliers
        return self.time_multiplier * self.thrust_multiplier * self.total_impulse

    def get_average_thrust(self):
        return self.get_total_impulse() / self.get_burn_time()

    def get_burn_time(self):
        return self.time_multiplier * self.burn_time

    def scale_thrust(self, multiplier):
        self.thrust_multiplier *= multiplier

    def reset_thrust_scale(self):
        self.thrust_multiplier = 1

    def scale_time(self, multiplier):
        self.time_multiplier *= multiplier

    def reset_time_scale(self):
        self.time_multiplier = 1


# https://www.grc.nasa.gov/www/k-12/rocket/rktthsum.html
# There are three equations of state (plus one for exit temperature that we don't care about)
# From the equation for exit mach, we solve for exit velocity by multiplying by the speed of sound at altitude

# The goal is to solve for thrust given easily determined characteristics of the motor
# The things that are changing is the mass flow rate and the exit velocity, as well as the exit pressure (probably)
class CustomMotor(Motor):
    # Test with https://www.grc.nasa.gov/www/k-12/rocket/ienzl.html
    # At the moment, everything is being calculated as a constant
    # I'm pretty sure it changes, but I haven't quite realized what gives.
    # Obviously it has something to do with the mass flow rate, since at some points there will be more material going through.
    # However, there doesn't appear to be any wiggle room for that in the equation

    def __init__(self, config={}):
        # TODO: Figure out how rocket motors work with gas (particularly hybrid) because I think it might affect these variables
        # pt is the total pressure in the combustion chamber, same for tt
        # I'm not sure these are the only things changing. I mean, there should be someway to simulate the fuel grain
        self.total_pressure = 10
        self.total_temperature = 100

        # Supposedly ratio should be from 1 to 60
        self.chamber_area = 0.1  # m
        self.throat_area = 0.01  # m
        self.exit_area = 0.1  # m

        # I believe that 1.33 is the best value for Nitrous, a common fuel
        # Between 1.3 and 1.6 ish
        self.specific_heat_ratio = 1.4  # often abbreviated gamma in equations
        self.gas_constant = 8.31446261815324  # per mole, probably not correct
        self.specific_heat_exponent = (
            self.specific_heat_ratio + 1) / (2 * (self.specific_heat_ratio - 1))

        super().overwrite_defaults(config)


    def mass_flow_rate(self, mach=1):
        # TODO: add mach adjustment into here
        # I believe this is for the conditions given that mass flow rate is choked at sonic conditions
        # I suspect this is where a CFD would be much more accurate
        # tis is were the problems are

        ans = self.throat_area * self.total_pressure / \
            (self.total_temperature) ** (1 / 2)

        ans *= (self.specific_heat_ratio / self.gas_constant) ** (1 / 2)

        ans *= ((self.specific_heat_ratio + 1) / 2) ** -self.specific_heat_exponent

        return ans




    def exit_mach(self):
        # The algebra is much more complicated
        # The exit mach is zero makes it undefined
        # It usually simplifies down to a polynomial
        # Unfortunately it often has multiple solutions
        # I believe that there should only ever be one solution at less than Mach one, which would be the correct result

        # Based on https://math.stackexchange.com/questions/2165814/how-to-solve-an-equation-with-a-decimal-exponent, I think there is no way to solve the polynomial rearrangement. I suspect that the best path forwards is the brute-force method. I think I'll just go ahead and use some kind of math library, but I am interested in coming up with a way to do this myself. Actually, I think binary search wouldn't be half bad, but it won't converge as quickly as a gradient descent algorithm
        # Have to rearrange equation so that x values are on one side
        # I'm not sure if polynomial form or original form is more efficient

        gamma_fraction = (self.specific_heat_ratio + 1) / 2

        gamma_fraction_extended = gamma_fraction / \
            (self.specific_heat_ratio - 1)


        target = self.exit_area / (self.throat_area * gamma_fraction ** -
                                   gamma_fraction_extended)

        # Just need to make sure it converges on the larger one
        ans = binary_solve(
            lambda
            exit_mach:
            (1 + ((self.specific_heat_ratio - 1) / 2) * exit_mach ** 2) **
            gamma_fraction_extended / exit_mach, target, 1, 10)


        return ans


    def exit_temperature(self):
        ans = 1 / ((1 + (self.specific_heat_ratio - 1) / 2 * self.exit_mach() ** 2))

        return self.total_temperature * ans

    def exit_pressure(self):
        ans = (1 + (self.specific_heat_ratio - 1) / 2 * self.exit_mach() **
               2) ** (self.specific_heat_ratio / (self.specific_heat_ratio - 1))

        return self.total_pressure * ans


    def exit_velocity(self):
        """Assuming flow is choked at the """

        return self.exit_mach() * \
            (self.specific_heat_ratio * self.gas_constant
             * self.exit_temperature()) ** (1 / 2)

    def get_free_stream_pressure(self):
        # A function of pressure, altitude, and mach number
        # just returning a constant atm bc idk
        # I believe this is a quantity that will vary slightly with atmospheric conditions

        # This will get funky because the pressure at the back end of the rocket is sometimes pretty close to negative. However, I already account for a lot of that. I don't know what to do. Is that pressure additional to the aerodynamic forces?

        return 20

    def get_thrust(self):
        # https://www.grc.nasa.gov/WWW/K-12/rocket/rktthsum.html
        # I think that it would be best just to simulate these things in a CFD
        # They should also be relatively easy to figure out from experimental data
        self.update_total_pressure()
        self.update_total_temperature()

        # The amount of momentum being pushed out + the pressure difference
        return self.mass_flow_rate() * self.exit_velocity() + self.exit_area * (
            self.exit_pressure() - self.get_free_stream_pressure())


# TODO: Figure out the min mass flow rate, if any, for the nozzle to reach mach one at the choke. I don't see how it could instantaneously reach mach speeds
if __name__ == "__main__":
    # some motor tests that should be moved to the actual tests TODO
    # m = CustomMotor()
    # m.exit_mach()
    # print(m.get_thrust())

    m = Motor()
    # print(m.get_burn_time())
