import sys
sys.path.append(".")

from preset_object import PresetObject
from Helpers.general import interpolate
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
            previous_thrust = self.thrust_data[self.thrust_data["time"] <= current_time]

            next_thrust = self.thrust_data[self.thrust_data["time"] >= current_time]

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

class CustomMotor(Motor):
    def __init__(self, config={}, ox_tank=None, injector=None, combustion_chamber=None, nozzle=None, environment=None):
        # Don't really need to do anything from super in init
        self.thrust_multiplier = 1
        self.time_multiplier = 1
        self.finished_thrusting = False

        self.ox_tank = ox_tank
        self.injector = injector
        self.combustion_chamber = combustion_chamber
        self.nozzle = nozzle
        self.environment = environment

        self.data_path = "./Data/Input/CombustionLookup.csv"
        self.data = pd.read_csv(self.data_path)


        super().overwrite_defaults(config)

        self.thrust = 0

        # Look, here is where I really want to have all of the mass calculations done separately
        # TODO: I could have a mass object class that all of the objects in the rocket with mass inherit from, then I have it define a get mass and a get_position function, then it uses its own state to calculate each
        # self.mass = ox_tank.mass + injector.mass + combustion_chamber.mass + nozzle.mass

    def update_values_from_CEA(self, chamber_pressure, OF):
        """
        This is doing a look up for the chamber pressure in Pascals.
        It will always round up
        """
        # I don't really know what to do if we are getting condensed values in the nose cone. I guess we can just use the next one up
        looking_for_pressure = False

        for index, row in self.data.iterrows():
            if looking_for_pressure and chamber_pressure < row["Chamber Pressure [psia]"] * 6894.76: # convert to Pa
                # print("Looking through row", index)
                # We have found the row we want
                # Eventually, I should probably add an output for the nozzle throat temperature over time. We want to be certain that our graphite won't be damaged by the extreme heat
                # Actually we don't even need the velocity at the throat because we can calculate it from the c-star and the internal pressure
                self.nozzle.throat_velocity = row["Throat Velocity [m/s]"]
                self.nozzle.exit_pressure = row["Exit Pressure [psia]"] * 6894.76
                self.nozzle.isentropic_exponent = row["gamma"]
                self.combustion_chamber.density = row["Chamber Density [kg/m^3]"]
                self.combustion_chamber.temperature = row["Chamber Temperature [K]"]
                self.combustion_chamber.cstar = row["C-star"] # m/s
                average_molar_mass = row["Molar Mass [kg/mol]"]
                # TODO: Divide by the M that I will get from parsing CEA
                self.combustion_chamber.ideal_gas_constant = 8.314 / average_molar_mass # 8.314 J/ mol·K / (kg/mol) = J / kgK, which I believe is what we want. Nevertheless, TODO:  I need to make sure the values are reasonable
                break
            elif looking_for_pressure:
                continue

            if OF < row["O/F Ratio"]:
                # To make sure that we always get a number, I am going to always pick the row that has an O/F ratio immediately above the current value
                looking_for_pressure = True



    def simulate_step(self):
        ox_flow = self.injector.get_mass_flow()
        self.ox_tank.update_drain(ox_flow * self.environment.time_increment)
        self.combustion_chamber.update_combustion(ox_flow, self.nozzle, self.environment.time_increment)

        fuel_flow = self.combustion_chamber.fuel_grain.mass_flow

        # I have no idea how I have made it this far without considering the O/F. The ox-fuel ratio should determine the C-star.
        # Actually, I guess all that I need is the chamber temperature and the average molar mass
        OF = ox_flow / fuel_flow
        self.update_values_from_CEA(self.combustion_chamber.pressure, OF)

        nozzle_coefficient = self.nozzle.get_nozzle_coefficient(self.combustion_chamber.pressure, self.environment.get_air_pressure(0))

        # TODO: Account for nozzle loss from the port diameter ratio to the nozzle throat. I still need to read about this some more
        # TODO: I want to reimplement this so that the nozzle is giving mass flow and exit velocity values. I think both ways should work, but that way will be easier to compare, and I am not sure that my nozzle coefficient calculation is correct
        self.thrust = nozzle_coefficient * self.nozzle.throat_area * self.combustion_chamber.pressure




        


# TODO: Figure out the min mass flow rate, if any, for the nozzle to reach mach one at the choke. I don't see how it could instantaneously reach mach speeds
if __name__ == "__main__":
    # some motor tests that should be moved to the actual tests TODO
    # m = CustomMotor()
    # m.exit_mach()
    # print(m.get_thrust())

    # Bare minimum simulation
    import matplotlib.pyplot as plt
    from RocketParts.Motor.oxTank import OxTank
    from RocketParts.Motor.injector import Injector
    from RocketParts.Motor.combustionChamber import CombustionChamber
    from RocketParts.Motor.grain import Grain
    from RocketParts.Motor.nozzle import Nozzle
    from environment import Environment

    ox = OxTank()
    grain = Grain()
    chamber = CombustionChamber(fuel_grain=grain)
    injector = Injector(ox_tank=ox, combustion_chamber=chamber)
    nozzle = Nozzle(fuel_grain=grain)
    env = Environment({
        "time_increment": 0.25
    })

    motor = CustomMotor(ox_tank=ox, injector=injector, combustion_chamber=chamber, nozzle=nozzle, environment=env)

    time = 0
    times = []
    pressures = []
    thrusts = []
    temperatures = []

    while ox.get_pressure() > chamber.pressure and ox.ox_mass > 0:
        motor.simulate_step()
        times.append(time)
        time += env.time_increment

        pressures.append(motor.combustion_chamber.pressure)
        thrusts.append(motor.thrust)
        temperatures.append(motor.combustion_chamber.temperature)
    
    plt.subplot(2, 2, 1)
    plt.plot(times, pressures)

    plt.subplot(2, 2, 2)
    plt.plot(times, thrusts)

    plt.subplot(2, 2, 3)
    plt.plot(times, temperatures)

    plt.show()
    

    
