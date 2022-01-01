# ROCKET COMBUSTION CHAMBER
# Simulates the evolution of the pressure within the combustion chamber
# Keeps track of pre-combustion and post-combustion volumes (not yet implemented)
# Is the main reference to the fuel grain, which is located within it.


import numpy as np


from presetObject import PresetObject
from RocketParts.Motor.grain import Grain
from Helpers.data import DataType
from Helpers.general import cylindrical_volume
from RocketParts.Motor.mixingChambers import PrecombustionChamber, PostcombustionChamber


class CombustionChamber(PresetObject):
    """
    Class for the combustion chamber; contains reference to the fuel grain
    Mostly simulates the evolution of the chamber pressure (incorrectly)
    """

    def __init__(self, **kwargs):
        self.fuel_grain = Grain()
        self.precombustion_chamber = PrecombustionChamber()
        self.postcombustion_chamber = PostcombustionChamber()


        # The inside of the engine starts off at atmospheric conditions
        self.pressure_data_type = DataType.DEFAULT
        self.pressure = 101300 # Pa
        # Instantly goes to the adiabatic (?) flame temperature
        self.temperature = 273.15 + 23 # Kelvin
        self.mass_flow_out = 0
        # P / RT = rho
        # Actually it turns out there is a wacko condition in the way MW is calculated and it is easiest just to use the density output by CEA; I think it does it with M but it might be with MW
        # Please do not use the value from CEA here, that will ruin the whole point of the calculations. We have to find our own pressure, because we have to find our own mass
        # TODO: I don't know the difference between M and MW. There is a 50% chance this is wrong. Most useful source is on 78 of https://ntrs.nasa.gov/api/citations/19960044559/downloads/19960044559.pdf
        # You know what, I came back around. Our system is only defined by the pressure and the volume. We have given the CEA pressure and temperature, from P=pRT it can find the density
        self.density = 4  # kg/m^3
        self.cstar = 1500 # m/s

        self.limit_pressure_change = True
        # These values are currently designed around a 30 bar chamber with time increment 0.1, but there is no substitute for time increment 0.02
        self.relative_pressure_increase_limit = 0.5
        self.relative_pressure_decrease_limit = 0.4

        super().overwrite_defaults(**kwargs)

        # Overriden by CEA in motor.py; current is based off of air
        self.ideal_gas_constant = 287

        self.pressurizing = True

    @property
    def volume(self):
        # TODO: move this volume into the grain class
        v = cylindrical_volume(self.fuel_grain.length, self.fuel_grain.port_radius)
        v += self.precombustion_chamber.volume + self.postcombustion_chamber.volume

        return v

    def get_change_in_pressure(self, apparent_mass_flow, efficiency=1):
        '''
        Returns the rate of pressure change with respect to time. 
        Based off of mass continuity in the combustion chamber.
        You have to input the net effective mass flowing into the chamber
        '''
        
        # Based off of this monster of an equation
        # d(P_c)/d(t) = [m-dot_ox + (rho_f - rho_c)*A_b*a*G_ox^n - P_c*A_t/c*_exp] * R*T_C / V_C
        
        # The apparent mass flow already accounts for the effect of the regression of the grain
        # To be honest, assumptions in this equation affect mostly the charge-up time, and I am pretty sure the way we ignite is going to play a much larger role
        # TODO: you should also be able to get pressure change from C*; would be nice to see if it is the same
        return efficiency * apparent_mass_flow * self.ideal_gas_constant * self.temperature / self.volume

    def update_pressure(self, effective_mass_flow, time_increment, efficiency=1):
        if self.pressure_data_type == DataType.CONSTANT:
            pass

        elif self.pressure_data_type is DataType.DEFAULT:
            pressure_increase_rate = self.get_change_in_pressure(effective_mass_flow, efficiency)
            planned_increment = pressure_increase_rate * time_increment
            # I am arbitrarily limiting this to not have pressure swings bigger than five times the current
            # Should allow us to run a shorter time increment
            # It will also make the charge-up time totally incorrect. FIXME: I need a better solution - I can probably just change the time increment by a factor of five after charge up is complete. I also just need a variable tgat turns this off
            if self.limit_pressure_change:
                if planned_increment > 0:
                    if planned_increment > self.pressure * self.relative_pressure_increase_limit:
                        print(f"Arbitrarily limiting the positive pressure change down from {planned_increment} to {self.pressure * self.relative_pressure_increase_limit}")
                        planned_increment = self.pressure * self.relative_pressure_increase_limit
                else:
                    if abs(planned_increment) > self.pressure * self.relative_pressure_decrease_limit:
                        print(f"Arbitrarily limiting the negative pressure change down from {planned_increment} to {-self.pressure * self.relative_pressure_decrease_limit}")
                        planned_increment = - self.pressure * self.relative_pressure_decrease_limit

            self.pressure += planned_increment
            self.pressurizing = planned_increment > 0         

    def update_combustion(self, ox_mass_flow, nozzle, time_increment, efficiency=1):
        # Calculate the mass flow out
        self.mass_flow_out = self.pressure * nozzle.throat_area / self.cstar

        # From the grain and the ox mass flow, calculate the mass flow of fuel
        self.fuel_grain.update_regression(ox_mass_flow, time_increment)
        volume_regression = self.fuel_grain.get_volume_flow()

        # Update the pressure in the system. Uses the previously calculated mass flux out
        effective_mass_flow_total = ox_mass_flow + (self.fuel_grain.density - self.density) * volume_regression - self.mass_flow_out
        
        self.update_pressure(effective_mass_flow_total, time_increment, efficiency)
        


    def set_pressure_constant(self, pressure):
        self.pressure_data_type = DataType.CONSTANT
        self.pressure = pressure