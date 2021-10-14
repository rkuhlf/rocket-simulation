import sys
sys.path.append(".")

from preset_object import PresetObject

# Finds the dynamic O/F stuff
# Keeps track of the change in chamber pressure
# The combustion chamber keeps track of the fuel grain and combustion
# The motor class connects ox tank to the injector to the combustion chamber to the nozzle

def find_characteristic_velocity_from_OF(ratio):
    # This part of the model should be completely empirical
    pass


def find_combustion_chamber_pressure():
    pass


class CombustionChamber(PresetObject):

    def __init__(self, config={}, fuel_grain=None):
        self.fuel_grain = fuel_grain

        # The inside of the engine starts off at atmospheric conditions
        # Starts at this and we change it manually
        self.pressure = 101300 # Pa
        # Instantly goes to the adiabatic (?) flame temperature
        # FIXME: For some reason I am not using this temperature value anywhere. I am 40% sure that I should be. The other 60% thinks that we have the system defined in terms of pressure, and the only thing we need the temperature for is to find the density, which CEA already knows
        self.temperature = 273.15 + 23 # Kelvin
        # P / RT = rho
        # Actually it turns out there is a wacko condition in the way MW is calculated and it is easiest just to use the density output by CEA; I think it does it with M but it might be with MW
        # Please do not use the value from CEA here, that will ruin the whole point of the calculations. We have to find our own pressure, because we have to find our own mass
        # TODO: I don't know the difference between M and MW. There is a 50% chance this is wrong. Most useful source is on 78 of https://ntrs.nasa.gov/api/citations/19960044559/downloads/19960044559.pdf
        # You know what, I came back around. Our system is only defined by the pressure and the volume. We have given the CEA pressure and temperature, from P=pRT it can find the density
        self.density = 4  # kg/m^3
        self.cstar = 1500 # m/s

        super().overwrite_defaults(config)

        #region CALCULATED
        # TODO: actually calculate it based on P = pRT
        self.ideal_gas_constant = 0

        #endregion

    def get_volume(self):
        pass

    def get_change_in_pressure(self, apparent_mass_flow):
        '''
        Returns the rate of pressure change with respect to time. 
        Based off of mass continuity in the combustion chamber.
        You have to input the net effective mass flowing into the chamber
        '''
        # Based off of this monster of an equation
        # I think there is some way to do this without knowing R. Again, I'm not too sure about what is going on with how density is calculated for the combustion chamber; however, I am going to move forward with using molar mass and adiabatic flame temperature as well as density to find the change in pressure
        # d(P_c)/d(t) = [m-dot_ox + (rho_f - rho_c)*A_b*a*G_ox^n - P_c*A_t/c*_exp] * R*T_C / V_C
        # TODO: R is broken right now. I don't know how to calculate; probably just use the M value from CEA
        return apparent_mass_flow * R * self.temperature / self.get_volume()

    def update_combustion(self, ox_mass_flow, nozzle, time_increment):
        # From the grain and the ox mass flow, calculate the mass flow of fuel
        self.fuel_grain.update_regression(ox_mass_flow, time_increment)
        fuel_flow = self.fuel_grain.mass_flow

        # Calculates the O/F ratio based on a given ox mass flow and the fuel we just calculated
        OF = ox_mass_flow / fuel_flow

        # Calculate the mass flow out (requires nozzle throat)
        mass_flow_out = self.pressure * self.nozzle.throat_area / self.cstar

        volume_regressed = self.fuel_grain.get_volume_flow() * time_increment

        # Update the pressure in the system. Uses the previously calculated mass flux out
        # mass flow into the chamber
        effective_mass_flow_total = ox_mass_flow + (self.fuel_grain.density - self.density) * volume_regressed - mass_flow_out

        self.get_change_in_pressure(effective_mass_flow_total)
        
