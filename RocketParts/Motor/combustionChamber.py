# ROCKET COMBUSTION CHAMBER
# Simulates the evolution of the pressure within the combustion chamber
# Keeps track of pre-combustion and post-combustion volumes (not yet implemented)
# Is the main reference to the fuel grain, which is located within it.


import numpy as np
import sys
sys.path.append(".")

from presetObject import PresetObject
from RocketParts.Motor.grain import Grain
from Helpers.data import DataType


class CombustionChamber(PresetObject):
    """
    Class for the combustion chamber; contains reference to the fuel grain
    Mostly simulates the evolution of the chamber pressure (incorrectly)
    """

    def __init__(self, **kwargs):
        self.fuel_grain = Grain()

        # The inside of the engine starts off at atmospheric conditions
        self.pressure_data_type = DataType.DEFAULT
        self.pressure = 101300 # Pa
        # Instantly goes to the adiabatic (?) flame temperature
        self.temperature = 273.15 + 23 # Kelvin
        self.p_temperature = self.temperature
        self.mass_flow_out = 0
        # P / RT = rho
        # Actually it turns out there is a wacko condition in the way MW is calculated and it is easiest just to use the density output by CEA; I think it does it with M but it might be with MW
        # Please do not use the value from CEA here, that will ruin the whole point of the calculations. We have to find our own pressure, because we have to find our own mass
        # TODO: I don't know the difference between M and MW. There is a 50% chance this is wrong. Most useful source is on 78 of https://ntrs.nasa.gov/api/citations/19960044559/downloads/19960044559.pdf
        # You know what, I came back around. Our system is only defined by the pressure and the volume. We have given the CEA pressure and temperature, from P=pRT it can find the density
        self.density = 4  # kg/m^3
        self.cstar = 1500 # m/s

        # These values are currently designed around a 30 bar chamber with time increment 0.1, but there is no substitute for time increment 0.02
        self.relative_pressure_increase_limit = 0.5
        self.relative_pressure_decrease_limit = 0.4

        super().overwrite_defaults(**kwargs)

        # Overriden by CEA in motor.py; current is based off of air
        self.ideal_gas_constant = 287

        self.pressurizing = True

    @property
    def volume(self):
        # TODO: add a precombustion and postcombustion chamber
        return np.pi * self.fuel_grain.port_radius ** 2


    def get_change_in_pressure(self, apparent_mass_flow):
        '''
        Returns the rate of pressure change with respect to time. 
        Based off of mass continuity in the combustion chamber.
        You have to input the net effective mass flowing into the chamber
        '''
        
        # Based off of this monster of an equation
        # d(P_c)/d(t) = [m-dot_ox + (rho_f - rho_c)*A_b*a*G_ox^n - P_c*A_t/c*_exp] * R*T_C / V_C
        
        # This equation is assuming that the gas flowing into the combustion chamber is immediately at the adiabatic flame temperature, and it doesn't have any heat transfer with the stuff already in the chamber.
        # To be honest, this only affects the charge-up time, and I am pretty sure the way we ignite is going to play a much larger role
        return apparent_mass_flow * self.ideal_gas_constant * self.temperature / self.volume

    def update_pressure(self, effective_mass_flow, time_increment):
        if self.pressure_data_type == DataType.CONSTANT:
            pass

        elif self.pressure_data_type is DataType.DEFAULT:
            self.p_temperature = self.temperature

            pressure_increase_rate = self.get_change_in_pressure(effective_mass_flow)
            planned_increment = pressure_increase_rate * time_increment
            # I am arbitrarily limiting this to not have pressure swings bigger than five times the current
            # Should allow us to run a shorter time increment
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
                

    def update_combustion(self, ox_mass_flow, nozzle, time_increment):
        # From the grain and the ox mass flow, calculate the mass flow of fuel
        self.fuel_grain.update_regression(ox_mass_flow, time_increment)
        fuel_flow = self.fuel_grain.mass_flow

        # Calculates the O/F ratio based on a given ox mass flow and the fuel we just calculated
        if fuel_flow == 0:
            # Basically the same as infinite, the graph will still look relatively normal
            OF = 100
        else:
            OF = ox_mass_flow / fuel_flow

        # Calculate the mass flow out (requires nozzle throat)
        self.mass_flow_out = self.pressure * nozzle.throat_area / self.cstar
        

        volume_regressed = self.fuel_grain.get_volume_flow() * time_increment

        # Update the pressure in the system. Uses the previously calculated mass flux out
        # mass flow into the chamber
        effective_mass_flow_total = ox_mass_flow + (self.fuel_grain.density - self.density) * volume_regressed - self.mass_flow_out

        # It's hard to say whether it is more accurate to multiply by temperature first or do the addition first.
        # The difference between approaches should tend to zero as the time increment approaches zero
        
        self.update_pressure(effective_mass_flow_total, time_increment)
        


    def set_pressure_constant(self, pressure):
        self.pressure_data_type = DataType.CONSTANT
        self.pressure = pressure